import os, json
from typing   import Any, get_args, get_origin, Union, List, Dict

from pydantic import BaseModel, Field, model_validator

from .transform import T
from .odb       import ODB


class O(BaseModel):

	__db__ = None

	# Magic
	############################################################################

	def __init__(self, *args, **kwargs):
		if len(args) == 1 and isinstance(args[0], int) and self.__class__.__db__:
			loaded = self.__class__.__db__.get(args[0])
			if not loaded:
				raise ValueError(f'{self.__class__.__name__} with id={args[0]} not found')
			super().__init__(**loaded.to_dict())
			self._resolve_foreign()
		else:
			super().__init__(*args, **kwargs)
			self._resolve_foreign()

	def __str__(self) -> str:
		return self.to_json()

	def __repr__(self):
		return f'<{self.__class__.__name__} id={self.id}>'

	# Private
	############################################################################

	def _resolve_foreign(self):
		for name, field in self.model_fields.items():
			tp    = field.annotation
			value = getattr(self, name, None)

			if isinstance(tp, type) and issubclass(tp, O) and isinstance(value, int):
				setattr(self, name, tp(value))

			elif get_origin(tp) in (list, List):
				subtype = get_args(tp)[0]
				if isinstance(subtype, type) and issubclass(subtype, O):
					fk_field = f'{self.__class__.__name__.lower()}_id'
					items = subtype.db.filter(getattr(subtype, fk_field) == self.id).all()
					setattr(self, name, items)

	# Public class methods
	############################################################################

	@model_validator(mode='before')
	@classmethod
	def convert_nested_o(cls, data):
		def convert(value):
			if isinstance(value, O):
				return value.to_dict()
			if isinstance(value, list):
				return [convert(v) for v in value]
			return value
		if isinstance(data, dict):
			return {k: convert(v) for k, v in data.items()}
		return data

	@classmethod
	def Field(cls, *args, description='', **kwargs):
		if description:
			kwargs.setdefault('json_schema_extra', {})['description'] = description
		return Field(*args, description=description, **kwargs)

	@classmethod
	def to_schema_prompt(cls) -> str:
		return T(T.PYDANTIC, T.PROMPT, cls)

	@classmethod
	def to_schema(cls) -> dict:
		return T(T.PYDANTIC, T.DEREFERENCED_JSONSCHEMA, cls)

	@classmethod
	def set_db(cls, session):
		cls.__db__ = ODB(session)

	@classmethod
	def db(cls):
		return cls.__db__

	@classmethod
	def create_table(cls):
		cls.db().create_table()

	@classmethod
	def drop_table(cls):
		cls.db().drop_table()

	# Getters
	############################################################################

	@property
	def db(self):
		return self.__class__.__db__

	@property
	def id(self):
		return getattr(self, '__id__', None)

	# Public
	############################################################################

	def to_prompt(self) -> str  : return self.to_json()
	def to_dict(self)   -> dict : return T(T.PYDANTIC, T.DATA, self)
	def to_json(self)   -> str  : return json.dumps(self.to_dict(), indent=4, ensure_ascii=False)

	def clone(self):
		data = self.to_dict()
		data.pop('id', None)
		return self.__class__(**data)

	def save(self):
		for name, field in self.model_fields.items():
			tp    = field.annotation
			value = getattr(self, name, None)
			if isinstance(tp, type) and issubclass(tp, O) and isinstance(value, O):
				value.save()
		self.db.__class__(self.db._session, self).save()

	def delete(self):
		self.db.__class__(self.db._session, self).delete()

	def get_description(self, field: str) -> str:
		info = self.model_fields.get(field)
		return info.description or ''
