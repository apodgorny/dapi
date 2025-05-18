import copy

from pydantic import BaseModel

from .transform import Transform


Transform.PYDANTIC(BaseModel)
Transform.JSONSCHEMA(dict)
Transform.DEREFERENCED_JSONSCHEMA(dict)
Transform.DATA()
Transform.ARGUMENTS(None)


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
				raise DatumSchemaError(f'Referenced type `{ref_name}` not found in $defs or globals()')

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