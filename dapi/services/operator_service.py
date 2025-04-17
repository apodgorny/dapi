from __future__ import annotations

from pydantic       import BaseModel
from typing         import Any, Dict
from datetime       import datetime

from dapi.db        import OperatorRecord
from dapi.lib       import Datum, DatumSchemaError, DapiService, DapiException
from dapi.schemas   import OperatorSchema


@DapiService.wrap_exceptions({DatumSchemaError: (400, 'halt')})
class OperatorService(DapiService):
	'''Service for managing operators: atomic_static, atomic_dynamic, function.'''

	def __init__(self, dapi):
		self.dapi = dapi

	############################################################################

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
		'''Ensure function operator contains valid meta.definition block.'''
		name = schema.name
		definition = (schema.meta or {}).get('definition')
		txs = definition.get('transactions')
		if not definition:
			raise DapiException(
				status_code = 400,
				detail      = f'Function `{name}` must include `meta.definition`',
				severity    = DapiException.HALT
			)
		if not isinstance(txs, list) or not all(isinstance(tx, str) for tx in txs):
			raise DapiException(
				status_code = 400,
				detail      = f'Function `{name}` has invalid `meta.definition.transactions`: must be a list of strings',
				severity    = DapiException.HALT
			)

		self.validate_transactions_exist(txs, function_name=schema.name)

	def validate_transactions_exist(self, ids: list[str], *, function_name: str = '<unknown>') -> None:
		'''Ensure all referenced transaction IDs exist.'''
		missing = [tx for tx in ids if not self.dapi.db.get('transactions', tx)]
		if missing:
			raise DapiException(
				status_code = 404,
				detail = f'Function `{function_name}` refers to missing transaction(s): {missing}',
				severity    = DapiException.HALT
			)

    # Methods exposed to controller
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

	async def invoke(self, name: str, input: dict) -> dict:
		'''Invoke an operator by creating and executing an instance.'''

		operator  = self.require(name)

		instance = await self.dapi.instance_service.create(
			operator_name = name,
			input_data    = input
		)

		result = await self.dapi.instance_service.invoke(instance.id)
		return result.output
  