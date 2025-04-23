import traceback

from dapi.lib             import Datum, Interpreter, DapiException
from dapi.lib.struct      import Struct
from dapi.lib.mini_python import MiniPython


class PythonInterpreter(Interpreter):
	'''
	Executes MiniPython operator code, supporting async external operator calls.
	'''

	def __init__(self, dapi=None):
		self.dapi = dapi

	async def invoke_external_operator(self, name: str, input_dict: dict) -> dict:
		result = await self.dapi.operator_service.invoke(name, input_dict)
		return result['output'] if 'output' in result else result

	async def invoke(
		self,
		operator_name : str,
		code          : str,
		input         : Datum,
		output        : Datum,
		config        : dict = {}
	) -> Datum:
		operators = await self.dapi.operator_service.get_all()
		print([o['name'] for o in operators])
		input_dict = input.to_dict()

		try:
			output_dict = await MiniPython(
				operators,
				self.invoke_external_operator
			).call_main(
				operator_name,
				input_dict
			)
		except Exception as e:
			raise DapiException.consume(e)

		output.from_dict(output_dict)
		return output
