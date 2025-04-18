import os
from dapi.lib import Module


class Model:
	'''Base class for LLM and runtime models.'''

	def __init__(self, name: str):
		self.name = name

	@classmethod
	def load(cls, model_id: str) -> 'Model':
		'''
		Load model by `provider::name` syntax from external module file.
		'''

		if '::' not in model_id:
			raise ValueError(f'Invalid model_id: `{model_id}`. Expected format "provider::name"')

		provider, name = model_id.split('::', 1)

		# MODELS_DIR must contain files like model_<provider>.py
		root_dir  = os.environ.get('MODELS_DIR') or os.path.join(os.path.dirname(__file__), '..', 'models')
		file_path = os.path.join(root_dir, f'model_{provider}.py')

		try:
			model_cls = Module.find_class_by_base(cls, file_path)
			instance  = model_cls(name)
			instance.model_id = model_id
			return instance

		except FileNotFoundError:
			raise ValueError(f'Model file not found: `{file_path}`')

		except AttributeError:
			raise ValueError(f'No subclass of Model found in `{file_path}`')
