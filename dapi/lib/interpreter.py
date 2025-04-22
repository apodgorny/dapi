# dapi/lib/interpreter.py

from abc      import ABC, abstractmethod
from dapi.lib import Datum


class Interpreter(ABC):
	'''Base class for all interpreters: python, llm, node, or custom.'''

	def __init__(self, dapi):
		self.dapi = dapi

	@abstractmethod
	async def invoke(
		self,
		operator_name : str,
		code          : str,
		input         : Datum,
		output        : Datum,
		meta          : dict | None = None
	) -> Datum:
		'''Execute operator logic and return populated output Datum.'''
		pass
