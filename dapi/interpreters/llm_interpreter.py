import re
from dapi.lib import (
	Datum,
	Struct,
	Model,
	DapiException,
	ExecutionContext,
	Interpreter
)

class LLMInterpreter(Interpreter):
	'''
	Executes a prompt using LLMs with {{input.x}} variable substitution.
	'''

	type = 'llm'

	async def invoke(self) -> dict:
		try:
			if self.context is None:
				raise ValueError('ExecutionContext must be explicitly provided')

			config      = self.config or {}
			model_id    = config.get('model_id', 'ollama::gemma3:4b')
			temperature = config.get('temperature', 0.0)
			role        = config.get('role', 'user')
			system      = config.get('system')

			prompt      = self.code
			input_data  = self.input
			output_type = self.config.get('output_schema')
			if output_type is None:
				raise ValueError(f'[LLMInterpreter] Missing `output_schema` in config for operator `{self.name}`')

			# Replace {{input.x}} → value
			input_paths = set(m.group(1) for m in re.finditer(r'\{\{\s*input\.([a-zA-Z0-9_.]+)\s*\}\}', prompt))
			for path in input_paths:
				if path not in input_data:
					raise ValueError(f'[LLMInterpreter] Missing input field `{path}` in operator `{self.name}`')
				prompt = prompt.replace(f'{{{{input.{path}}}}}', str(input_data[path]))

			model = Model.load(model_id)

			result = await model(
				prompt          = prompt,
				response_schema = output_type,
				role            = role,
				temperature     = temperature,
				system          = system
			)
			
			# Convert to tuple to match minipython and fullpython
			result = tuple(result[k] for k in result)
			if len(result) == 1:
				result = result[0]

			return result

		except Exception as e:
			raise DapiException.consume(e)
