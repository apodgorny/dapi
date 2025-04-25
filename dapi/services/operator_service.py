from __future__ import annotations

import os
import uuid
import inspect

from dapi.db         import OperatorRecord
from dapi.schemas    import OperatorSchema
from dapi.lib        import (
	String,
	Datum,
	DapiService,
	DapiException,
	DatumSchemaError,
	ExecutionContext,
	Operator,
	Module,
	is_reserved
)
from dapi.interpreters import (
	LLMInterpreter,
	MiniPythonInterpreter,
	FullPythonInterpreter
)


OPERATOR_DIR = os.path.join(
	os.environ.get('PROJECT_PATH'),
	os.environ.get('OPERATOR_DIR', 'operators')
)


@DapiService.wrap_exceptions()
class OperatorService(DapiService):
	'''Service for managing operators.'''

	def __init__(self, dapi):
		print('Initializing service')
		self.dapi         = dapi
		self.last_context = None

	async def initialize(self):
		await super().initialize()
		await self.register_plugin_operators()

	############################################################################

	async def register_plugin_operators(self):
		classes = Module.load_package_classes(Operator, OPERATOR_DIR)

		print(String.underlined('\nLoading operators:'))
		for name, operator_class in classes.items():
			if not hasattr(operator_class, 'invoke'):
				continue

			if is_reserved(name):
				raise ValueError(f'Can not load operator `{name}` - the name is reserved')

			try:
				print('  -', name)
				# code = inspect.getsource(operator_class)
				schema = OperatorSchema(
					name         = name,
					class_name   = operator_class.__name__,
					interpreter  = 'full',
					input_type   = operator_class.InputType.model_json_schema(),
					output_type  = operator_class.OutputType.model_json_schema(),
					code         = '',
					description  = (operator_class.__doc__ or '').strip() or ''
				)
				await self.create(schema)

			except DapiException as e:
				if e.detail.get('severity') == 'beware':
					continue
				raise
			except:
				print('Failed loading:', name)
				raise

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

	async def validate_interpreter(self, interpreter):
		if not await self.dapi.interpreter_service.has(interpreter):
			raise DapiException(
				status_code = 404,
				detail      = f'Interpreter `{interpreter}` does not exist',
				severity    = DapiException.HALT
			)

	def get_execution_context(self):
		return self.last_context

	############################################################################

	async def create(self, schema: OperatorSchema) -> str:
		try:
			self.validate_name(schema.name)
			await self.validate_interpreter(schema.interpreter)
			record = OperatorRecord(**schema.model_dump())
			self.dapi.db.add(record)
			self.dapi.db.commit()
			return schema.name
		except Exception as e:
			print(e)

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
				.filter(OperatorRecord.interpreter.in_(['mini', 'llm']))
				.all()
		)
		for record in records:
			self.dapi.db.delete(record)
		self.dapi.db.commit()

	async def call_external_operator(self, name: str, input: dict, context: ExecutionContext) -> dict:
		return await self.invoke(name, input, context)

	async def invoke(self, name: str, input: dict, context: ExecutionContext) -> dict:
		if context is None:
			raise ValueError('ExecutionContext must be explicitly provided')
		
		self.last_context = context
		operator = self.require(name)

		if interpreter := self.dapi.interpreter_service.get(operator.interpreter):
			interpreter_instance = interpreter (
				operator_name       = name,
				operator_class_name = operator.class_name,
				operator_code       = operator.code,
				operator_input      = input,
				execution_context   = context,
				external_callback   = self.call_external_operator,
				config              = operator.config or {}
			)
			return await interpreter_instance.invoke()

		raise DapiException(
				status_code = 400,
				detail      = f'Unknown interpreter: `{operator.interpreter}`',
				severity    = DapiException.HALT
			)


