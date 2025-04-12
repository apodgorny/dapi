from __future__ import annotations

import uuid

from dapi.db        import TransactionTable
from dapi.lib       import DapiService, DapiException
from dapi.schemas   import TransactionSchema, TransactionCreateSchema


@DapiService.wrap_exceptions()
class TransactionService(DapiService):
	'''Service for creating, invoking, and deleting transactions.'''

	def __init__(self, dapi):
		self.dapi = dapi

	############################################################################

	def validate_id(self, tx_id: str) -> None:
		if self.dapi.db.get(TransactionTable, tx_id):
			raise DapiException(status_code=400, detail=f'Transaction `{tx_id}` already exists', severity=DapiException.BEWARE)

	def require(self, tx_id: str) -> TransactionTable:
		record = self.dapi.db.get(TransactionTable, tx_id)
		if not record:
			raise DapiException(status_code=404, detail=f'Transaction `{tx_id}` does not exist', severity=DapiException.HALT)
		return record

	############################################################################

	async def create(self, schema: TransactionSchema) -> str:
		# Generate ID if not provided
		if not schema.id:
			schema.id = str(uuid.uuid4())
		else:
			self.validate_id(schema.id)
			
		self.dapi.operator_service.require(schema.operator)

		# For now, we'll use fixed values since the DB schema requires these fields
		record = TransactionTable(
			id=schema.id,
			operator=schema.operator,
			function_id="default",  # Default value until function support is fully implemented
			position=0,             # Default position
			input=None,             # Will be populated later via assignments
			output=None             # Will be populated after invocation
		)
		
		self.dapi.db.add(record)
		self.dapi.db.commit()

		return schema.id

	async def get(self, tx_id: str) -> dict:
		record = self.require(tx_id)
		return record.to_dict()

	async def get_all(self) -> list[dict]:
		transactions = self.dapi.db.query(TransactionTable).all()
		return [tx.to_dict() for tx in transactions]
		
	async def invoke(self, tx_name: str, input_data: dict) -> dict:
		"""Invoke a transaction by ID, executing its associated operator"""
		if not tx_name:
			raise DapiException(status_code=400, detail="Transaction name cannot be empty")
			
		transaction = self.require(tx_name)
		
		# Get the operator associated with this transaction
		operator_name = transaction.operator
		
		# Update transaction input with provided data
		transaction.input = input_data
		self.dapi.db.commit()
		
		try:
			# Invoke the operator
			result = await self.dapi.operator_service.invoke(operator_name, input_data)
			
			# Update the transaction with the result
			transaction.output = result
			self.dapi.db.commit()
			
			# Return the result
			return result
			
		except DapiException:
			# Pass through DapiExceptions
			transaction.input = None
			self.dapi.db.commit()
			raise
		except Exception as e:
			# If anything goes wrong, clean up the transaction data and provide a detailed error
			transaction.input = None
			self.dapi.db.commit()
			raise DapiException(status_code=500, detail=f"Error invoking transaction: {str(e)}", severity=DapiException.HALT)

	async def delete(self, tx_id: str) -> None:
		record = self.require(tx_id)
		self.dapi.db.delete(record)
		self.dapi.db.commit()
