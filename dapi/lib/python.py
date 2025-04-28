
import ast, os
from typing import Callable, Optional, Awaitable, Any
from .execution_context import ExecutionContext


class Python:
	def __init__(
		self,
		operator_name          : str,
		operator_class_name    : str,
		input_dict             : dict,
		code                   : str,
		execution_context      : Optional[ExecutionContext],
		operator_globals       : dict, 
		call_external_operator : Callable[[str, dict, ExecutionContext], Awaitable[Any]],
		get_operator_class     : Callable[[str], type]
	):
		self.operator_name          = operator_name
		self.operator_class_name    = operator_class_name
		self.input                  = input_dict
		self.code                   = code
		self.call_external_operator = call_external_operator
		self.get_operator_class     = get_operator_class
		self.execution_context      = execution_context
		self.globals                = { ** operator_globals }
		self.i                      = execution_context.i

		self._initialize()

	def _initialize(self):
		pass
