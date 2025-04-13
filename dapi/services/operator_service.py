from __future__ import annotations

from pydantic       import BaseModel

from dapi.db        import OperatorTable
from dapi.lib       import Datum, DatumSchemaError, DapiService, DapiException
from dapi.schemas   import OperatorSchema


@DapiService.wrap_exceptions({DatumSchemaError: (400, 'halt')})
class OperatorService(DapiService):
	'''Service for managing operators: atomic_static, atomic_dynamic, composite.'''

	def __init__(self, dapi):
		self.dapi = dapi

	############################################################################

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
		if self.dapi.db.get(OperatorTable, name):
			raise DapiException(
				status_code = 400,
				detail      = f'Operator `{name}` already exists',
				severity    = DapiException.BEWARE
			)

	def require(self, name: str) -> OperatorTable:
		record = self.dapi.db.get(OperatorTable, name)
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

	############################################################################

	async def create(self, schema: OperatorSchema) -> str:
		self.validate_name(schema.name)
		await self.validate_io(schema)
		await self.validate_interpreter(schema.interpreter)

		record = OperatorTable(**schema.model_dump())

		self.dapi.db.add(record)
		self.dapi.db.commit()
		return schema.name

	async def get(self, name: str) -> dict:
		record = self.require(name)
		return record.to_dict()

	async def get_all(self) -> list[dict]:
		return [op.to_dict() for op in self.dapi.db.query(OperatorTable).all()]

	async def delete(self, name: str) -> None:
		record = self.require(name)
		self.dapi.db.delete(record)
		self.dapi.db.commit()

	async def invoke(self, name: str, input: dict) -> dict:
		operator      = self.require(name)
		input_schema  = await self.dapi.type_service.get(operator.input_type)
		output_schema = await self.dapi.type_service.get(operator.output_type)
		interpreter   = await self.dapi.interpreter_service.require(operator.interpreter)

		input_datum   = Datum(input_schema['schema']).from_dict(input)
		output_datum  = Datum(output_schema['schema'])
		
		try:
			result_datum = await interpreter.invoke(
				operator_name = operator.name,
				code          = operator.code,
				input         = input_datum,
				output        = output_datum
			)
		except Exception as e:
			raise DapiException(
				status_code = 500,
				detail      = f'Error during execution: {str(e)}',
				severity    = DapiException.HALT
			)

		self.validate_data(output_datum, result_datum.to_dict(), label='output')
		return result_datum.to_dict()
