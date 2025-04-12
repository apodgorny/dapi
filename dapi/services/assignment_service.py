from __future__ import annotations

import uuid

from dapi.db        import AssignmentTable
from dapi.lib       import DapiService, DapiException
from dapi.schemas   import AssignmentSchema


@DapiService.wrap_exceptions()
class AssignmentService(DapiService):
	'''Service for creating and managing assignments in transactions.'''

	def __init__(self, dapi):
		self.dapi = dapi

	############################################################################

	def validate_id(self, id: str) -> None:
		if self.dapi.db.get(AssignmentTable, id):
			raise DapiException(status_code=400, detail=f'Assignment `{id}` already exists', severity=DapiException.BEWARE)

	def require(self, id: str) -> AssignmentTable:
		record = self.dapi.db.get(AssignmentTable, id)
		if not record:
			raise DapiException(status_code=404, detail=f'Assignment `{id}` does not exist', severity=DapiException.HALT)
		return record

	############################################################################

	async def create(self, schema: AssignmentSchema) -> AssignmentTable:
		# Generate ID if not provided
		if not schema.id:
			schema.id = str(uuid.uuid4())
		else:
			self.validate_id(schema.id)
			
		# Validate transaction exists
		self.dapi.transaction_service.require(schema.transaction_id)
		
		record = AssignmentTable(**schema.model_dump())
		self.dapi.db.add(record)
		self.dapi.db.commit()
		
		return record

	async def get(self, assign_id: str) -> dict:
		record = self.require(assign_id)
		return record.to_dict()

	async def get_all(self) -> list[dict]:
		return [a.to_dict() for a in self.dapi.db.query(AssignmentTable).all()]

	async def delete(self, assign_id: str) -> None:
		record = self.require(assign_id)
		self.dapi.db.delete(record)
		self.dapi.db.commit()
