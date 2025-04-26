from dapi.lib.string import String

class Frame:
	def __init__(self, name, lineno, interpreter='', file=None, line=None):
		self.name        = name
		self.file        = file
		self.line        = line
		self.lineno      = lineno
		self.interpreter = interpreter
		self.subframes   = []

class ExecutionContext:
	def __init__(self,
		enable_color  : bool = True,
		enable_code   : bool = True,
		enable_detail : bool = True
	):
		self._root        = Frame(name='root', lineno=0)
		self._stack       = [self._root]
		self._indent      = 0
		self._indent_text = '|'
		self.i            = ''

		self.enable_color  = enable_color
		self.enable_code   = enable_code
		self.enable_detail = enable_detail

	@property
	def current(self) -> Frame:
		return self._stack[-1]

	def _color(self, text: str) -> str:
		if self.enable_color:
			return String.color(text, String.LIGHTGRAY)
		return text

	def update_indent(self, n: int):
		self._indent += n
		self.i = self._color(self._indent_text) * self._indent

	def push(self, name: str, lineno: int, interpreter: str = '', file: str = None, line: str = None):
		# If detail is disabled, filter out non-operator level frames
		if not self.enable_detail and interpreter == 'mini':
			return

		line_text = f' : {line.strip()}' if self.enable_code and line else ''
		print(self.i, f'→ {name}{line_text}')
		self.update_indent(1)

		frame = Frame(
			name        = name,
			file        = file,
			line        = line,
			lineno      = lineno,
			interpreter = interpreter
		)
		self.current.subframes.append(frame)
		self._stack.append(frame)

	def pop(self):
		if len(self._stack) > 1:
			frame = self._stack.pop()
			if not self.enable_detail and frame.interpreter == 'mini':
				self.update_indent(-1)
				return

			line_text = f' : {frame.line.strip()}' if self.enable_code and frame.line else ''
			self.update_indent(-1)
			print(self.i, f'← {frame.name}{line_text}')

	############################################################################

	def print_trace(self, frame: Frame = None, indent: int = 0):
		if frame is None:
			frame = self._root

		prefix = self._color(self._indent_text) * indent
		file_info = f'({frame.file}:{frame.lineno})' if frame.file else f'(line {frame.lineno})'
		code_snippet = f' : {frame.line.strip()}' if self.enable_code and frame.line else ''

		# Detail control: if disabled, only show operator frames
		if self.enable_detail or frame.interpreter != 'mini':
			print(f'{prefix}- {frame.name} {file_info}{code_snippet}')

		for child in frame.subframes:
			self.print_trace(child, indent + 1)

	def to_standard_trace(self, frame: Frame = None, indent: int = 0, short: bool = False, max_levels: int = 10) -> str:
		'''
		Returns a standard plain-text trace suitable for including in exceptions.
		If short=True, shows only the last `max_levels` frames.
		'''
		if frame is None:
			frame = self._root

		lines = []

		def _recurse(f: Frame, level: int):
			prefix = '  ' * level
			file_info = f'({f.file}:{f.lineno})' if f.file else f'(line {f.lineno})'
			code_snippet = f' : {f.line.strip()}' if self.enable_code and f.line else ''

			if self.enable_detail or f.interpreter != 'mini':
				lines.append((level, f'{prefix}- {f.name} {file_info}{code_snippet}'))

			for child in f.subframes:
				_recurse(child, level + 1)

		_recurse(frame, indent)

		if short:
			# Оставляем только последние max_levels уровней
			lines = lines[-max_levels:]

		# Теперь рендерим только текст
		return '\n'.join(text for _, text in lines)

