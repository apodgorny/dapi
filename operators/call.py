from pydantic             import BaseModel
from dapi.lib.operator    import Operator
from typing               import Dict, Any

class Call(Operator):
	'''Triggers external operator call from within mini-python.'''

	class InputType(BaseModel):
		name : str
		data : Dict[str, Any] = {}
		
		class Config:
			extra = "allow"  # Allow extra fields in input

	class OutputType(BaseModel):
		data : dict

	@classmethod
	async def invoke(cls, input, config=None):
		name = input['name']
		data = input.get('data', {})
		
		if config and 'invoke' in config:
			# The text field needs to be at the top level for the log operator
			result = await config['invoke'](name, {'text': data.get('text', '')})
			
			if isinstance(result, dict) and 'output' in result:
				# Extract the output field if it exists
				return {'data': result['output']}
			
			return {'data': result}
		else:
			# Fallback if invoke function is not available
			return {'data': {'result': 'invoke function not available'}}
