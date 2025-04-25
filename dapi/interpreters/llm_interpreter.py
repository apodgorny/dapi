import re
import json

from dapi.lib import (
	Datum,
	Interpreter,
	Struct,
	Model,
	DapiException,
	ExecutionContext
)


class LLMInterpreter(Interpreter):
	'''
	Interprets prompts with LLMs using {{input.x}} syntax. 
	Uses `config` to determine model, temperature, etc.
	'''

	type = 'llm'

	async def invoke(
		self,
		operator_name : str,
		code          : str,
		input         : Datum,
		output        : Datum,
		config        : dict,
		context       : ExecutionContext
	) -> Datum:

		if context is None: raise ValueError('ExecutionContext must be explicitly provided')
		config      = config or {}
		model_id    = config.get('model_id', 'ollama::gemma3:4b')
		temperature = config.get('temperature', 0.0)
		role        = config.get('role', 'user')
		system      = config.get('system')  # optional

		input_data  = input.to_dict()
		input_paths = set(m.group(1) for m in re.finditer(r'\{\{\s*input\.([a-zA-Z0-9_.]+)\s*\}\}', code))

		# Replace {{input.x}} → value
		for path in input_paths:
			if path not in input:
				raise ValueError(f'Missing input path `{path}` in operator `{operator_name}`')
			code = code.replace(f'{{{{input.{path}}}}}', str(input[path]))

		model = Model.load(model_id)
		context.push(operator_name, 1, 'llm')

		try:
			result = await model(
				prompt          = code,
				response_schema = output.schema,
				role            = role,
				temperature     = temperature,
				system          = system
			)
			output.from_dict(result)
			return output
		except Exception as e:
			raise DapiException.consume(e)
		finally:
			context.pop()