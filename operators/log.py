from pydantic      import BaseModel

from lib.operator  import Operator


class Log(Operator):
	'''Triggers external operator call from within mini-python.'''

	class InputType(BaseModel):
		text : str

	class OutputType(BaseModel):
		text : str

	async def invoke(self, text):
		print('From operator:', text, flush=True)
		return 'From operator:' + text
