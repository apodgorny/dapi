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
	
	def validate_uniqueness(self, name: str, operator: str) -> None:
		"""Check that no transaction exists with the same name and operator."""
		transaction = self.dapi.db.query(TransactionRecord).filter_by(
			name     = name,
			operator = operator
		).first()
		
		if transaction:
			raise DapiException(
				status_code = 400,
				detail      = f'Transaction with name `{name}` for operator `{operator}` already exists',
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
			
		if schema.operator != 'return':
			self.dapi.operator_service.require(schema.operator)
		self.validate_uniqueness(schema.name, schema.operator)

		record = TransactionRecord(
			id          = schema.id,
			name        = schema.name,
			operator    = schema.operator,
			input       = None,
			output      = None
		)
		
		self.dapi.db.add(record)
		self.dapi.db.commit()

		return schema.id

	async def get(self, tx_id: str) -> dict:
		record = self.require(tx_id)
		return record.to_dict()

	async def get_by_name(self, name: str, operator_name: str) -> dict:
		"""Get a transaction by name and operator name."""
		transaction = self.dapi.db.query(TransactionRecord).filter_by(
			name     = name,
			operator = operator_name
		).first()
		
		if not transaction:
			raise DapiException(
				status_code = 404,
				detail      = f'Transaction with name `{name}` for operator `{operator_name}` does not exist',
				severity    = DapiException.HALT
			)
		
		return transaction.to_dict()

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
