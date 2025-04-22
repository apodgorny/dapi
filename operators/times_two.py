from pydantic import BaseModel
from dapi.lib.operator import Operator


class TimesTwo(Operator):
	'''Plugin operator that multiplies input by two.'''
	
	class InputType(BaseModel):
		x: int

	class OutputType(BaseModel):
		x: int
	
	@classmethod
	async def invoke(cls, input_data, config=None):
		return {'x': input_data['x'] * 2}
