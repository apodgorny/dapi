import json
from uuid      import uuid4
from datetime  import datetime

from sqlalchemy.orm                 import Session
from dapi.db                        import OperatorInstanceRecord, OperatorInstanceStatus, TransactionRecord, OperatorRecord
from dapi.schemas                   import OperatorInstanceSchema, OperatorScopeSchema
from dapi.services.operator_service import OperatorService
from dapi.lib                       import Datum, DapiService, Interpreter


@DapiService.wrap_exceptions()
class InstanceService(DapiService):

	async def _set_status(self, instance, status, error=None):
		if status == OperatorInstanceStatus.invoked:
			instance.invoked_at = datetime.utcnow()
		if status == OperatorInstanceStatus.error:
			instance.error  = str(error)
		instance.status = status
		self.dapi.db.commit()

	async def _invoke_atomic(self, instance: OperatorInstanceRecord, operator):
		interpreter  = await self.dapi.interpreter_service.require(operator.interpreter)
		datum_input  = await self.dapi.operator_service.get_input_datum(operator.name)
		datum_output = await self.dapi.operator_service.get_output_datum(operator.name)

		result = await interpreter.invoke(
			operator_name = operator.name,
			code          = operator.code,
			input         = datum_input.from_dict(instance.input),
			output        = datum_output,
			config        = operator.config
		)

		instance.output = result.to_dict()
		self.dapi.db.commit()

	async def _invoke_composite(self, instance: OperatorInstanceRecord, operator: OperatorRecord):
		if not (transactions := operator.transactions):
			raise ValueError(f'Function operator `{operator.name}` has no transactions defined.')

		scope = Datum(OperatorScopeSchema)
		scope['this.input']  = instance.input
		scope['this.output'] = instance.output

		children_ids = []
		for tx_id in transactions:
			if not (tx := self.dapi.db.get(TransactionRecord, tx_id)):
				raise ValueError(f'Transaction `{tx_id}` not found')

			if child_id := await self.dapi.transaction_service.invoke(scope, tx):
				children_ids.append(child_id)

		instance.children = children_ids
		instance.output   = scope['this.output']

	async def create(self, operator_name: str, instance_name: str = None, input_data: dict = {}) -> OperatorInstanceSchema:
		instance_id = str(uuid4())
		instance = OperatorInstanceRecord(
			id         = instance_id,
			name       = instance_name or instance_id,
			operator   = operator_name,
			input      = input_data,
			output     = {},
			children   = [],
			status     = OperatorInstanceStatus.created,
			error      = None,
			created_at = datetime.utcnow(),
			invoked_at = None,
		)

		self.dapi.db.add(instance)
		self.dapi.db.commit()
		self.dapi.db.refresh(instance)

		return OperatorInstanceSchema.model_validate(instance.to_dict())

	async def invoke(self, instance_id: str) -> OperatorInstanceSchema:
		instance = self.dapi.db.query(OperatorInstanceRecord).get(instance_id)
		if not instance:
			raise ValueError(f'Instance `{instance_id}` not found')

		operator     = self.dapi.operator_service.require(instance.operator)
		is_composite = operator.interpreter == 'function'

		await self._set_status(instance, OperatorInstanceStatus.running)

		try:
			if is_composite:
				await self._invoke_composite(instance, operator)
			else:
				await self._invoke_atomic(instance, operator)

			await self._set_status(instance, OperatorInstanceStatus.invoked)
		except Exception as e:
			await self._set_status(instance, OperatorInstanceStatus.error, e)
			raise

		self.dapi.db.commit()
		self.dapi.db.refresh(instance)
		return OperatorInstanceSchema.model_validate(instance.to_dict())

	async def get(self, instance_id: str) -> OperatorInstanceSchema:
		instance = self.dapi.db.query(OperatorInstanceRecord).get(instance_id)
		if not instance:
			raise ValueError(f'Instance `{instance_id}` not found')
		return OperatorInstanceSchema.model_validate(instance.to_dict())

	async def delete(self, instance_id: str) -> None:
		instance = self.dapi.db.query(OperatorInstanceRecord).get(instance_id)
		if not instance:
			raise ValueError(f'Instance `{instance_id}` not found')
		self.dapi.db.delete(instance)
		self.dapi.db.commit()
