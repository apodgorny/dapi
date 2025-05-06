from typing import Callable

from lib.o                 import O
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

		if not (
			hasattr(self.__class__, 'InputType')             and
			isinstance(self.__class__.InputType, type)       and
			issubclass(self.__class__.InputType, O)
		):
			raise TypeError(f'InputType of operator `{self.__class__.__name__}` must be a class subclassing O')

		if not (
			hasattr(self.__class__, 'OutputType')            and
			isinstance(self.__class__.OutputType, type)      and
			issubclass(self.__class__.OutputType, O)
		):
			raise TypeError(f'OutputType of operator `{self.__class__.__name__}` must be a class subclassing O')


	async def invoke(self) -> Datum:
		'''Execute operator and return output Datum.'''
		raise NotImplementedError('Operator must implement invoke method')

	def __repr__(self) -> str:
		return f'<Operator {self.__class__.__name__}>'
