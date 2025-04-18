from dapi.lib            import Datum, Interpreter
from dapi.lib.struct     import Struct
from dapi.lib.mini_python import MiniPython


class PythonInterpreter(Interpreter):
	'''
	Executes MiniPython operator code synchronously with no external calls.
	'''

	def __init__(self, dapi=None):
		self.dapi = dapi

	async def invoke(
		self,
		operator_name : str,
		code          : str,
		input         : Datum,
		output        : Datum,
		config        : dict = {}
	) -> Datum:
		try:
			raw = MiniPython(
				{operator_name: code}
			).call_operator(operator_name, input.to_dict())
		except Exception as e:
			import traceback
			raise ValueError(f'Runtime error in `{operator_name}`:\n{traceback.format_exc()}') from e

		output.from_dict(raw)
		return output if not output.is_empty() else input
