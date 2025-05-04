from __future__    import annotations

import json

from typing        import Any, Dict, List, Optional

from dapi.db       import TypeRecord
from dapi.schemas  import TypeSchema
from dapi.lib      import DapiService, DapiException, O, jscpy


@DapiService.wrap_exceptions()
class TypeService(DapiService):
	'''Stores and manages type definitions as schema + code.'''

	def _get_type_globals(self):
		return {
			'O'        : O,
			'Optional' : Optional,
			'List'     : List,
			'Dict'     : Dict
		}

	async def initialize(self):
		await super().initialize()

	async def create(self, schema: TypeSchema):
		if not schema.name:
			raise DapiException.halt('Missing type name')

		existing = self.dapi.db.get(TypeRecord, schema.name)
		if existing:
			self.dapi.db.delete(existing)

		self.dapi.db.add(TypeRecord(
			name        = schema.name,
			description = schema.description,
			code        = schema.code,
			type_schema = schema.type_schema
		))
		self.dapi.db.commit()

		return schema

	async def get(self, name: str) -> TypeSchema:
		record = self.dapi.db.get(TypeRecord, name)
		if not record:
			raise DapiException.halt(f'Type `{name}` not found')
		return TypeSchema(**record.to_dict())

	async def get_all(self) -> list[TypeSchema]:
		records = self.dapi.db.query(TypeRecord).all()
		return [TypeSchema(**r.to_dict()) for r in records]

	async def delete(self, name: str):
		record = self.dapi.db.get(TypeRecord, name)
		if record:
			self.dapi.db.delete(record)
			self.dapi.db.commit()

	async def delete_all(self):
		self.dapi.db.query(TypeRecord).delete()
		self.dapi.db.commit()

	def get_class(self, name: str):
		record = self.dapi.db.get(TypeRecord, name)
		if not record:
			raise DapiException.halt(f'Type `{name}` not found')

		schema_dict = record.type_schema
		model_cls   = jscpy(schema_dict, base_class=O)
		return model_cls

	def get_all_classes(self) -> dict[str, type]:
		classes = {}
		records = self.dapi.db.query(TypeRecord).all()
		for r in records:
			classes[r.name] = jscpy(r.type_schema, base_class=O)
			# print('= '*20)
			# print('---', r.name, '---')
			# print(json.dumps(classes[r.name].model_json_schema(), indent=4))
			# print('= '*20)
		return classes
