from pydantic import BaseModel

from dapi.lib import Operator, Model


class Ask(Operator):
	'''
	Performs an LLM prompt completion based on the given input and model configuration.
	'''

	class InputType(BaseModel):
		input           : dict
		prompt          : str
		response_schema : type[BaseModel]
		model_id        : str   = 'ollama::gemma3:4b'
		temperature     : float = 0.0

	class OutputType(BaseModel):
		result : dict

	async def invoke(self,
		input,
		prompt,
		response_schema,

		model_id    = 'ollama::gemma3:4b',
		temperature = 0.0
	):
		response = await Model.generate(
			prompt          = prompt,
			input           = input,
			response_schema = response_schema,
			model_id        = model_id,
			temperature     = temperature
		)

		return response
