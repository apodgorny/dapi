from __future__ import annotations

import os
import uuid

from dapi.db         import OperatorRecord
from dapi.lib        import String, Datum, DapiService, DapiException, DatumSchemaError, Operator, Module, is_reserved
from dapi.schemas    import OperatorSchema


OPERATOR_DIR = os.path.join(
	os.environ.get('PROJECT_PATH'),
	os.environ.get('OPERATOR_DIR', 'operators')
)


@DapiService.wrap_exceptions()
class OperatorService(DapiService):
	'''Service for managing operators.'''

	def __init__(self, dapi):
		print('Initializing service')
		self.dapi                      = dapi
		self.plugin_operator_functions = {}

	async def initialize(self):
		await super().initialize()
		await self.register_plugin_operators()

	############################################################################

	async def register_plugin_operators(self):
		classes   = Module.load_package_classes(Operator, OPERATOR_DIR)

		print(String.underlined('\nLoading operators:'))
		for name, cls in classes.items():
			if not hasattr(cls, 'invoke'):  # TODO: Do full validation here next
				continue

			if is_reserved(name):
				raise ValueError(f'Can not load operator `{name}` - the name is reserved')
			try:
				print('  -', name)
				schema = OperatorSchema(
					name         = name,
					interpreter  = 'plugin',
					input_type   = cls.InputType.model_json_schema(),
					output_type  = cls.OutputType.model_json_schema(),
					code         = '',
					description  = (cls.__doc__ or '').strip() or ''
				)
				
				# Create function to inject into plugin operator's scope
				# to be able to do cool things like 'await call('foobar', data)'
				# right in the code of operators
				# Create function to inject into plugin operator's scope
				async def fn(input_data, cls=cls):
					return await cls.invoke(input_data, { 'invoke': self.invoke })

				self.plugin_operator_functions[name.lower()] = fn

				# Insert record in db, so that api was able to see it
				await self.create(schema)
				
			except DapiException as e:
				if e.detail.get('severity') == 'beware':
					continue
				raise
			except:
				print('Failed loading:', name)
				raise

	async def get_input_datum(self, name: str) -> Datum:
		operator = self.dapi.db.get(OperatorRecord, name)
		return Datum(operator.input_type)

	async def get_output_datum(self, name: str) -> Datum:
		operator = self.dapi.db.get(OperatorRecord, name)
		return Datum(operator.output_type)

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
		# await self.validate_io(schema)
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
		
	async def get_operator_sources(self) -> list[str]:
		"""Get a list of all operator names/sources."""
		operators = await self.get_all()
		return [op['name'] for op in operators]

	async def delete(self, name: str) -> None:
		record = self.require(name)
		self.dapi.db.delete(record)
		self.dapi.db.commit()

	async def truncate(self) -> None:
		'''Delete all python operators from the database.'''
		records = (
			self.dapi.db.query(OperatorRecord)
				.filter(OperatorRecord.interpreter.in_(['python', 'llm']))
				.all()
		)
		for record in records:
			self.dapi.db.delete(record)
		self.dapi.db.commit()

	async def invoke(self, name: str, input: dict) -> dict:
		# print('[OPERATOR_SERVICE] Invoking', name, 'with input', type(input), input)
		operator  = self.require(name)
		# async def create(self, operator_name: str, instance_name: str = None, input_data: dict = {}) -> OperatorInstanceSchema:
		instance  = await self.dapi.instance_service.create(
			operator_name = name,
			input_data    = input
		)
		result = await self.dapi.instance_service.invoke(instance.id)
		# print(f'[OPERATOR_SERVICE] Invoked {name} with result {result}')
		return result.output
