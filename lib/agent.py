import re

from .operator import Operator
from .string   import String


class Agent(Operator):

	def _get_template(self):
		if not hasattr(self, 'template'):
			raise ValueError(f'Property `template` is not defined in `{self.__class__.__name__}`')
		return self.template

	def fill(self, template: str, **vars) -> str:
		template = String.unindent(template)
		matches  = set(re.findall(r'\{\{\s*([a-zA-Z0-9_.]+)\s*\}\}', template))

		for path in matches:
			if path not in vars:
				raise ValueError(f'[LLM] Field `{path}` mentioned in template, but not supplied')
			template = template.replace(f'{{{{{path}}}}}', str(vars[path]))
		return template

	async def ask(self, prompt = None, schema = None):
		return await self.globals['ask'](
			prompt          = prompt,
			response_schema = (schema or self.output_type)  # Passing BaseModel here
		)