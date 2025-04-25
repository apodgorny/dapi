from __future__ import annotations

from dapi.lib          import String, DapiService, DapiException
from dapi.interpreters import MiniPythonInterpreter, FullPythonInterpreter, LLMInterpreter


@DapiService.wrap_exceptions()
class InterpreterService(DapiService):
	'''Service for executing code across multiple interpreters.'''

	def __init__(self, dapi):
		super().__init__(dapi)
		self.interpreters = {
			MiniPythonInterpreter.type : MiniPythonInterpreter,
			FullPythonInterpreter.type : FullPythonInterpreter,
			LLMInterpreter.type        : LLMInterpreter
		}

		print(String.underlined('\nInitializing interpreters'))
		for name, cls in self.interpreters.items():
			print('  -', name)

	############################################################################

	def get(self, name: str) -> str:
		return self.interpreters.get(name, None)

	async def has(self, name: str) -> bool:
		"""Check if the interpreter exists."""
		return name in self.interpreters

	async def require(self, name: str):
		"""Ensure the interpreter exists and return it."""
		if not await self.has(name):
			raise DapiException(
				status_code = 404,
				detail      = f'Interpreter `{name}` does not exist',
				severity    = DapiException.HALT
			)
		return self.interpreters[name]
