from __future__ import annotations

import uuid

from dapi.lib       import DapiService, DapiException
from dapi.schemas   import OperatorsSchema
from dapi.db		import OperatorRecord


@DapiService.wrap_exceptions()
class FunctionService(DapiService):
	'''Service for managing functions — operators without code, used for static routing.'''

	def __init__(self, dapi):
		self.dapi = dapi

	############################################################################

	def validate_name(self, name: str) -> None:
		if self.dapi.db.get(OperatorRecord, name):
			raise DapiException(status_code=400, detail=f'Function `{name}` already exists', severity=DapiException.BEWARE)

	def require(self, name: str) -> OperatorRecord:
		record = self.dapi.db.get(OperatorRecord, name)
		if not record:
			raise DapiException(status_code=404, detail=f'Function `{name}` does not exist', severity=DapiException.HALT)
		return record

	############################################################################

	async def create(self, schema: OperatorsSchema) -> str:
		self.validate_name(schema.name)

		# Create OperatorRecord record
		record = OperatorRecord(
			id          = str(uuid.uuid4()),
			name        = schema.name,
			description = '',
			scope       = schema.scope or {}
		)
		
		self.dapi.db.add(record)
		self.dapi.db.commit()

		return schema.name

	async def delete(self, name: str) -> None:
		record = self.require(name)
		self.dapi.db.delete(record)
		self.dapi.db.commit()
