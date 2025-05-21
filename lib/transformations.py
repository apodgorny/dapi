import copy
from typing import Any, get_args, get_origin, Union, List, Dict

from pydantic import BaseModel, create_model
from pydantic.fields import FieldInfo
from sqlalchemy import Table, Column, MetaData, Integer, String

from .transform import Transform


Transform.PYDANTIC(BaseModel)
Transform.JSONSCHEMA(dict)
Transform.DEREFERENCED_JSONSCHEMA(dict)
Transform.DATA()
Transform.ARGUMENTS(None)
Transform.SQLALCHEMY_TABLE(object)
Transform.PROMPT(str)
Transform.FIELD(FieldInfo)
Transform.TYPE(str)
Transform.STRING(str)


@Transform.register(Transform.PYDANTIC, Transform.JSONSCHEMA)
def model_to_schema(model: type[BaseModel]) -> dict:
	return model.model_json_schema()


@Transform.register(Transform.PYDANTIC, Transform.DATA)
def model_to_data(obj):
	if isinstance(obj, BaseModel):
		return {k: model_to_data(v) for k, v in obj.model_dump().items()}
	elif isinstance(obj, dict):
		return {k: model_to_data(v) for k, v in obj.items()}
	elif isinstance(obj, (list, tuple, set)):
		return [model_to_data(v) for v in obj]
	else:
		return obj

@Transform.register(Transform.JSONSCHEMA, Transform.DEREFERENCED_JSONSCHEMA)
def dereference_schema(schema: dict) -> dict:
	def resolve_refs(obj, defs):
		if isinstance(obj, dict):
			if '$ref' in obj:
				ref_name = obj['$ref'].split('/')[-1]
				
				# Try from $defs
				if ref_name in defs:
					return resolve_refs(defs[ref_name], defs)

				# Try from globals (must be a Pydantic model)
				if ref_name in globals():
					ref_cls = globals()[ref_name]
					if hasattr(ref_cls, 'model_json_schema'):
						return resolve_refs(ref_cls.model_json_schema(), defs)

				# Fallback: raise error
				raise TypeError(f'Referenced type `{ref_name}` not found in $defs or globals()')

			return {k: resolve_refs(v, defs) for k, v in obj.items()}

		elif isinstance(obj, list):
			return [resolve_refs(item, defs) for item in obj]

		else:
			return obj

	copied = copy.deepcopy(schema)
	defs   = copied.pop('$defs', {})
	return resolve_refs(copied, defs)
	

@Transform.register(Transform.DATA, Transform.ARGUMENTS)
def data_to_arguments(data):
	if isinstance(data, list):
		return data
	elif isinstance(data, dict):
		args = tuple(data[k] for k in data)
		if len(args) == 1:
			args = args[0]
	return args


@Transform.register(Transform.PYDANTIC, Transform.SQLALCHEMY_TABLE)
def pydantic_to_table(model: type[BaseModel]) -> Table:
	metadata = MetaData()
	columns  = []

	for name, field in model.model_fields.items():
		ftype = field.annotation
		sql_type = (
			Integer if ftype is int else
			String  if ftype is str else
			String  # fallback for now
		)
		columns.append(
			Column(name, sql_type, primary_key=(name == 'id'))
		)

	return Table(model.__name__.lower(), metadata, *columns)


@Transform.register(Transform.SQLALCHEMY_TABLE, Transform.PYDANTIC)
def table_to_model(table: Table) -> type[BaseModel]:
	fields = {}

	for col in table.columns:
		# crude type mapping
		if isinstance(col.type, Integer):
			py_type = int
		elif isinstance(col.type, String):
			py_type = str
		else:
			py_type = str  # fallback

		# required if not nullable and no default
		required = col.nullable is False and col.default is None and not col.autoincrement
		default = ... if required else None

		fields[col.name] = (py_type, default)

	model_name = ''.join(word.capitalize() for word in table.name.split('_')) + 'Model'
	return create_model(model_name, **fields)


######################################## TYPE ########################################

@Transform.register(Transform.TYPE, Transform.STRING)
def type_to_string(tp: Any) -> str:
	origin = get_origin(tp)
	args   = get_args(tp)

	if origin is Union and type(None) in args:
		non_none = [a for a in args if a is not type(None)]
		return Transform(Transform.TYPE, Transform.STRING, non_none[0])

	if origin in (list, List):
		item_type = args[0] if args else Any
		item_str  = Transform(Transform.TYPE, Transform.STRING, item_type)
		return f'List[{item_str}]'

	if origin in (dict, Dict):
		key_type   = args[0] if args else Any
		value_type = args[1] if len(args) > 1 else Any
		key_str    = Transform(Transform.TYPE, Transform.STRING, key_type)
		val_str    = Transform(Transform.TYPE, Transform.STRING, value_type)
		return f'Dict[{key_str}, {val_str}]'

	if hasattr(tp, '__name__'):
		return tp.__name__

	return str(tp)

@Transform.register(Transform.TYPE, Transform.PROMPT)
def type_to_prompt(tp: Any, indent: int = 0) -> str:
	origin = get_origin(tp)
	args   = get_args(tp)

	# Optional[X]
	if origin is Union and type(None) in args:
		non_none = [a for a in args if a is not type(None)]
		return Transform(Transform.TYPE, Transform.PROMPT, non_none[0], indent)

	# List[T] (with recursive support)
	if origin in (list, List):
		item_type = args[0] if args else Any
		if hasattr(item_type, 'model_fields'):
			body   = Transform(Transform.TYPE, Transform.PROMPT, item_type, indent + 1)
			pad    = '  ' * (indent + 1)
			lines  = body.splitlines()
			indented = '\n'.join(pad + line for line in lines)
			return '[\n' + indented + '\n' + '  ' * indent + ', ... ]'
		else:
			type_str = Transform(Transform.TYPE, Transform.STRING, item_type)
			return f'[ {type_str} ]'

	# Dict[...] (fallback only)
	if origin in (dict, Dict):
		key_type   = args[0] if args else Any
		value_type = args[1] if len(args) > 1 else Any
		key_name   = Transform(Transform.TYPE, Transform.STRING, key_type)
		val_str    = Transform(Transform.TYPE, Transform.PROMPT, value_type, indent + 1)
		return f'{{ "{key_name}": {val_str} }}'

	# Submodel
	if hasattr(tp, 'model_fields'):
		return Transform(Transform.PYDANTIC, Transform.PROMPT, tp, indent)

	return Transform(Transform.TYPE, Transform.STRING, tp)


@Transform.register(Transform.FIELD, Transform.PROMPT)
def field_to_prompt(field: FieldInfo, indent: int = 0) -> str:
	comment = f'  # {field.description}' if field.description else ''
	value   = Transform(Transform.TYPE, Transform.PROMPT, field.annotation, indent + 1)
	pad     = '  ' * indent
	return f'{pad}"{field.title}": {value}{comment}'


@Transform.register(Transform.PYDANTIC, Transform.PROMPT)
def pydantic_to_prompt(model_cls: type[BaseModel], indent: int = 0) -> str:
	lines = []
	pad = '  ' * indent
	lines.append(pad + '{')
	for name, field in model_cls.model_fields.items():
		field.title = name
		lines.append(Transform(Transform.FIELD, Transform.PROMPT, field, indent + 1))
	lines.append(pad + '}')
	return '\n'.join(lines)
