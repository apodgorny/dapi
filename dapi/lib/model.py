import os, re

from pydantic import BaseModel

from .module         import Module
from .datum          import Datum
from .string         import String
from .dapi_exception import DapiException


class Model:

	def __init__(self, name: str):
		self.name = name

	##################################################################

	def to_json_schema(self, schema: any) -> dict:
		if isinstance(schema, Datum):		                            return schema.to_schema()
		if isinstance(schema, type) and issubclass(schema, BaseModel):	return schema.model_json_schema()
		if isinstance(schema, dict):		                            return schema
		raise ValueError(f'Unsupported schema type: {type(schema).__name__}')

	##################################################################

	@staticmethod
	def fill_prompt(template: str, input_data: dict) -> str:
		template = String.unindent(template)
		matches  = set(re.findall(r'\{\{\s*([a-zA-Z0-9_.]+)\s*\}\}', template))

		for path in matches:
			if path not in input_data:
				raise ValueError(f'[LLM] Field `{path}` mentioned in prompt, but not supplied')
			template = template.replace(f'{{{{{path}}}}}', str(input_data[path]))
		return template

	@classmethod
	def load(cls, model_id: str) -> 'Model':
		if '::' not in model_id:
			raise ValueError(f'Invalid model_id: `{model_id}`. Expected format `provider::name`')

		provider, name = model_id.split('::', 1)

		# MODELS_DIR must contain files like model_<provider>.py
		root_dir  = os.environ.get('MODELS_DIR') or os.path.join(os.path.dirname(__file__), '..', 'models')
		file_path = os.path.join(root_dir, f'model_{provider}.py')

		try:
			model_cls         = Module.find_class_by_base(cls, file_path)
			instance          = model_cls(name)
			instance.model_id = model_id
			return instance

		except FileNotFoundError:
			raise ValueError(f'Model file not found: `{file_path}`')

		except AttributeError:
			raise ValueError(f'No subclass of Model found in `{file_path}`')

	@classmethod
	async def generate(
		cls,
		prompt          : str,
		input           : dict,
		response_schema : BaseModel,

		model_id        : str        = 'ollama::gemma3:4b',
		role            : str        = 'user',
		temperature     : float      = 0.0,
		system          : str | None = None

	) -> dict:
		try:
			prompt          = Model.fill_prompt(prompt, input)
			model           = Model.load(model_id)
			# response_schema = response_schema.model_json_schema()

			result = await model(
				prompt          = prompt,
				response_schema = response_schema,
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