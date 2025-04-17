from __future__ import annotations

from dapi.lib          import DapiService, DapiException
from dapi.interpreters import PythonInterpreter, LLMInterpreter, PluginInterpreter
from dapi.lib.datum    import Datum


@DapiService.wrap_exceptions()
class InterpreterService(DapiService):
	'''Service for executing code across multiple interpreters.'''

	def __init__(self, dapi):
		self.dapi = dapi
		self.interpreters = {
			'python'   : PythonInterpreter(),
			'llm'      : LLMInterpreter(),
			'plugin'   : PluginInterpreter(),
			'function' : None
		}

	############################################################################

	async def has(self, name: str) -> bool:
		return name in self.interpreters

	async def require(self, name: str):
		if not await self.has(name):
			raise DapiException(status_code=404, detail=f'Interpreter `{name}` does not exist', severity=DapiException.HALT)
		return self.interpreters[name]
