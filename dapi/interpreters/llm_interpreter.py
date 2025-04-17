import re
import json
from dapi.lib   import Datum, Interpreter
from dapi.lib.struct import Struct
from dapi.lib.model import Model


class LLMInterpreter(Interpreter):
	'''
    Interprets prompts with LLMs using {{input.x}} syntax. 
    Uses `meta` to determine model, temperature, etc.
    '''

	async def invoke(
		self,
		operator_name : str,
		code          : str,
		input         : Datum,
		output        : Datum,
		config        : dict = {}
	) -> Datum:
		# Default model settings with config overrides
		model_id    = config.get('model_id',    'ollama::gemma3:4b')
		temperature = config.get('temperature', 0.0)
		role        = config.get('role',        'user')
		system      = config.get('system',      None)

		input_data  = input.to_dict()
		input_paths = set(m.group(1) for m in re.finditer(r'\{\{\s*input\.([a-zA-Z0-9_.]+)\s*\}\}', code))

		for path in input_paths:
			if path not in input:
				raise ValueError(f'Missing input path `{path}` in operator `{operator_name}`')
			code = code.replace(f'{{{{input.{path}}}}}', str(input[path]))

		model = Model.load(model_id)

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
			raise ValueError(f'LLM error in `{operator_name}`: {e}')
