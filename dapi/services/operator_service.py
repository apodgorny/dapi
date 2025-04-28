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
		self.dapi = dapi
		self.i    = ''

		self._last_context     = None
		self._operator_classes = {}  # name → operator class

	async def initialize(self):
		await super().initialize()
		await self._register_plugin_operators()

	############################################################################

	async def _register_plugin_operators(self):
		await self.delete_all()
		classes = Module.load_package_classes(Operator, OPERATOR_DIR)

		print(String.underlined('\nFull python operators:'))
		for name, operator_class in classes.items():
			if not hasattr(operator_class, 'invoke'):
				continue

			if is_reserved(name):
				raise ValueError(f'Can not load operator `{name}` - the name is reserved')

			with open(os.path.join(OPERATOR_DIR, f'{name}.py')) as f:
				code = f.read()

			try:
				print(f'  - {name}')
				schema = OperatorSchema(
					name         = name,
					class_name   = operator_class.__name__,
					interpreter  = 'full',
					input_type   = operator_class.InputType.model_json_schema(),
					output_type  = operator_class.OutputType.model_json_schema(),
					code         = code,
					description  = (operator_class.__doc__ or '').strip() or ''
				)

				await self.create(schema, replace=True)

			except DapiException as e:
				if e.detail.get('severity') == 'beware':
					continue
				raise
			except:
				print('Failed loading:', name)
				raise

		print()

	############################################################################

	def validate_name(self, name: str) -> None:
		if is_reserved(name):
			raise DapiException(
				status_code = 422,
				detail      = f'Can not create operator `{name}` - the name is reserved',
				severity    = DapiException.HALT
			)

	def require(self, name: str) -> OperatorRecord:
		operator = self.dapi.db.get(OperatorRecord, name)
		if not operator:
			raise DapiException(
				status_code = 404,
				detail      = f'Operator `{name}` does not exist',
				severity    = DapiException.HALT
			)
		operator.config = operator.config if operator.config else {}
		return operator

	async def validate_interpreter(self, interpreter):
		if not await self.dapi.interpreter_service.has(interpreter):
			raise DapiException(
				status_code = 404,
				detail      = f'Interpreter `{interpreter}` does not exist',
				severity    = DapiException.HALT
			)

	def get_execution_context(self):
		return self._last_context

	async def get_operator_class(self, name: str):
		operator_class = self._operator_classes.get(name, None)
		if not operator_class:
			operator = self.require(name)

			globals_dict = {}
			exec(operator.code, globals_dict)

			operator_class = globals_dict[class_name]
			self._operator_classes[name] = operator_class

		return operator_class

	############################################################################

	def exists(self, name) -> bool:
		return bool(self.dapi.db.get(OperatorRecord, name))

	async def create(self, schema: OperatorSchema, replace=False) -> bool:
		try:
			self.validate_name(schema.name)
			if self.exists(schema.name) and replace:
				await self.delete(schema.name)

			await self.validate_interpreter(schema.interpreter)
			record = OperatorRecord(**schema.model_dump())
			self.dapi.db.add(record)
			self.dapi.db.commit()
			return schema.name
		except Exception as e:
			pass

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

	async def delete_all(self, which=None) -> None:
		'''Delete all operators from the database.'''
		which = ['mini', 'llm', 'full'] if not isinstance(which, list) else which
		records = (
			self.dapi.db.query(OperatorRecord)
				.filter(OperatorRecord.interpreter.in_(which))
				.all()
		)
		for record in records:
			self.dapi.db.delete(record)
		self.dapi.db.commit()

	async def get_input_dict(self, operator_name: str, args: list[Any], kwargs: dict[str, Any]) -> dict:
		'''
		Builds and validates the input dictionary for an operator call
		from positional args and keyword kwargs.
		'''
		operator        = await self.get(operator_name)
		input_schema    = operator['input_type']
		expected_fields = list(input_schema.get('properties', {}).keys())
		required_fields = input_schema.get('required', [])

		provided = {}

		# 1. Map positional args
		for param, value in zip(expected_fields, args):
			provided[param] = value

		# 2. Fill missing from kwargs
		for param in expected_fields:
			if param not in provided and param in kwargs:
				provided[param] = kwargs[param]

		# 3. Handle 'self'
		if 'self' in expected_fields and 'self' not in provided:
			provided['self'] = None

		# 4. Validate required fields only
		parameters = {}
		for param in expected_fields:
			if param in provided:
				parameters[param] = provided[param]
			elif param in required_fields:
				provided_keys = list(provided.keys())
				provided_keys = ', '.join([f'`{k}`' for k in provided_keys])
				raise ValueError(f'[OperatorService] Operator `{operator_name}` is missing required parameter: `{param}`, keys provided: {provided_keys}')

		return parameters

	async def get_output_dict(self, operator_name: str, output: Any) -> dict:
		'''
		Wraps a raw operator output (single value or tuple) into a validated dict
		according to the operator's OutputType schema.
		'''
		# Retrieve operator metadata
		record          = await self.get(operator_name)
		expected_fields = list(record['output_type'].get('properties', {}).keys())

		if not expected_fields:
			raise ValueError(f'[OperatorService] Operator `{operator_name}` has no output fields defined.')

		if len(expected_fields) == 1:
			# Single field — output must be a single value
			return { expected_fields[0]: output }

		else:
			# Multiple fields — output must be a tuple matching the fields
			if not isinstance(output, tuple):
				raise ValueError(f'[OperatorService] Operator `{operator_name}` expected a tuple output for fields {expected_fields}, got {type(output).__name__} instead.')

			if len(output) != len(expected_fields):
				raise ValueError(f'[OperatorService] Operator `{operator_name}` output tuple length mismatch. Expected {len(expected_fields)}, got {len(output)}.')

			return { field: value for field, value in zip(expected_fields, output) }


	async def unwrap_output(self, operator_name: str, output_dict: dict) -> Any: # TODO: refactor
		'''
		Transforms an output dict into a value or tuple for use inside user code.
		'''
		expected_fields = list(output_dict.keys())

		if not expected_fields:
			return None

		if len(expected_fields) == 1:
			return output_dict[expected_fields[0]]

		return tuple(output_dict[field] for field in expected_fields)

	async def call_external_operator(self, name: str, args: list, kwargs: dict, context: ExecutionContext, de: str = None) -> Any:
		'''
		Handles external operator call by packing input from local variables,
		invoking the operator, and unpacking the output for use.
		'''
		input_dict  = await self.get_input_dict(name, args, kwargs)  # Step 1: Pack input
		output_dict = await self.invoke(name, input_dict, context)   # Step 2: Full invocation
		result      = await self.unwrap_output(name, output_dict)    # Step 3: Unpack output to tuple

		return result

	async def invoke(self, name: str, input: dict, context: ExecutionContext) -> dict:
		if context is None:
			raise ValueError('ExecutionContext must be explicitly provided')
		
		self._last_context = context
		self.i            = context.i

		operator = self.require(name)
		output   = ''

		if operator.interpreter == 'llm':
			operator.config['output_schema'] = operator.output_type

		try:
			context.push(
				name        = name,
				lineno      = 1,
				interpreter = operator.interpreter,
				importance  = 1,
				detail      = str(input)
			)
			if interpreter := self.dapi.interpreter_service.get(operator.interpreter):
				interpreter_instance = interpreter (
					operator_name          = name,
					operator_class_name    = operator.class_name,
					operator_code          = operator.code,
					operator_input         = input,
					execution_context      = context,
					call_external_operator = self.call_external_operator,
					get_operator_class     = self.get_operator_class,
					config                 = operator.config
				)
				result = await interpreter_instance.invoke()
				output = await self.get_output_dict(name, result)  # Pack output (wrap value/tuple into output dict)
				return output

			raise DapiException(
					status_code = 400,
					detail      = f'Unknown interpreter: `{operator.interpreter}`',
					severity    = DapiException.HALT
				)
		finally:
			context.pop(detail=str(output))