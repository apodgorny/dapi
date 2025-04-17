from __future__ import annotations

import uuid

from dapi.db        import TransactionRecord
from dapi.lib       import DapiService, DapiException
from dapi.schemas   import TransactionSchema, TransactionCreateSchema


@DapiService.wrap_exceptions()
class TransactionService(DapiService):
	'''Service for creating, invoking, and deleting transactions.'''

	def __init__(self, dapi):
		self.dapi = dapi

	############################################################################

	def validate_id(self, tx_id: str) -> None:
		if self.dapi.db.get(TransactionRecord, tx_id):
			raise DapiException(
				status_code = 400,
				detail      = f'Transaction `{tx_id}` already exists',
				severity    = DapiException.BEWARE
			)

	def require(self, tx_id: str) -> TransactionRecord:
		record = self.dapi.db.get(TransactionRecord, tx_id)
		if not record:
			raise DapiException(
				status_code = 404,
				detail      = f'Transaction `{tx_id}` does not exist',
				severity    = DapiException.HALT
			)
		return record

	############################################################################

	async def create(self, schema: TransactionSchema) -> str:
		if not schema.id : schema.id = str(uuid.uuid4())
		else             : self.validate_id(schema.id)
			
		self.dapi.operator_service.require(schema.operator)

		record = TransactionRecord(
			id          = schema.id,
			operator    = schema.operator,
			function_id = schema.function_id or None,
			input       = None,
			output      = None
		)
		
		self.dapi.db.add(record)
		self.dapi.db.commit()

		return schema.id

	async def get(self, tx_id: str) -> dict:
		record = self.require(tx_id)
		return record.to_dict()

	async def get_all(self) -> list[dict]:
		transactions = self.dapi.db.query(TransactionRecord).all()
		return [tx.to_dict() for tx in transactions]

	async def delete(self, tx_id: str) -> None:
		record = self.require(tx_id)
		self.dapi.db.delete(record)
		self.dapi.db.commit()
		
	# async def invoke(self, tx_id: str) -> dict:
	# 	'''Invoke a transaction by ID, using its stored input.'''
	# 	transaction = self.require(tx_id)

	# 	try:
	# 		transaction.output = await self.dapi.operator_service.invoke(
	# 			transaction.operator,
	# 			transaction.input
	# 		)
	# 	except DapiException:
	# 		raise
	# 	except Exception as e:
	# 		raise DapiException(
	# 			status_code = 500,
	# 			detail      = f'Error invoking transaction `{tx_id}`: {str(e)}',
	# 			severity    = DapiException.HALT
	# 		)
	# 	finally:
	# 		self.dapi.db.commit()

	# 	return transaction.output
