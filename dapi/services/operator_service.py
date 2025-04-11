from __future__ import annotations

from fastapi   import HTTPException
from pydantic  import BaseModel

from dapi.db   import OperatorTable
from dapi.lib  import Datum
from dapi.schemas import OperatorSchema
# from dapi.services.interpreter_service import InterpreterService


class OperatorService:
	'''Service for managing operators: atomic_static, atomic_dynamic, composite.'''

	def __init__(self, dapi):
		self.dapi = dapi

	############################################################################

	async def _create_invoke_handler(self, operator_schema):
		output_schema = self.type_name_to_schema(operator_schema.output_type)
		
		async def handler(input):
			print(f'Operator {operator_schema.name} is called with input: {input}')
			print(f'Input type: {type(input)}')
			
			# For simple doubling operation demonstration
			if hasattr(input, 'number'):
				print(f'Input has number attribute: {input.number}')
				result = output_schema(number=input.number * 2)
				print(f'Result created: {result}')
				return result
			elif hasattr(input, 'value'):
				print(f'Input has value attribute: {input.value}')
				result = output_schema(value=input.value * 2)
				print(f'Result created: {result}')
				return result
			
			# If nothing else works, just return the input
			print('No matching attributes found, returning input')
			return input
			
		return handler


	def type_name_to_schema(self, type_name: str) -> type[BaseModel]:
		print(type_name, self.dapi.type_service.get(type_name))
		# NumberType {'name': 'NumberType', 'schema': {'title': 'NumberType', 'type': 'object', 'properties': {'number': {'type': 'number'}}, 'required': ['number']}}
		schema_dict = self.dapi.type_service.get(type_name)
		datum = Datum(schema_dict)
		return datum.schema

	def validate_name(self, name: str) -> None:
		if self.dapi.db.get(OperatorTable, name):
			raise HTTPException(status_code=400, detail=f'Operator `{name}` already exists')

	def require(self, name: str) -> OperatorTable:
		record = self.dapi.db.get(OperatorTable, name)
		if not record:
			raise HTTPException(status_code=404, detail=f'Operator `{name}` does not exist')
		return record

	def validate_io(self, schema):
		if not self.dapi.type_service.has(schema.input_type):
			raise HTTPException(status_code=404, detail=f'Type `{schema.input_type}` specified in `{schema.name}.input_type` does not exist')
		if not self.dapi.type_service.has(schema.output_type):
			raise HTTPException(status_code=404, detail=f'Type `{schema.output_type}` specified in `{schema.name}.output_type` does not exist')

	# def validate_interpreter(self, interpreter):
	# 	if not self.dapi.interpreter_service.has(schema.interpreter):
	# 		raise HTTPException(status_code=404, detail=f'Interpreter `{schema.interpreter}` specified in `{schema.name}.interpreter` does not exist')

	############################################################################

	async def create(self, schema: OperatorSchema) -> str:
		self.validate_name(schema.name)
		self.validate_io(schema)
		# self.validate_interpreter(schema.interpreter)

		record = OperatorTable(**schema.model_dump())

		self.dapi.db.add(record)
		self.dapi.db.commit()

		handler = await self._create_invoke_handler(schema)
		
		# print(f"Before define_operator_route for {schema.name}")
		# input_schema = self.type_name_to_schema(schema.input_type)
		# output_schema = self.type_name_to_schema(schema.output_type)
		# print(f"Input schema: {input_schema}")
		# print(f"Output schema: {output_schema}")

		# # Register with define()
		# try:
		# 	self.dapi.define_operator_route(
		# 		name           = schema.name,
		# 		input_schema   = input_schema,
		# 		output_schema  = output_schema,
		# 		description    = schema.description,
		# 		invoke_handler = handler
		# 	)
		# 	print(f"Route registered successfully for {schema.name}")
		# except Exception as e:
		# 	print(f"Error registering route for {schema.name}: {e}")

		return schema.name

	def get(self, name: str) -> dict:
		record = self.require(name)
		return record.to_dict()

	def get_all(self) -> list[dict]:
		return [op.to_dict() for op in self.dapi.db.query(OperatorTable).all()]

	def delete(self, name: str) -> None:
		record = self.require(name)
		self.dapi.db.delete(record)
		self.dapi.db.commit()

	async def invoke(self, name: str, raw_input: dict) -> dict:
		operator     = self.require(name)
		input_datum  = Datum(self.dapi.type_service.get(operator.input_type))
		output_datum = Datum(self.dapi.type_service.get(operator.output_type))
		interpreter  = self.dapi.interpreter_service.require(operator.interpreter)
		code         = operator.code

		input_datum.validate(raw_input)  # TODO: have validate take substring explaining what action was taken that produced error

		output = interpreter.invoke(
			code  = code,
			input = input_datum
		)

		output_datum.validate(result)
		return output_datum.to_dict()
