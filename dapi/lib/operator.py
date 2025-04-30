from typing import Callable

from dapi.lib.datum             import Datum
from dapi.lib.string            import String
from dapi.lib.autoargs          import autodecorate
from dapi.lib.execution_context import ExecutionContext


class Operator:
	'''Base interface for any executable operator: static, dynamic, composite.'''

	@property
	def input_type(self):
		return self.__class__.InputType

	@property
	def output_type(self):
		return self.__class__.OutputType

	@property
	def name(self):
		return String.camel_to_snake(self.__class__.__name__)

	@classmethod
	def input_fields(cls) -> list[str]:
		return list(cls.InputType.model_fields.keys())

	@classmethod
	def output_fields(cls) -> list[str]:
		return list(cls.OutputType.model_fields.keys())

	def __init__(self, globals):
		self.globals = globals

	async def invoke(self) -> Datum:
		'''Execute operator and return output Datum.'''
		raise NotImplementedError('Operator must implement invoke method')

	# For agents only
	async def ask(self, *args, **kwargs):
		if not hasattr(self, 'prompt'):
			raise ValueError('Method call self.ask is only allowed for agent operators (self.prompt must be defined)')

		# ask({ ... })
		if len(args) == 1 and isinstance(args[0], dict) and not kwargs:
			input = args[0]
		else:
			input = kwargs

		return await self.globals['ask'](
			input           = input,
			prompt          = self.prompt,
			response_schema = self.output_type
		)

	def __repr__(self) -> str:
		return f'<Operator {self.__class__.__name__}>'
