class Struct:
	'''Dot-accessible nested dictionary wrapper.'''

	def __init__(self, data=None):
		self._data = self._wrap(data or {})

	def _wrap(self, value):
		if isinstance(value, dict):
			return {k: self._wrap(v) for k, v in value.items()}
		if isinstance(value, list):
			return [self._wrap(i) for i in value]
		return value

	def to_dict(self):
		def unwrap(v):
			if isinstance(v, Struct):
				return v.to_dict()
			if isinstance(v, dict):
				return {k: unwrap(x) for k, x in v.items()}
			if isinstance(v, list):
				return [unwrap(i) for i in v]
			return v
		return unwrap(self._data)

	@classmethod
	def from_dict(cls, d):
		return cls(d)

	def __getattr__(self, name):
		if name in self._data:
			return self._data[name]
		raise AttributeError(name)

	def __setattr__(self, name, value):
		if name == '_data':
			object.__setattr__(self, name, value)
		else:
			self._data[name] = self._wrap(value)

	def __getitem__(self, key):
		return self._data[key]

	def __setitem__(self, key, value):
		self._data[key] = self._wrap(value)

	def __contains__(self, key):
		return key in self._data

	def __repr__(self):
		return f'Struct({self._data})'