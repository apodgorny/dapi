import ast
from dapi.lib import DapiException, ExecutionContext, String, FullPython, Interpreter


class FullPythonInterpreter(Interpreter):
	'''
	Executes a full Python class operator from the provided code string.
	Assumes the code includes a valid Python class with async invoke().
	'''

	type = 'full'

	async def invoke(self) -> dict:
		try:
			full_python = FullPython(
				operator_name          = self.name,
				operator_class_name    = self.class_name,
				input_dict             = self.input,
				code                   = self.code,
				call_external_operator = self.call,
				execution_context      = self.context,
				globals_dict           = {}
			)

			result = await full_python.invoke()
			return result

		except Exception as e:
			raise DapiException.consume(e)