import ast
from dapi.lib import DapiException, ExecutionContext, String, FullPython, Interpreter, Operator


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

				execution_context      = self.context,
				operator_globals       = self.operator_globals,

				call_external_operator = self.call_external_operator,
				get_operator_class     = self.get_operator_class,
			)

			result = await full_python.invoke()
			return result

		except Exception as e:
			raise DapiException.consume(e)
