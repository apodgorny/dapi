from dapi.lib.string    import String
from dapi.lib.highlight import Highlight

class Frame:
	def __init__(
		self,
		name        : str,
		lineno      : int   = 1,
		interpreter : str   = '',
		file        : str   = None,
		line        : str   = None,
		importance  : float = 0
	):
		self.name        = name
		self.file        = file
		self.line        = line
		self.lineno      = lineno
		self.interpreter = interpreter
		self.importance  = importance
		self.subframes   = []

class ExecutionContext:
	def __init__(self,
		enable_color  : bool  = True,
		enable_code   : bool  = True,
		importance    : float = 0.5
	):
		self._root        = Frame(name='root', lineno=0)
		self._stack       = [self._root]
		self._indent      = 0
		self._indent_text = String.color(' ', String.GRAY) if enable_color else ' '
		self.i            = ''

		self.enable_color  = enable_color
		self.enable_code   = enable_code
		self.enable_detail = True
		self.importance    = importance

	#################################################################

	def _get_code(self, frame):
		if self.enable_code and frame.line:
			code = frame.line.strip() + '\n'
			if self.enable_color:
				code = Highlight.python(code).replace('\n', '')
			return code
		return ''

	def _get_interpreter(self, frame):
		interpreter = frame.interpreter
		if self.enable_color:
			colors = {
				'llm'  : String.MAGENTA,
				'mini' : String.GREEN,
				'full' : String.LIGHTBLUE
			}
			interpreter = String.color('▮', colors[interpreter])
		return interpreter

	def _get_name(self, frame):
		return frame.name

	def _get_detail(self, detail=''):
		if self.enable_color:
			detail = String.color(detail, String.GRAY, 'i')
		return detail

	def _get_direction(self, is_push):
		direction = '→' if is_push else '←'
		if self.enable_color:
			color = String.GREEN if is_push else String.RED
			direction = String.color(direction, color)
		return direction

	def _get_line(self, frame, is_push=True, detail=None):
		interpreter = self._get_interpreter(frame)
		name        = self._get_name(frame)
		code        = self._get_code(frame)
		detail      = self._get_detail(detail)
		direction   = self._get_direction(is_push)
		left        = f'{interpreter}{self.i} {direction} {name} :'
		return  f'{left} {code}{detail}'

	#################################################################

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

	def push(self, 
		name        : str,
		lineno      : int   = 1,
		interpreter : str   = '',
		file        : str   = None,
		line        : str   = None,
		importance  : float = 0,
		detail      : str   = None
	):
		frame = Frame(
			name        = name,
			file        = file,
			line        = line,
			lineno      = lineno,
			interpreter = interpreter,
			importance  = importance
		)

		self.current.subframes.append(frame)
		self._stack.append(frame)

		if frame.importance > self.importance:
			logline = self._get_line(frame=frame, is_push=True, detail=detail)
			print(logline)
		self.update_indent(1)

	def pop(self, detail=None):
		if len(self._stack) > 1:
			frame = self._stack.pop()
			if not self.enable_detail and frame.interpreter == 'mini':
				self.update_indent(-1)
				return
			
			self.update_indent(-1)
			if frame.importance > self.importance:
				logline = self._get_line(frame, is_push=False, detail=detail)
				print(logline)

	#################################################################

	def print_trace(self, frame: Frame = None, indent: int = 0):
		if frame is None:
			frame = self._root

		prefix       = self._color(self._indent_text) * indent
		file_info    = f'({frame.file}:{frame.lineno})' if frame.file else f'(line {frame.lineno})'
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
			prefix       = '  ' * level
			file_info    = f'({f.file}:{f.lineno})' if f.file else f'(line {f.lineno})'
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

