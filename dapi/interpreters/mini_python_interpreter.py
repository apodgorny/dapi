from dapi.lib import MiniPython, DapiException, Interpreter
from dapi.lib import String


class MiniPythonInterpreter(Interpreter):
	'''
	Executes MiniPython code passed as a string. Assumes code is valid and defines a root function.
	All operator calls are routed through the external callback.
	'''

	type = 'mini'

	async def invoke(self) -> dict:
		try:
			mini_python = MiniPython(
				operator_name          = self.name,
				operator_class_name    = self.class_name,
				input_dict             = self.input,
				code                   = self.code,
				call_external_operator = self.call,
				execution_context      = self.context,
				globals_dict           = {}
			)

			result = await mini_python.invoke()
			return result

		except Exception as e:
			raise DapiException.consume(e)