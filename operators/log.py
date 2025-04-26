from pydantic             import BaseModel
from dapi.lib.operator    import Operator


class Log(Operator):
	'''Triggers external operator call from within mini-python.'''

	class InputType(BaseModel):
		text : str

	class OutputType(BaseModel):
		text : str

	async def invoke(self, text):
		print('From operator:', text)
		return 'From operator:' + text
