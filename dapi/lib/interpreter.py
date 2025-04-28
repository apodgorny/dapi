from abc              import ABC, abstractmethod
from typing           import Callable, Awaitable, Optional, Any

from dapi.lib.execution_context import ExecutionContext


class Interpreter(ABC):
	'''Base class for all interpreters (mini, full, llm).'''

	def __init__(
		self,
		operator_name          : str,
		operator_class_name    : str,
		operator_code          : str,
		operator_input         : dict,
		execution_context      : ExecutionContext,
		operator_globals       : dict,
		call_external_operator : Callable[[str, dict, ExecutionContext, str], Awaitable[Any]],
		get_operator_class     : Callable[[str], type],
		config                 : Optional[dict] = None
	):
		self.name                   = operator_name
		self.class_name             = operator_class_name
		self.code                   = operator_code
		self.input                  = operator_input
		self.context                = execution_context
		self.operator_globals       = operator_globals
		self.call_external_operator = call_external_operator
		self.get_operator_class     = get_operator_class
		self.config                 = config or {}

	############################################################################

	@abstractmethod
	async def invoke(self) -> dict:
		'''Run the interpreter and return the result. Must be implemented by subclasses.'''
		pass
