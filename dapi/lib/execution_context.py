import traceback as tb


class ExecutionContext:
	def __init__(self):
		self.stack = []
		self._mark  = None

	def push(self, filename, lineno, name, line='', interpreter='python'):
		frame = tb.FrameSummary(
			filename = filename,
			lineno   = lineno,
			name     = name,
			line     = line
		)
		self.stack.append(frame)

	def pop(self):
		if self.stack:
		 	self.stack.pop()

	def start_autotrace(self):
		self._mark = tb.extract_stack()[-2]

	def stop_autotrace(self):
		if self._mark:
			py_stack  = tb.extract_stack()[:-1]
			try:
				idx = py_stack.index(self._mark)
				self.stack += py_stack[idx + 1:]
			except ValueError:
				raise Exception('Failed to autotrace python call stack')

			self._mark = None
		else:
			raise Exception('Failed to stop autotrace – mark is not set')

	def get_trace(self):
		lines = []
		for item in self.stack:
			loc  = f'(`{item.filename}`@{item.lineno})'
			name = f'`{item.filename}`'
			line = f'`\n{item.line}`' if item.line else ''
			lines.append(f'--> {name} {loc}{line}')
		self.trace = '\n'.join(lines)