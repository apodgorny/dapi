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
			result = await config['invoke'](name, {'text': data.get('text', '')})
			
			if isinstance(result, dict) and 'output' in result:
				return {'data': result['output']}
			
		return {'data': result}
