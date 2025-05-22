import copy
from typing import Any, get_args, get_origin, Union, List, Dict

from pydantic import BaseModel, create_model
from pydantic.fields import FieldInfo
from sqlalchemy import Table, Column, MetaData, Integer, String

from .t import T


T.PYDANTIC(BaseModel)
T.JSONSCHEMA(dict)
T.DEREFERENCED_JSONSCHEMA(dict)
T.DATA()
T.ARGUMENTS(None)
T.SQLALCHEMY_TABLE(object)
T.PROMPT(str)
T.FIELD(FieldInfo)
T.TYPE(str)
T.STRING(str)


@T.register(T.PYDANTIC, T.JSONSCHEMA)
def model_to_schema(model: type[BaseModel]) -> dict:
	return model.model_json_schema()


@T.register(T.PYDANTIC, T.DATA)
def model_to_data(obj):
	if isinstance(obj, BaseModel):
		return {k: model_to_data(v) for k, v in obj.model_dump().items()}
	elif isinstance(obj, dict):
		return {k: model_to_data(v) for k, v in obj.items()}
	elif isinstance(obj, (list, tuple, set)):
		return [model_to_data(v) for v in obj]
	else:
		return obj

@T.register(T.JSONSCHEMA, T.DEREFERENCED_JSONSCHEMA)
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
	

@T.register(T.DATA, T.ARGUMENTS)
def data_to_arguments(data):
	if isinstance(data, list):
		return data
	elif isinstance(data, dict):
		args = tuple(data[k] for k in data)
		if len(args) == 1:
			args = args[0]
	return args


@T.register(T.PYDANTIC, T.SQLALCHEMY_TABLE)
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


@T.register(T.SQLALCHEMY_TABLE, T.PYDANTIC)
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

@T.register(T.TYPE, T.STRING)
def type_to_string(tp: Any) -> str:
	origin = get_origin(tp)
	args   = get_args(tp)

	if origin is Union and type(None) in args:
		non_none = [a for a in args if a is not type(None)]
		return T(T.TYPE, T.STRING, non_none[0])

	if origin in (list, List):
		item_type = args[0] if args else Any
		item_str  = T(T.TYPE, T.STRING, item_type)
		return f'List[{item_str}]'

	if origin in (dict, Dict):
		key_type   = args[0] if args else Any
		value_type = args[1] if len(args) > 1 else Any
		key_str    = T(T.TYPE, T.STRING, key_type)
		val_str    = T(T.TYPE, T.STRING, value_type)
		return f'Dict[{key_str}, {val_str}]'

	if hasattr(tp, '__name__'):
		return tp.__name__

	return str(tp)

@T.register(T.TYPE, T.PROMPT)
def type_to_prompt(tp: Any, indent: int = 0) -> str:
	origin = get_origin(tp)
	args   = get_args(tp)

	# Optional[X]
	if origin is Union and type(None) in args:
		non_none = [a for a in args if a is not type(None)]
		return T(T.TYPE, T.PROMPT, non_none[0], indent)

	# List[T] (with recursive support)
	if origin in (list, List):
		item_type = args[0] if args else Any
		if hasattr(item_type, 'model_fields'):
			body   = T(T.TYPE, T.PROMPT, item_type, indent + 1)
			pad    = '  ' * (indent + 1)
			lines  = body.splitlines()
			indented = '\n'.join(pad + line for line in lines)
			return '[\n' + indented + '\n' + '  ' * indent + ', ... ]'
		else:
			type_str = T(T.TYPE, T.STRING, item_type)
			return f'[ {type_str} ]'

	# Dict[...] (fallback only)
	if origin in (dict, Dict):
		key_type   = args[0] if args else Any
		value_type = args[1] if len(args) > 1 else Any
		key_name   = T(T.TYPE, T.STRING, key_type)
		val_str    = T(T.TYPE, T.PROMPT, value_type, indent + 1)
		return f'{{ "{key_name}": {val_str} }}'

	# Submodel
	if hasattr(tp, 'model_fields'):
		return T(T.PYDANTIC, T.PROMPT, tp, indent)

	return T(T.TYPE, T.STRING, tp)


@T.register(T.FIELD, T.PROMPT)
def field_to_prompt(field: FieldInfo, indent: int = 0) -> str:
	comment = f'  # {field.description}' if field.description else ''
	value   = T(T.TYPE, T.PROMPT, field.annotation, indent + 1)
	pad     = '  ' * indent
	return f'{pad}"{field.title}": {value}{comment}'


@T.register(T.PYDANTIC, T.PROMPT)
def pydantic_to_prompt(model_cls: type[BaseModel], indent: int = 0) -> str:
	lines = []
	pad = '  ' * indent
	lines.append(pad + '{')
	for name, field in model_cls.model_fields.items():
		field.title = name
		lines.append(T(T.FIELD, T.PROMPT, field, indent + 1))
	lines.append(pad + '}')
	return '\n'.join(lines)
