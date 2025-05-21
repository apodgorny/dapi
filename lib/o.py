import os, json
from typing   import Any, get_args, get_origin, Union, List, Dict

from pydantic import BaseModel, Field, model_validator

from .jscpy   import jscpy
from .transformations import Transform


class O(BaseModel):
	# @classmethod
	# def Field(cls, *args, **kwargs):
	# 	return Field(*args, **kwargs)

	@model_validator(mode='before')
	@classmethod
	def convert_nested_o(cls, data):
		'''Recursively convert any O instances inside any fields to dicts.'''
		if isinstance(data, dict):
			return {
				k: (
					v.to_dict() if isinstance(v, O) else
					[vv.to_dict() if isinstance(vv, O) else vv for vv in v] if isinstance(v, list) else
					v
				)
				for k, v in data.items()
			}
		return data

	@classmethod
	def Field(cls, *args, description=None, **kwargs):
		# Inject description into json_schema_extra
		if description:
			kwargs.setdefault('json_schema_extra', {})['description'] = description

		return Field(*args, description=description, **kwargs)

	def __str__(self) -> str:
		return json.dumps(self.to_dict(), indent=4, ensure_ascii=False)

	@classmethod
	def to_prompt(cls) -> str:
		return Transform(Transform.PYDANTIC, Transform.PROMPT, cls)

	def to_log(self):
		id_s = ''
		s    = ''
		for attr in self.__dict__:
			if not attr.startswith('__'):
				if id in attr.split('_'):
					id_s = attr
				else:
					s += f'\n{attr}'
		return f'{id_s}\n{"="*40}\n{s}'

	def to_dict(self) -> dict:
		return Transform(Transform.PYDANTIC, Transform.DATA, self)

	def to_json(self) -> str:
		'''Return JSON string from deeply serialized dict.'''
		return json.dumps(self.to_dict(), indent=4, ensure_ascii=False)

	@classmethod
	def to_schema(cls) -> dict:
		return Transform(Transform.PYDANTIC, Transform.DEREFERENCED_JSONSCHEMA, cls)

	def __str__(self) -> str:
		'''Default string representation is JSON.'''
		return self.to_json()

	def get_description(self, field: str) -> str:
		'''Return description of a field or empty string.'''
		info = self.model_fields.get(field)
		return info.description or ''