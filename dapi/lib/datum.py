from __future__ import annotations

import json
import yaml
import copy

import jsonschema
from typing     import get_args, get_origin, List, Dict, Any, Self
from pydantic   import BaseModel, ValidationError, create_model


class DatumError(Exception):
	def __init__(self, err: ValidationError, model_name='pydantic model'):
		self.err = err
		super().__init__(self.humanize(err, model_name))

	@staticmethod
	def humanize(err: ValidationError, model_name='pydantic model') -> str:
		lines = [f'In {model_name}']
		for e in err.errors():
			var = '.'.join(str(x) for x in e.get('loc', [])) or 'unknown'
			t1  = e.get('type', 'unknown')
			v1  = e.get('input', 'unknown')
			t2  = type(v1).__name__ if v1 != 'unknown' else 'unknown'
			v1  = str(v1)
			if len(v1) > 300:
				v1 = v1[:300] + ' ...'
			if t1 == 'missing':
				line = f'- `{var}`: is missing'
			else:
				line = f'- `{var}`: expected `{t1}`, got `{t2}({v1})`'
			lines.append(line)
		return '\n'.join(lines)


class DatumSchemaError(Exception):
	pass


class Datum:
	BaseModel = BaseModel
	Pydantic  = BaseModel

	############################################################################

	@classmethod
	def is_valid_jsonschema(cls, schema: dict) -> bool:
		try:
			cls.assert_valid_jsonschema(schema)
		except DatumSchemaError:
			return False
		return True

	@classmethod
	def assert_valid_jsonschema(cls, schema: dict) -> None:
		try:
			jsonschema.Draft202012Validator.check_schema(schema)
		except jsonschema.exceptions.SchemaError as exc:
			raise DatumSchemaError(f'Invalid JSON Schema: {exc.message}')

	@classmethod
	def jsonschema_to_basemodel(cls, schema: dict) -> type[BaseModel]:
		title = schema.get('title')
		props = schema.get('properties')

		if not isinstance(title, str)  : raise DatumSchemaError('Schema must have a valid "title"')
		if not isinstance(props, dict) : raise DatumSchemaError('Schema must have a "properties" object')

		map = {
			'boolean' : bool,
			'integer' : int,
			'number'  : float,
			'string'  : str,
		}

		def type(s, path):
			t = s.get('type')
			if t in map      : return map[t]
			if t == 'array'  : return List[type(s.get('items', {}), path + ['Item'])]
			if t == 'object' : return cls.jsonschema_to_basemodel({
				'title'      : '_'.join(path),
				'properties' : s.get('properties', {})
			})
			raise DatumSchemaError(f'Unsupported or missing type for property: {".".join(path)}')

		return create_model(title, **{
			k: (type(s, [title, k]), ...)
			for k, s in props.items()
		})

	@classmethod
	def dereference_schema(cls, schema: dict) -> dict:
		def resolve_refs(obj, defs):
			if isinstance(obj, dict):
				result = {}
				for k, v in obj.items():
					if k == '$defs':
						continue
					elif k == '$ref' and isinstance(v, str) and v.startswith('#/$defs/'):
						def_key = v[len('#/$defs/'):]
						if def_key in defs:
							return resolve_refs(defs[def_key], defs)
					else:
						result[k] = resolve_refs(v, defs)
				return result
			elif isinstance(obj, list):
				return [resolve_refs(i, defs) for i in obj]
			else:
				return obj

		copied = copy.deepcopy(schema)
		defs   = copied.pop('$defs', {})
		return resolve_refs(copied, defs)
		
	############################################################################

	@property
	def schema(self) -> type[BaseModel]:
		return self._schema

	@property
	def model(self) -> BaseModel | None:
		return self._model

	@property
	def title(self) -> str:
		return self.schema.model_json_schema().get('title') or self.schema.__name__

	def is_empty(self) -> bool:
		return self._model is None

	############################################################################

	def __init__(self, source: BaseModel | type[BaseModel] | dict | str | Datum):
		if isinstance(source, Datum):
			source = source.schema

		if isinstance(source, BaseModel):
			self._schema = type(source)
			self._model  = source

		elif isinstance(source, type) and issubclass(source, BaseModel):
			self._schema = source
			self._model  = None

		elif isinstance(source, str):
			schema = json.loads(source)
			Datum.assert_valid_jsonschema(schema)
			self._schema = self.jsonschema_to_basemodel(schema)
			self._model  = None

		elif isinstance(source, dict):
			Datum.assert_valid_jsonschema(source)
			source = Datum.dereference_schema(source)
			self._schema = Datum.jsonschema_to_basemodel(source)
			self._model  = None

		else:
			raise TypeError(f'Expected Pydantic model, type, JSON schema (dict or str), or Datum — got {type(source)}')

	############################################################################

	def validate(self, data:dict):
		datum = Datum(self.schema)
		return datum.from_dict(data).to_dict()

	def to_dict(self, *, schema: bool = False) -> dict:
		if schema:
			# Export schema without $defs by dereferencing
			schema_dict = self.schema.model_json_schema()
			return self.dereference_schema(schema_dict)
		if self._model is None:
			return {}
		return self._model.model_dump(mode='python')

	def from_dict(self, data: dict) -> Datum:
		try:
			self._model = self.schema.model_validate(data)
		except ValidationError as e:
			raise DatumError(e, self.title)
		return self

	def to_json(self, *, schema: bool = False, indent=4) -> str:
		return json.dumps(self.to_dict(schema=schema), indent=indent)

	def from_json(self, json_str: str) -> Datum:
		return self.from_dict(json.loads(json_str))

	def to_yaml(self, *, schema: bool = False) -> str:
		return yaml.dump(self.to_dict(schema=schema), sort_keys=False)

	def from_yaml(self, yaml_str: str) -> Datum:
		return self.from_dict(yaml.safe_load(yaml_str))

	def copy(self, deep: bool = True) -> Datum:
		if self._model is None:
			raise ValueError('No data present')
		copied = copy.deepcopy(self._model) if deep else copy.copy(self._model)
		return Datum(copied)

	def to_empty_dict(self) -> dict:
		schema = Datum.dereference_schema(self.schema.model_json_schema())
		schema = {
			k: v if k != 'required' else None
			for k, v in schema.items()
			if k != 'required'
		}
		schema = json.loads(json.dumps(schema))  # shallow sanitize to remove `None`
		model  = self.jsonschema_to_basemodel(schema)
		def none(fields):
			return {
				k: none(t.model_fields) if hasattr(t := f.annotation, 'model_fields') else
				[] if get_origin(t) is list else
				{} if get_origin(t) is dict else
				None
				for k, f in fields.items()
			}
		return none(model.model_fields)

	def to_empty_json(self, indent: int = 4) -> str:
		return json.dumps(self.to_empty_dict(), indent=indent)

	def to_empty_yaml(self, sort_keys: bool = False) -> str:
		return yaml.dump(self.to_empty_dict(), sort_keys=sort_keys)

	def to_empty_datum(self) -> Datum:
		return Datum(self.schema).from_dict(self.to_empty_dict())

	def to_empty_model(self) -> BaseModel:
		return self.to_empty_datum().model

	def ensure_path(self, accessor: str) -> None:
		'''Ensure that all intermediate keys in accessor path exist and are dicts.'''
		chain     = accessor.split('.')
		data_dict = self.to_dict()
		target    = data_dict
		for key in chain:
			if key not in target or not isinstance(target[key], dict):
				target[key] = {}
			target = target[key]
		self.from_dict(data_dict)

	############################################################################

	def __contains__(self, accessor: str) -> bool:
		try:
			self[accessor]
		except (KeyError, IndexError, TypeError):
			return False
		return True

	def __getitem__(self, accessor: str):
		if not isinstance(accessor, str):
			raise TypeError(f'Accessor must be string, got `{type(accessor).__name__}` in `{accessor}`')
		chain = accessor.split('.')
		value = self.to_dict()
		for attr in chain:
			if isinstance(value, list):
				if attr.isnumeric()     : attr = int(attr)
				else                    : raise KeyError(f'Invalid accessor index: {attr}')
				if attr < len(value)    : value = value[attr]
				else                    : raise IndexError(f'Index out of bounds: {attr}')
			elif isinstance(value, dict):
				if attr in value        : value = value[attr]
				else                    : raise KeyError(f'Invalid accessor key: {attr}')
			else:
				raise TypeError(f'Unsupported structure at {attr}')
		return value

	# def __setitem__(self, accessor: str, new_value):
	# 	if isinstance(new_value, Datum):
	# 		new_value = new_value.to_dict()
	# 	elif isinstance(new_value, BaseModel):
	# 		new_value = Datum(new_value).to_dict()
	# 	chain     = accessor.split('.')
	# 	data_dict = self.to_dict()
	# 	target    = data_dict
	# 	for key in chain[:-1]:
	# 		if key not in target:
	# 			target[key] = {}
	# 		target = target[key]
	# 	target[chain[-1]] = new_value
	# 	self.from_dict(data_dict)

	def __setitem__(self, accessor: str, new_value):
		if isinstance(new_value, Datum):
			new_value = new_value.to_dict()
		elif isinstance(new_value, BaseModel):
			new_value = Datum(new_value).to_dict()

		self.ensure_path('.'.join(accessor.split('.')[:-1]))

		chain     = accessor.split('.')
		data_dict = self.to_dict()
		target    = data_dict
		for key in chain[:-1]:
			target = target[key]
		target[chain[-1]] = new_value
		self.from_dict(data_dict)

	def __repr__(self):
		return f"<Datum[{self.title}]{' — empty' if self.is_empty() else ''}>"

	def __str__(self):
		return self.to_json()