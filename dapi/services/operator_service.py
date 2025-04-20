from __future__ import annotations

import os
import uuid

from dapi.db         import OperatorRecord
from dapi.lib        import Datum, DapiService, DapiException, DatumSchemaError
from dapi.schemas    import OperatorSchema
from dapi.lib.module import Module


OPERATOR_DIR = os.path.join(
	os.environ.get('PROJECT_PATH'),
	os.environ.get('OPERATOR_DIR', 'operators')
)


@DapiService.wrap_exceptions({DatumSchemaError: (400, 'halt')})
class OperatorService(DapiService):
	'''Service for managing operators.'''

	def __init__(self, dapi):
		self.dapi = dapi

	############################################################################

	async def register_plugin_operators(self):
		classes = Module.load_package_classes(Operator, OPERATOR_DIR)

		for name, cls in classes.items():
			input_type  = getattr(cls, 'input_type', None)
			output_type = getattr(cls, 'output_type', None)

			if not input_type or not output_type:
				continue

			schema = OperatorSchema(
				name         = name,
				interpreter  = 'plugin',
				input_type   = input_type,
				output_type  = output_type,
				code         = '',
				meta         = None,
				description  = (cls.__doc__ or '').strip() or None
			)

			try:
				await self.create(schema)
			except DapiException as e:
				if e.detail.get('severity') == 'beware':
					continue
				raise

	async def get_input_datum(self, name: str) -> Datum:
		operator = self.dapi.db.get(OperatorRecord, name)
		type_record = await self.dapi.type_service.get(operator.input_type)
		return Datum(type_record['schema'])

	async def get_output_datum(self, name: str) -> Datum:
		operator = self.dapi.db.get(OperatorRecord, name)
		type_record = await self.dapi.type_service.get(operator.output_type)
		return Datum(type_record['schema'])

	############################################################################

	def validate_name(self, name: str) -> None:
		if self.dapi.db.get(OperatorRecord, name):
			raise DapiException(
				status_code = 400,
				detail      = f'Operator `{name}` already exists',
				severity    = DapiException.BEWARE
			)

	def require(self, name: str) -> OperatorRecord:
		record = self.dapi.db.get(OperatorRecord, name)
		if not record:
			raise DapiException(
				status_code = 404,
				detail      = f'Operator `{name}` does not exist',
				severity    = DapiException.HALT
			)
		return record

	async def validate_io(self, schema):
		for direction in ('input_type', 'output_type'):
			type_name = getattr(schema, direction)
			if not await self.dapi.type_service.has(type_name):
				raise DapiException(
					status_code = 404,
					detail      = f'Type `{type_name}` specified in `{schema.name}.{direction}` does not exist',
					severity    = DapiException.HALT
				)

	async def validate_interpreter(self, interpreter):
		if not await self.dapi.interpreter_service.has(interpreter):
			raise DapiException(
				status_code = 404,
				detail      = f'Interpreter `{interpreter}` does not exist',
				severity    = DapiException.HALT
			)

	############################################################################

	async def create(self, schema: OperatorSchema) -> str:
		self.validate_name(schema.name)
		await self.validate_io(schema)
		await self.validate_interpreter(schema.interpreter)

		record = OperatorRecord(**schema.model_dump())

		self.dapi.db.add(record)
		self.dapi.db.commit()
		return schema.name

	async def get(self, name: str) -> dict:
		record = self.require(name)
		return record.to_dict()

	async def get_all(self) -> list[dict]:
		return [op.to_dict() for op in self.dapi.db.query(OperatorRecord).all()]

	async def delete(self, name: str) -> None:
		record = self.require(name)
		self.dapi.db.delete(record)
		self.dapi.db.commit()

	async def invoke(self, name: str, input: dict) -> dict:
		# print('[OPERATOR_SERVICE] Invoking', name)
		operator  = self.require(name)
		instance  = await self.dapi.instance_service.create(
			operator_name = name,
			input_data    = input
		)
		result = await self.dapi.instance_service.invoke(instance.id)
		# print(f'[OPERATOR_SERVICE] Invoked {name}')
		return result.output
