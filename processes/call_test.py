from dapi.lib import Datum, Operator


class main(Operator):
	class InputType(Datum.Pydantic):
		operator : str
		message  : str

	class OutputType(Datum.Pydantic):
		call_result : dict

	async def invoke(input):
		call_params = {
			'name': input['operator'],
			'data': {
				'text': input['message']
			}
		}
		result = await call(call_params)
		return { 'call_result': result if result else {'result': 'Called operator'} }

class Process:
	entry = main
