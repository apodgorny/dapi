from pydantic               import BaseModel
from typing                 import Any
from dapi.lib.operator      import Operator


class brancher(Operator):
	'''Branches stuff'''
	
	class InputType(BaseModel):
		item     : str
		operator : str

	class OutputType(BaseModel):
		data : dict[str, Any]

	@classmethod
	async def invoke(cls, input, config=None):
		print('globals at load time:', globals().keys())
		result = await call({
			'name' : input['operator'],
			'data' : input['item']
		})
		# for item in result['items']:
		# 	print(item)
		return { 'data' : { 'item' : input['item'] } }
