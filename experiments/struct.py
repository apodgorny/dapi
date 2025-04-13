from typing import Any, Dict


class Struct:
	def __init__(self, data: dict):
		object.__setattr__(self, '_data', {})
		for key, value in data.items():
			self._data[key] = self._to_struct(value)

############################################################################

	def _to_struct(self, obj: Any) -> Any:
		if isinstance(obj, dict):
			return Struct(obj)
		elif isinstance(obj, list):
			return [self._to_struct(item) for item in obj]
		return obj

############################################################################

	def _to_dict(self, obj: Any) -> Any:
		if isinstance(obj, Struct):
			return { key: self._to_dict(value) for key, value in obj._data.items() }
		elif isinstance(obj, list):
			return [self._to_dict(item) for item in obj]
		return obj

############################################################################

	def to_dict(self) -> Dict[str, Any]:
		return self._to_dict(self)

	def to_json(self, indent=4) -> str:
		return json.dumps(self.to_dict(), indent=indent)

############################################################################

	@classmethod
	def from_dict(cls, data: dict) -> 'Struct':
		return cls(data)

############################################################################

	def __getattr__(self, name: str) -> Any:
		if name in self._data:
			return self._data[name]
		raise AttributeError(f"No such attribute: '{name}'")

	def __setattr__(self, name: str, value: Any):
		if name == '_data':
			super().__setattr__(name, value)
		else:
			self._data[name] = self._to_struct(value)

	def __getitem__(self, key: str) -> Any:
		return self._data[key]

	def __setitem__(self, key: str, value: Any):
		self._data[key] = self._to_struct(value)

	def __contains__(self, key: str) -> bool:
		return key in self._data

	def __repr__(self):
		return f'Struct({self})'

	def __str__(self):
		return self.to_json()

############################################################################

if __name__ == '__main__':
	test_data = {
		'user': {
			'name'   : 'Alice',
			'address': {
				'city'    : 'Wonderland',
				'street'  : 'Rabbit Hole',
				'zipcode' : 12345,
				'extra'   : {
					'floor': 2,
					'unit' : 'B'
				}
			}
		},
		'items': [
			{'id': 1, 'name': 'Potion'},
			{'id': 2, 'name': 'Cake'}
		]
	}

	struct = Struct(test_data)
	assert struct.user.name == 'Alice'
	assert struct.user.address.extra.unit == 'B'
	assert struct.items[1].name == 'Cake'

	reversed_data = struct.to_dict()
	assert reversed_data == test_data

	print(struct.user.name)
	struct.user.name = 'Victor'
	print(struct.user.name)

	print('Test passed.')
