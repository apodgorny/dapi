from __future__ import annotations

from dapi.db        import TypeTable
from dapi.lib       import DatumSchemaError, Datum, DapiException, DapiService


@DapiService.wrap_exceptions({DatumSchemaError: (422, 'halt')})
class TypeService(DapiService):
	'''Service for managing JSON Schema types via SQLAlchemy.'''

	def __init__(self, dapi):
		self.dapi = dapi

	############################################################################

	def validate_name(self, name: str) -> None:
		if self.dapi.db.get(TypeTable, name):
			raise DapiException(status_code=400, detail=f'Type `{name}` already exists', severity=DapiException.BEWARE)

	def validate_jsonschema(self, schema):
		try:
			Datum.assert_valid_jsonschema(schema)
		except DatumSchemaError as exc:
			raise DapiException(status_code=422, detail=str(exc))

	def require(self, name: str) -> TypeTable:
		if not name:
			raise DapiException(status_code=400, detail=f'Type name cannot be empty')
		record = self.dapi.db.get(TypeTable, name)
		if not record:
			raise DapiException(status_code=404, detail=f'Type `{name}` does not exist')
		return record

	############################################################################

	async def has(self, name: str) -> bool:
		return bool(self.dapi.db.get(TypeTable, name))

	async def create(self, name: str, schema: dict) -> str:
		self.validate_name(name)
		self.validate_jsonschema(schema)

		record = TypeTable(name=name, schema=schema)

		self.dapi.db.add(record)
		self.dapi.db.commit()
		return name

	async def get(self, name: str) -> dict:
		record = self.require(name)
		return {'name': record.name, 'schema': record.schema}

	async def get_all(self) -> list[dict]:
		types = self.dapi.db.query(TypeTable).all()
		return [{'name': t.name, 'schema': t.schema} for t in types]

	async def delete(self, name: str) -> None:
		record = self.require(name)
		self.dapi.db.delete(record)
		self.dapi.db.commit()
