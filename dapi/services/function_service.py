from __future__ import annotations

from fastapi import HTTPException
import uuid

from dapi.db     import FunctionTable
from dapi.schemas import FunctionSchema


class FunctionService:
	'''Service for managing functions — operators without code, used for static routing.'''

	def __init__(self, dapi):
		self.dapi = dapi

	############################################################################

	def validate_name(self, name: str) -> None:
		if self.dapi.db.get(FunctionTable, name):
			raise HTTPException(status_code=400, detail=f'Function `{name}` already exists')

	def require(self, name: str) -> FunctionTable:
		record = self.dapi.db.get(FunctionTable, name)
		if not record:
			raise HTTPException(status_code=404, detail=f'Function `{name}` does not exist')
		return record

	############################################################################

	def create(self, schema: FunctionSchema) -> str:
		self.validate_name(schema.name)

		# Create FunctionTable record
		record = FunctionTable(
			id=str(uuid.uuid4()),
			name=schema.name,
			description="",
			scope=schema.scope or {}
		)
		
		self.dapi.db.add(record)
		self.dapi.db.commit()

		return schema.name

	def delete(self, name: str) -> None:
		record = self.require(name)
		self.dapi.db.delete(record)
		self.dapi.db.commit()
