from pydantic  import BaseModel
from dapi.lib  import Operator
from typing    import Dict, Any


class Call(Operator):
	'''Triggers external operator call from within mini-python.'''

	class InputType(BaseModel):
		name   : str
		kwargs : Dict[str, Any] = {}

	class OutputType(BaseModel):
		data : Dict[str, Any]

	async def invoke(self, name, kwargs):
		result = await self.call_external_operator(
			name    = name,
			kwargs  = kwargs
		)
		return result
