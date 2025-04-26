from dapi.lib import Datum, Operator


class main(Operator):
	class InputType(Datum.Pydantic):
		operator : str
		message  : str

	class OutputType(Datum.Pydantic):
		call_result : dict

	async def invoke(self, operator, message):
		result = await call(operator, {'text' : message })
		return result

class Process:
	entry = main
