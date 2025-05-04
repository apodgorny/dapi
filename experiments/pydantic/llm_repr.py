from pydantic import BaseModel, Field
from typing   import Any, get_args, Union, List, Dict

class O(BaseModel):
	@classmethod
	def Field(cls, default=None, *, description=None):
		return Field(default, description=description)

	def __str__(self) -> str:
		'''Render current object values as JSON, including nested O structures.'''
		def serialize(val):
			if isinstance(val, O):
				return json.loads(str(val))
			elif isinstance(val, (list, tuple)):
				return [serialize(i) for i in val]
			return val

		result = {
			k: serialize(getattr(self, k))
			for k in self.model_fields
		}
		return json.dumps(result, indent=4, ensure_ascii=False)


	def walk(self, f):
		def visit(val: Any, path: list[str], hint: Any = None):
			desc = None
			if isinstance(val, BaseModel) and path:
				field = val.__class__.model_fields.get(path[-1])
				if field:
					desc = field.description

			f(path, type(val), val, desc)

			if isinstance(val, BaseModel):
				for name, field in val.model_fields.items():
					visit(getattr(val, name), path + [name], field.annotation)

			elif isinstance(val, list):
				item_type = get_args(hint)[0] if hint else None
				for i, item in enumerate(val):
					visit(item, path + [str(i)], item_type)

			elif isinstance(val, dict):
				val_type = get_args(hint)[1] if hint and len(get_args(hint)) == 2 else None
				for k, v in val.items():
					visit(v, path + [str(k)], val_type)

		visit(self, [])

	@classmethod
	def as_llm_schema(cls) -> str:
		lines = []

		def render(model_cls: type[BaseModel], indent=0, desc: str | None = None):
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
					comment = f'  # {c_desc}' if c_desc else ''
					sub_lines.append(key_str + value + comment)
				sub_lines.append('  ' * indent + '}')
				return '\n'.join(sub_lines)

			elif origin in (list, List):
				item_type = args[0] if args else Any
				if hasattr(item_type, 'model_fields'):
					inner = render_type(item_type, indent + 1)
					return '[\n' + inner + '\n' + '  ' * indent + '  ... ]'
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
		'''Return object as dict (non-recursive).'''
		return self.model_dump()

	def get_description(self, field: str) -> str:
		'''Return description of a field or empty string.'''
		info = self.model_fields.get(field)
		return info.description or ''







class Address(O):
	city: str = Field(..., description='City of residence')
	zip : int = Field(..., description='Postal code')

class Tag(O):
	name     : str = Field(..., description='Tag name')
	priority : int = Field(..., description='Tag priority')

class User(O):
	name    : str              = Field(..., description='Full name')
	address : Address          = Field(..., description='Current address')
	tags    : list[Tag]        = Field(..., description='List of user tags')
	notes   : dict[str, int]   = Field(..., description='Arbitrary numeric notes')

# user = User(
# 	name='Alice',
# 	address=Address(city='Kyiv', zip=12345),
# 	tags=[
# 		Tag(name='admin', priority=1),
# 		Tag(name='beta',  priority=2)
# 	],
# 	notes={'score': 10, 'year': 2025}
# )

print(User.as_llm_schema())
