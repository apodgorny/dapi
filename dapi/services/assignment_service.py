from __future__ import annotations

import uuid

from dapi.db        import AssignmentRecord
from dapi.lib       import DapiService, DapiException
from dapi.schemas   import AssignmentSchema


@DapiService.wrap_exceptions()
class AssignmentService(DapiService):
	'''Service for creating and managing assignments in transactions.'''

	def validate_id(self, id: str) -> None:
		if self.dapi.db.get(AssignmentRecord, id):
			raise DapiException(
				status_code = 400,
				detail      = f'Assignment `{id}` already exists',
				severity    = DapiException.BEWARE
			)

	def require(self, id: str) -> AssignmentRecord:
		record = self.dapi.db.get(AssignmentRecord, id)
		if not record:
			raise DapiException(
				status_code = 404,
				detail      = f'Assignment `{id}` does not exist',
				severity    = DapiException.HALT
			)
		return record

	############################################################################

	def validate_unique_assignment(self, transaction_id: str, l_accessor: str, r_accessor: str, exclude_id: str = None) -> None:
		"""Validate that the combination of transaction_id, l_accessor, and r_accessor is unique."""
		query = self.dapi.db.query(AssignmentRecord).filter(
			AssignmentRecord.transaction_id == transaction_id,
			AssignmentRecord.l_accessor == l_accessor,
			AssignmentRecord.r_accessor == r_accessor
		)
		
		if exclude_id:
			query = query.filter(AssignmentRecord.id != exclude_id)
			
		existing = query.first()
		if existing:
			raise DapiException(
				status_code = 400,
				detail      = f'Assignment with transaction_id={transaction_id}, l_accessor={l_accessor}, r_accessor={r_accessor} already exists',
				severity    = DapiException.BEWARE
			)

	async def create(self, schema: AssignmentSchema) -> AssignmentRecord:
		# Generate ID if not provided
		if not schema.id:
			schema.id = str(uuid.uuid4())
		else:
			self.validate_id(schema.id)
			
		# Validate transaction exists
		self.dapi.transaction_service.require(schema.transaction_id)
		
		# Validate uniqueness of transaction_id, l_accessor, r_accessor combination
		self.validate_unique_assignment(
			transaction_id = schema.transaction_id,
			l_accessor     = schema.l_accessor,
			r_accessor     = schema.r_accessor
		)
		
		record = AssignmentRecord(**schema.model_dump())
		self.dapi.db.add(record)
		self.dapi.db.commit()
		
		return record

	async def get(self, assign_id: str) -> dict:
		record = self.require(assign_id)
		return record.to_dict()

	async def get_all(self) -> list[dict]:
		return [a.to_dict() for a in self.dapi.db.query(AssignmentRecord).all()]

	async def delete(self, assign_id: str) -> None:
		record = self.require(assign_id)
		self.dapi.db.delete(record)
		self.dapi.db.commit()
