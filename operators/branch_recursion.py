from pydantic               import BaseModel
from typing                 import Any
from dapi.lib.operator      import Operator


class BranchRecursion(Operator):
	'''Recursively calls an operator and builds a tree structure using its list output.''' 

	class InputType(BaseModel):
		depth       : int
		level       : int
		operator    : str
		get_input   : str
		input_data  : dict

	class OutputType(BaseModel):
		value : dict
		items : list[Any]

	@classmethod
	async def invoke(
		cls,
		input  : dict,
		config : dict = None
	) -> dict:
		depth      = input['depth']
		level      = input['level']
		operator   = input['operator']
		get_input  = input['get_input']
		data       = input['input_data']

		# Call operator functions (injected into interpreter scope)
		result = await operator(data)
		items  = result.get('items', [])

		children = []
		if level < depth:
			for item in items:
				next_input = await get_input({
					'level': level + 1,
					'item' : item
				})
				child = await cls.invoke({
					'depth'      : depth,
					'level'      : level + 1,
					'operator'   : operator,
					'get_input'  : get_input,
					'input_data' : next_input
				})
				children.append(child)

		return {
			'value': result,
			'items': children
		}
