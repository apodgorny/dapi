from typing import Callable

from lib.datum             import Datum
from lib.string            import String
from lib.autoargs          import autodecorate
from lib.execution_context import ExecutionContext


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

	def __repr__(self) -> str:
		return f'<Operator {self.__class__.__name__}>'
