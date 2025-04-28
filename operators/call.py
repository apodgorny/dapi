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
		operator_class  = await self.get_operator_class(name)
		expected_fields = operator_class().input_fields()
		missing         = [field for field in expected_fields if field not in kwargs]

		if missing:
			raise DapiException(
				status_code = 400,
				detail      = f'Missing fields {missing} for operator `{name}`'
		)

		result = await self.call_external_operator(
			name    = name,
			kwargs  = kwargs
		)
		return result
