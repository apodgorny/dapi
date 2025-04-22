from __future__ import annotations

from dapi.lib          import String, DapiService, DapiException
from dapi.interpreters import PythonInterpreter, LLMInterpreter, PluginInterpreter


@DapiService.wrap_exceptions()
class InterpreterService(DapiService):
	'''Service for executing code across multiple interpreters.'''

	def __init__(self, dapi):
		self.dapi = dapi
		self.interpreters = {
			'python'   : PythonInterpreter,
			'llm'      : LLMInterpreter,
			'plugin'   : PluginInterpreter
		}

		print(String.underlined('\nInitializing interpreters'))
		for name, cls in self.interpreters.items():
			self.interpreters[name] = cls(dapi)
			print('  -', name)

	############################################################################

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
