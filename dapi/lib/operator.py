from typing import Callable

from dapi.lib.datum             import Datum
from dapi.lib.autoargs          import autodecorate
from dapi.lib.execution_context import ExecutionContext


class Operator:
	'''Base interface for any executable operator: static, dynamic, composite.'''

	def __init__(self, call_external_operator=None, real_print=None):
		self.call_external_operator = call_external_operator
		self.print = real_print

	async def invoke(self) -> Datum:
		'''Execute operator and return output Datum.'''
		pass

	def __repr__(self) -> str:
		return f'<Operator {self.__class__.__name__}>'
