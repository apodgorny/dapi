from __future__ import annotations

from fastapi import HTTPException

from dapi.db                    import TransactionTable
from dapi.schemas   import TransactionSchema

# TODO DEBUG AFTER STUPID GPT

class TransactionService:
	'''Service for creating, invoking, and deleting transactions.'''

	def __init__(self, dapi):
		self.dapi = dapi

	############################################################################

	def validate_id(self, tx_id: str) -> None:
		if self.dapi.db.get(TransactionTable, tx_id):
			raise HTTPException(status_code=400, detail=f'Transaction `{tx_id}` already exists')

	def require(self, tx_id: str) -> TransactionTable:
		record = self.dapi.db.get(TransactionTable, tx_id)
		if not record:
			raise HTTPException(status_code=404, detail=f'Transaction `{tx_id}` does not exist')
		return record

	############################################################################

	def create(self, schema: TransactionSchema) -> str:
		self.validate_id(schema.id)
		self.dapi.operator_service.require(schema.operator)

		record = TransactionTable(**schema.model_dump())
		self.dapi.db.add(record)
		self.dapi.db.commit()

		return schema.id

	def get(self, tx_id: str) -> dict:
		record = self.require(tx_id)
		return record.to_dict()

	def get_all(self) -> list[dict]:
		return [tx.to_dict() for tx in self.dapi.db.query(TransactionTable).all()]

	def delete(self, tx_id: str) -> None:
		record = self.require(tx_id)
		self.dapi.db.delete(record)
		self.dapi.db.commit()
