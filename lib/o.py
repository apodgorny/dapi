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
	def prompt(cls) -> str:
		lines = []

		def render(model_cls: type[BaseModel], indent=0, desc: str | None = None):
			desc = desc or ''
			pad = '  ' * indent
			lines.append(pad + '{')

			for name, field in model_cls.model_fields.items():
				field_type = field.annotation
				c_desc     = field.description
				key_str    = f'{pad}  "{name}": '
				value      = render_type(field_type, indent + 1)
				comment    = f'  # {c_desc}' if c_desc else ''
				lines.append(key_str + value + comment)

			lines.append(pad + '}')

		def render_type(tp, indent=0) -> str:
			origin = getattr(tp, '__origin__', None)
			args   = getattr(tp, '__args__', ())

			# Optional[X]
			if origin is Union and type(None) in args:
				non_none = [a for a in args if a is not type(None)]
				return render_type(non_none[0], indent)

			if hasattr(tp, 'model_fields'):  # it's a BaseModel subclass
				sub_lines = ['{']
				for name, field in tp.model_fields.items():
					c_desc  = field.description
					key_str = '  ' * (indent + 1) + f'"{name}": '
					value   = render_type(field.annotation, indent + 1)
					comment = f'  # {c_desc}' if c_desc else f''
					sub_lines.append(key_str + value + comment)
				sub_lines.append('  ' * indent + '}')
				return '\n'.join(sub_lines)

			elif origin in (list, List):
				item_type = args[0] if args else Any
				if hasattr(item_type, 'model_fields'):
					inner = render_type(item_type, indent + 1)
					return '[\n' + inner + '\n' + '  ' * indent + ', ... ]'
				else:
					return f'[ {get_typename(item_type)} ]'

			elif origin in (dict, Dict):
				return '{...}'

			return get_typename(tp)

		def get_typename(tp) -> str:
			if tp in (str,):
				return 'str'
			if tp in (int,):
				return 'int'
			if tp in (float,):
				return 'float'
			if tp in (bool,):
				return 'bool'
			if tp in (dict,):
				return 'dict'
			if tp in (list,):
				return 'list'
			if hasattr(tp, '__name__'):
				return tp.__name__
			return 'Any'

		render(cls)
		return '\n'.join(lines)

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

	@classmethod
	def from_dict(cls, data: dict) -> 'O':
		'''Create instance from dict, with nested O reconstruction.'''
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

	@classmethod
	def from_disk(cls, path: str):
		with open(path, 'r', encoding='utf-8') as f:
			obj   = json.load(f)
			Model = jscpy(obj['schema'])
			return Model(**obj['data'])

	def to_disk(self, path: str):
		if os.path.isdir(path):
			filename = f'{self.__class__.__name__}.json'
			path     = os.path.join(path, filename)

		with open(path, 'w', encoding='utf-8') as f:
			json.dump({
				'schema': self.model_json_schema(),
				'data'  : self.model_dump()
			}, f, indent=4, ensure_ascii=False)

