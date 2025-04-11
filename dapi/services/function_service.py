from __future__ import annotations

from fastapi import HTTPException

from dapi.db                   import FunctionTable
from dapi.schemas.function     import FunctionSchema


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

		# Ensure input/output types exist
		if not self.dapi.type_service.has(schema.input_type):
			raise HTTPException(status_code=404, detail=f'Type `{schema.input_type}` does not exist')
		if not self.dapi.type_service.has(schema.output_type):
			raise HTTPException(status_code=404, detail=f'Type `{schema.output_type}` does not exist')

		record = FunctionTable(**schema.model_dump())
		self.dapi.db.add(record)
		self.dapi.db.commit()

		return schema.name

	def delete(self, name: str) -> None:
		record = self.require(name)
		self.dapi.db.delete(record)
		self.dapi.db.commit()
