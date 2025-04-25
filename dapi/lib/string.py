import re


class String:
	'''String utilities for formatting, normalization, and validation.'''

	# ANSI styles
	RESET         = '\033[0m'
	BOLD          = '\033[1m'
	ITALIC        = '\033[3m'
	UNDERLINE     = '\033[4m'
	STRIKETHROUGH = '\033[9m'

	# ANSI colors
	BLACK         = '\033[30m'
	RED           = '\033[31m'
	GREEN         = '\033[32m'
	YELLOW        = '\033[33m'
	BLUE          = '\033[34m'
	MAGENTA       = '\033[35m'
	CYAN          = '\033[36m'
	WHITE         = '\033[37m'

	GRAY          = '\033[90m'
	LIGHTRED      = '\033[91m'
	LIGHTGREEN    = '\033[92m'
	LIGHTYELLOW   = '\033[93m'
	LIGHTBLUE     = '\033[94m'
	LIGHTMAGENTA  = '\033[95m'
	LIGHTCYAN     = '\033[96m'
	LIGHTWHITE    = '\033[97m'
	LIGHTGRAY     = GRAY  # alias
	DARK_GRAY     = '\033[38;5;235m'

	@staticmethod
	def indent(text: str, prefix: str = '\t') -> str:
		'''Adds `prefix` at the beginning of every non-empty line.'''
		return '\n'.join(
			f'{prefix}{line}' if line.strip() else line
			for line in text.splitlines()
		)

	@staticmethod
	def unindent(text: str) -> str:
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
	def snake_to_camel(name: str, capitalize=True) -> str:
		'''Converts snake_case to CamelCase or camelCase depending on `capitalize` argument value.'''
		components = name.split('_')
		if capitalize:
			return ''.join(x.title() for x in components)
		return components[0] + ''.join(x.title() for x in components[1:])

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

	@staticmethod
	def underlined(text: str) -> str:
		'''Underlines the given text.'''
		return f'{String.UNDERLINE}{text}{String.RESET}'

	@staticmethod
	def italic(text: str) -> str:
		'''Italicizes the given text.'''
		return f'{String.ITALIC}{text}{String.RESET}'

	@staticmethod
	def strikethrough(text: str) -> str:
		'''Strikes through the given text.'''
		return f'{String.STRIKETHROUGH}{text}{String.RESET}'

	@staticmethod
	def color(text: str, color: str = None) -> str:
		'''Wraps text in ANSI color. Use constants like String.LIGHTGRAY.'''
		if not color:
			return text
		return f'{color}{text}{String.RESET}'

	@staticmethod
	def color_between(
		text      : str,
		begin     : str,
		end       : str,
		color     : str | None = None,
		inclusive : bool = True
	) -> str:
		if color is None:
			return text

		pat = re.compile(
			fr'({re.escape(begin)})(.*?)({re.escape(end)})',
			re.DOTALL
		)

		def repl(m: re.Match) -> str:
			left, middle, right = m.groups()
			if inclusive:
				# Красим маркеры + содержимое
				return String.color(f'{left}{middle}{right}', color)
			# Красим только середину
			return f'{left}{String.color(middle, color)}{right}'

		return pat.sub(repl, text)

	@staticmethod
	def highlight(text: str, highlight_groups: dict[str, list[str]]) -> str:
		'''
		Highlights groups of substrings with specified colors.

		Accepts dict like:
		{
			String.LIGHTRED   : ['fox', 'jump'],
			String.LIGHTGREEN : ['dog', 'lazy'],
		}
		'''
		import re

		# Flatten to word → color map
		word_to_color = {
			word: color
			for color, words in highlight_groups.items()
			for word in words
		}

		def replacer(match):
			word = match.group(0)
			return f'{word_to_color[word]}{word}{String.RESET}'

		# Match longest words first
		pattern = '|'.join(re.escape(word) for word in sorted(word_to_color, key=len, reverse=True))
		return re.sub(pattern, replacer, text)



