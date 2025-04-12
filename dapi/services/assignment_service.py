from __future__ import annotations

from fastapi import HTTPException
import uuid

from dapi.db import AssignmentTable
from dapi.schemas import AssignmentSchema


class AssignmentService:
	'''Service for creating and managing assignments in transactions.'''

	def __init__(self, dapi):
		self.dapi = dapi

	############################################################################

	def validate_id(self, assign_id: str) -> None:
		if self.dapi.db.get(AssignmentTable, assign_id):
			raise HTTPException(status_code=400, detail=f'Assignment `{assign_id}` already exists')

	def require(self, assign_id: str) -> AssignmentTable:
		record = self.dapi.db.get(AssignmentTable, assign_id)
		if not record:
			raise HTTPException(status_code=404, detail=f'Assignment `{assign_id}` does not exist')
		return record

	############################################################################

	def create(self, schema: AssignmentSchema) -> AssignmentTable:
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

	def get(self, assign_id: str) -> dict:
		record = self.require(assign_id)
		return record.to_dict()

	def get_all(self) -> list[dict]:
		return [a.to_dict() for a in self.dapi.db.query(AssignmentTable).all()]

	def delete(self, assign_id: str) -> None:
		record = self.require(assign_id)
		self.dapi.db.delete(record)
		self.dapi.db.commit()
