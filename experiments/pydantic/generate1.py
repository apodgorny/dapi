from __future__ import annotations
import json

from pydantic				 import BaseModel, create_model, Field
from typing				 import Any, Union, get_args, get_origin
from collections		 import defaultdict


class JsonSchemaToPydanticConverter:
	'''Converts JSON Schema to Pydantic BaseModel classes (resolving $ref and $defs).'''

	def __init__(self, root_schema: dict):
		self.root_schema	= root_schema
		self.models			= {}  # name -> class
		self.defs			= root_schema.get('$defs', {})

	def convert(self, name: str = 'RootModel') -> type[BaseModel]:
		return self._convert_schema(name, self.root_schema)

	############################################################################

	def _convert_schema(self, name: str, schema: dict) -> type[BaseModel]:
		if 'type' not in schema:
			return Any

		typ = schema['type']
		if typ == 'object':
			fields = {}
			required = set(schema.get('required', []))
			for prop_name, prop_schema in schema.get('properties', {}).items():
				resolved_schema	= self._resolve_ref(prop_schema)
				field_type		= self._resolve_type(f'{name}_{prop_name}', resolved_schema)
				field_args		= {}

				if 'description' in resolved_schema:
					field_args['description'] = resolved_schema['description']
				if 'default' in resolved_schema:
					field_args['default'] = resolved_schema['default']
				elif prop_name not in required:
					field_args['default'] = None

				fields[prop_name] = (field_type, Field(**field_args))

			model = create_model(name, **fields)
			self.models[name] = model
			return model

		elif typ == 'array':
			items_schema = self._resolve_ref(schema.get('items', {}))
			item_type = self._resolve_type(f'{name}Item', items_schema)
			return list[item_type]

		elif typ == 'string':
			if 'enum' in schema:
				return Literal[tuple(schema['enum'])]  # noqa: F821
			return str
		elif typ == 'integer':
			return int
		elif typ == 'number':
			return float
		elif typ == 'boolean':
			return bool
		elif typ == 'null':
			return type(None)
		else:
			return Any

	############################################################################

	def _resolve_type(self, name: str, schema: dict) -> Any:
		if '$ref' in schema:
			ref_name = self._ref_to_name(schema['$ref'])
			if ref_name in self.models:
				return self.models[ref_name]
			ref_schema = self.defs.get(ref_name)
			return self._convert_schema(ref_name, ref_schema)
		else:
			return self._convert_schema(name, schema)

	def _resolve_ref(self, schema: dict) -> dict:
		if '$ref' in schema:
			ref_name = self._ref_to_name(schema['$ref'])
			return self.defs.get(ref_name, {})
		return schema

	def _ref_to_name(self, ref: str) -> str:
		assert ref.startswith('#/$defs/')
		return ref.split('/')[-1]

schema = json.loads('{"properties": {"name": {"default": "", "description": "The person\'s name", "title": "Name", "type": "string"}, "sex": {"default": "", "description": "The person\'s biological sex", "title": "Sex", "type": "string"}, "age": {"default": 0, "description": "The person\'s age in years", "title": "Age", "type": "integer"}, "occupation": {"default": "", "description": "The person\'s type of work or hobby", "title": "Occupation", "type": "string"}, "pain": {"default": "", "description": "What causes emotional suffering in this person. Concise.", "title": "Pain", "type": "string"}, "desire": {"default": "", "description": "What this person deeply wants or longs for. Concise.", "title": "Desire", "type": "string"}, "portrait": {"default": "", "description": "Summary of this person\'s personality, values, and inner world. Concise.", "title": "Portrait", "type": "string"}, "look": {"default": "", "description": "A visual description of this person\'s appearance. Concise.", "title": "Look", "type": "string"}, "personality": {"anyOf": [{"description": "Represents the whole psyche as a network of subpersonalities.", "properties": {"subpersonalities": {"default": [], "description": "All inner subpersonalities", "items": {"description": "Represents a coherent internal role composed of harmonized sides from various dualities.", "properties": {"name": {"default": "", "description": "Name or label of the subpersonality", "title": "Name", "type": "string"}, "sides": {"default": [], "description": "List of Side names that make up this subpersonality", "items": {"type": "string"}, "title": "Sides", "type": "array"}}, "title": "Subpersonality", "type": "object"}, "title": "Subpersonalities", "type": "array"}}, "title": "Personality", "type": "object"}, {"type": "null"}], "default": null, "description": "Full psychological structure of this person"}}, "title": "Persona", "type": "object"}')

converter   = JsonSchemaToPydanticConverter(schema)
Model       = converter.convert('MyRoot')

# Сгенерировать экземпляр с полями по умолчанию
instance    = Model()  # поля с default будут заданы, остальные — None / пустые
print(instance.model_dump(mode='python'))