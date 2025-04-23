from pydantic             import BaseModel
from dapi.lib.operator    import Operator


class Log(Operator):
	'''Triggers external operator call from within mini-python.'''

	class InputType(BaseModel):
		text : str

	class OutputType(BaseModel):
		text : str

	@classmethod
	async def invoke(cls, input, config=None):
		print('From operator:', input['text'])
		return { 'text': 'From operator:' + input['text'] }
