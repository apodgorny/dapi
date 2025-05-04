from typing import Any

from pydantic import BaseModel

from .agent import Agent


################################################################

class AgentOnGrid(Agent):
	'''Base class for agents inside StateGrid. Stateless transformation: State → State.'''

	class InputType(BaseModel):
		state : str
		data  : Any
		h_ctx : list[Any]
		v_ctx : list[Any]
		c_ctx : dict[str, Any]

	class OutputType(BaseModel):
		items : list[dict]

	async def invoke(self, state, data, h_ctx, v_ctx, c_ctx):
		'''Agent logic happens here. Must return updated State.'''
		raise NotImplementedError('Agent must implement invoke(state)')
