from abc              import ABC, abstractmethod
from typing           import Callable, Awaitable, Optional, Any

from dapi.lib.execution_context import ExecutionContext


class Interpreter(ABC):
	'''Base class for all interpreters (mini, full, llm).'''

	def __init__(
		self,
		operator_name       : str,
		operator_class_name : str,
		operator_code       : str,
		operator_input      : dict,
		execution_context   : ExecutionContext,
		external_callback   : Callable[[str, dict, ExecutionContext, str], Awaitable[Any]],
		config              : Optional[dict] = None
	):
		self.name       = operator_name
		self.class_name = operator_class_name
		self.code       = operator_code
		self.input      = operator_input
		self.context    = execution_context
		self.call       = external_callback
		self.config     = config or {}

	############################################################################

	@abstractmethod
	async def invoke(self) -> dict:
		'''Run the interpreter and return the result. Must be implemented by subclasses.'''
		pass
