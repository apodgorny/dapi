from pydantic               import BaseModel
from typing                 import Any, Callable
from dapi.lib.operator      import Operator


class BranchRecursion(Operator):
	'''Recursively calls another operator and branches by returned list items.'''

	class InputType(BaseModel):
		depth       : int                              # Maximum recursion depth
		level       : int                              # Current recursion level
		operator    : str                              # Name of operator to call
		get_input   : Any                              # Function to compute input for next level
		input_data  : dict                             # Initial input data (only used at root)

	class OutputType(BaseModel):
		value : dict                                   # Result of MyOperator call
		items : list[Any]                              # Recursively nested outputs

	@classmethod
	async def invoke(cls, input_data: dict, config: dict = None) -> dict:
		depth         = input_data['depth']
		level         = input_data['level']
		operator      = input_data['operator']
		get_input     = input_data['get_input']
		current_input = input_data.get('input_data')

		# Call the operator with current input
		result = await operator(current_input)

		# Extract field with list
		if not isinstance(result, dict):
			raise Exception(f'Expected dict output from `{operator}`, got: {type(result)}')
		list_field = next((k for k, v in result.items() if isinstance(v, list)), None)

		if list_field is None:
			return { 'value': result, 'items': [] }

		items = []
		if level < depth:
			for item in result[list_field]:
				next_input = await operator(get_input, {
					'level' : level + 1,
					'item'  : item
				})
				child = await cls.invoke({
					'depth'      : depth,
					'level'      : level + 1,
					'operator'   : operator,
					'get_input'  : get_input,
					'input_data' : next_input
				})
				items.append(child)

		return {
			'value': result,
			'items': items
		}
