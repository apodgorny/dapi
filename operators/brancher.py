from pydantic               import BaseModel
from typing                 import Any
from dapi.lib.operator      import Operator


class Brancher(Operator):
	'''Branches stuff'''
	
	class InputType(BaseModel):
		item     : str
		operator : str

	class OutputType(BaseModel):
		data : dict[str, Any]

	async def invoke(self, item, operator, call):
		result = await call(
			name = operator,
			data = item
		)
		# for item in result['items']:
		# 	print(item)
		return { 'data' : { 'item' : item } }
