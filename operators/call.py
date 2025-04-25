from pydantic             import BaseModel
from dapi.lib.operator    import Operator
from typing               import Dict, Any

class Call(Operator):
	'''Triggers external operator call from within mini-python.'''

	class InputType(BaseModel):
		name   : str
		kwargs : Dict[str, Any] = {}

	class OutputType(BaseModel):
		data : Dict[str, Any]

	async def invoke(self, name, kwargs):
		print(name, data)
		result = await self.invoke_operator('log', kwargs, self.execution_context)
		return {'data': result}
