import json
from uuid      import uuid4
from datetime  import datetime

from sqlalchemy.orm                 import Session
from dapi.db                        import OperatorInstanceRecord, OperatorInstanceStatus, OperatorRecord
from dapi.schemas                   import OperatorInstanceSchema
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

		print(instance.operator, interpreter)
		result = await interpreter.invoke(
			operator_name = operator.name,
			code          = operator.code,
			input         = datum_input.from_dict(instance.input),
			output        = datum_output,
			config        = operator.config
		)

		instance.output = result.to_dict()
		self.dapi.db.commit()

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

		operator = self.dapi.operator_service.require(instance.operator)
		await self._set_status(instance, OperatorInstanceStatus.running)

		try:
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
