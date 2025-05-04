import json
from typing import get_args, get_origin

from pydantic import BaseModel, Field


class O(BaseModel):
	'''Base class for prompt templates with JSON rendering and nested support.'''

	Field = Field  # allow usage like O.Field(...)

	@classmethod
	def prompt(cls, omit: list[str] = None) -> str:
		from typing import Optional
		cls.model_rebuild()
		instance = cls.model_construct()
		return instance.omit(*(omit or [])).__repr__()

	################################################################################

	def __init__(self, **data):
		super().__init__(**data)
		self._exclude: set[str] = set()

	def __repr__(self) -> str:
		'''Render object as JSON with descriptions or nested structures, omitting excluded sfields.'''
		excluded = getattr(self, '_exclude', set())
		d        = {}

		for k, v in self.model_fields.items():
			if k in excluded:
				continue

			typ = v.annotation

			if isinstance(typ, type) and issubclass(typ, O):
				d[k] = json.loads(repr(typ()))
			elif get_origin(typ) in [list, tuple]:
				item_type = get_args(typ)[0]
				if isinstance(item_type, type) and issubclass(item_type, O):
					d[k] = [json.loads(repr(item_type()))]
				else:
					d[k] = f'<{self.get_description(k)}>'
			else:
				d[k] = f'<{self.get_description(k)}>'
				
		return json.dumps(d, indent=4, ensure_ascii=False)

	def __str__(self) -> str:
		'''Render current object values as JSON, including nested structures, omitting excluded fields.'''
		excluded = getattr(self, '_exclude', set())
		d        = {}

		for k, v in self.model_fields.items():
			if k in excluded:
				continue

			val = getattr(self, k, None)

			if isinstance(val, O):
				d[k] = json.loads(str(val))
			elif isinstance(val, (list, tuple)) and val and isinstance(val[0], O):
				d[k] = [json.loads(str(i)) for i in val]
			else:
				d[k] = val

		return json.dumps(d, indent=4, ensure_ascii=False)

	################################################################################

	def omit(self, *fields: str) -> 'O':
		'''Return a shallow copy with certain fields excluded from __repr__ and __str__.'''
		clone          = self.copy()
		clone._exclude = set(fields)
		return clone

	def get_description(self, field: str) -> str:
		'''Return description of a field or empty string.'''
		info = self.model_fields.get(field)
		return info.description if info and info.description else ''

	def to_dict(self) -> dict:
		'''Return object as dict with all data.'''
		return self.model_dump()

	@classmethod
	def from_dict(cls, data: dict) -> 'O':
		'''Create instance from dict with nested O support.'''
		fields = cls.model_fields
		parsed = {}

		for k, v in data.items():
			if k not in fields:
				continue

			typ = fields[k].annotation

			if isinstance(typ, type) and issubclass(typ, O):
				parsed[k] = typ.from_dict(v)
			elif get_origin(typ) in [list, tuple]:
				item_type = get_args(typ)[0]
				if isinstance(item_type, type) and issubclass(item_type, O):
					parsed[k] = [item_type.from_dict(i) for i in v]
				else:
					parsed[k] = v
			else:
				parsed[k] = v

		return cls(**parsed)
