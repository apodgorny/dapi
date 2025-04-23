from dapi.lib import Datum, Operator
from typing   import Any


################################################################

class BrancherFriend(Operator):
	'''Splits input into a list of sub-items.'''

	class InputType(Datum.Pydantic):
		s: str

	class OutputType(Datum.Pydantic):
		items: list[str]

	async def invoke(self, input):
		s = input['s']
		return {
			'items': [
				{ 's': s + 'a' },
				{ 's': s + 'b' },
				{ 's': s + 'c' }
			]
		}


################################################################

class main(Operator):
	'''Entry point that launches recursive process.'''

	class InputType(Datum.Pydantic):
		s: str

	class OutputType(Datum.Pydantic):
		result: dict[str, Any]

	async def invoke(self, input):
		result = await brancher({
			'operator' : 'brancher_friend',
			'item'     : input['s']
		})
		return { 'result' : result }


################################################################

class Process:
	entry = main
