from __future__ import annotations

import os
import asyncio
from pydantic       import BaseModel
from typing         import Any, Dict
from datetime       import datetime

from dapi.db        import OperatorRecord, TransactionRecord
from dapi.lib       import Datum, DatumSchemaError, DapiService, DapiException
from dapi.schemas   import OperatorSchema
from dapi.lib.module    import Module
from dapi.lib.operator  import Operator


OPERATOR_DIR = os.path.join(
	os.environ.get('PROJECT_PATH'),
	os.environ.get('OPERATOR_DIR', 'operators')
)

@DapiService.wrap_exceptions({DatumSchemaError: (400, 'halt')})
class OperatorService(DapiService):
	'''Service for managing operators: atomic_static, atomic_dynamic, function, plugin.'''

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

	async def type_name_to_schema(self, type_name: str) -> type[BaseModel]:
		schema_dict = await self.dapi.type_service.get(type_name)
		try:
			return Datum(schema_dict['schema']).schema
		except DatumSchemaError as e:
			raise DapiException(
				status_code = 400,
				detail      = str(e),
				severity    = DapiException.HALT
			)

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

	def validate_data(self, datum: Datum, data: dict, label: str = ''):
		try:
			datum.validate(data)
		except Exception as e:
			raise DapiException(
				status_code = 400,
				detail      = f'Invalid {label} data: {str(e)}',
				severity    = DapiException.HALT
			)

	async def validate_interpreter(self, interpreter):
		if not await self.dapi.interpreter_service.has(interpreter):
			raise DapiException(
				status_code = 404,
				detail      = f'Interpreter `{interpreter}` does not exist',
				severity    = DapiException.HALT
			)

	def validate_function(self, schema: OperatorSchema) -> None:
		'''For function operators, just validate they have the correct interpreter.'''
		pass

	def validate_transactions_exist(self, ids: list[str], *, function_name: str = '<unknown>') -> None:
		missing = [tx for tx in ids if not self.dapi.db.get(TransactionRecord, tx)]
		if missing:
			raise DapiException(
				status_code = 404,
				detail      = f'Function `{function_name}` refers to missing transaction(s): {missing}',
				severity    = DapiException.HALT
			)

	############################################################################

	async def create(self, schema: OperatorSchema) -> str:
		if schema.interpreter == 'function':
			self.validate_function(schema)

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

	async def set_transactions(self, name: str, transaction_ids: list[str]) -> None:
		if not (operator := self.dapi.db.query(OperatorRecord).filter_by(name=name).first()):
			raise DapiException(
				status_code = 404,
				detail      = f'Operator `{name}` does not exist',
				severity    = DapiException.HALT
			)

		if operator.interpreter != 'function':
			raise DapiException(
				status_code = 400,
				detail      = f'Operator `{name}` is not a function operator',
				severity    = DapiException.HALT
			)

		self.validate_transactions_exist(transaction_ids, function_name=name)
		operator.transactions = transaction_ids
		self.dapi.db.commit()

	async def invoke(self, name: str, input: dict) -> dict:
		print('[OPERATOR_SERVICE] Invoking', name, input)
		operator  = self.require(name)
		instance  = await self.dapi.instance_service.create(
			operator_name = name,
			input_data    = input
		)
		result = await self.dapi.instance_service.invoke(instance.id)
		print(f'[OPERATOR_SERVICE] Invoked {name}. Result:', result.output)
		return result.output