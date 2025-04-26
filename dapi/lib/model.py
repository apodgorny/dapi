import os
from pydantic import BaseModel

from dapi.lib import Module, Datum


class Model:
	'''Base class for LLM and runtime models.'''

	def __init__(self, name: str):
		self.name = name

	def to_json_schema(self, schema: any) -> dict:
		if isinstance(schema, Datum):		                            return schema.to_schema()
		if isinstance(schema, type) and issubclass(schema, BaseModel):	return schema.model_json_schema()
		if isinstance(schema, dict):		                            return schema
		raise ValueError(f'Unsupported schema type: {type(schema).__name__}')

	@classmethod
	def load(cls, model_id: str) -> 'Model':
		'''
		Load model by `provider::name` syntax from external module file.
		'''

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
