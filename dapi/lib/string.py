class String:
	'''String utilities for formatting, normalization, and validation.'''

	@staticmethod
	def indent(text: str, prefix: str = '\t') -> str:
		'''Adds `prefix` at the beginning of every non-empty line.'''
		return '\n'.join(
			f'{prefix}{line}' if line.strip() else line
			for line in text.splitlines()
		)

	@staticmethod
	def dedent(text: str) -> str:
		'''Removes common leading whitespace from all lines.'''
		import textwrap
		return textwrap.dedent(text)

	@staticmethod
	def is_empty(s: str) -> bool:
		'''Checks if string is None or consists only of whitespace.'''
		return not s or s.strip() == ''

	@staticmethod
	def to_snake_case(name: str) -> str:
		'''Converts CamelCase or kebab-case to snake_case.'''
		import re
		name = re.sub(r'(?<!^)(?=[A-Z])', '_', name).lower()
		return name.replace('-', '_')

	@staticmethod
	def camel_to_snake(name: str) -> str:
		'''Converts CamelCase to snake_case (preserving acronyms).'''
		import re
		return re.sub(r'(?<!^)(?=[A-Z])', '_', name).lower()

	@staticmethod
	def normalize_whitespace(text: str) -> str:
		'''Replaces multiple spaces/newlines with a single space.'''
		import re
		return re.sub(r'\s+', ' ', text).strip()
