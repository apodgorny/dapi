from uuid      import uuid4
from datetime  import datetime

from sqlalchemy.orm                 import Session
from dapi.db                        import OperatorInstanceRecord, OperatorInstanceStatus
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

	async def _resolve_accessor(self, r_accessor: str, scope: Datum, instance: OperatorInstanceRecord):
		# implicit scope
		if '.output' in r_accessor:
			name, _, path = r_accessor.partition('.output')
			if name not in scope:
				raise ValueError(f'Scope has no entry `{name}`')
			value = scope[name]
			if not path or path == '.':
				return value
			return value[path.lstrip('.')]

		elif r_accessor.startswith('input.'):
			return instance.input[r_accessor[6:]]
		elif r_accessor == 'input':
			return instance.input
		elif r_accessor.startswith('output.'):
			return instance.output[r_accessor[7:]]
		elif r_accessor == 'output':
			return instance.output
		elif r_accessor in scope:
			return scope[r_accessor]
		else:
			raise ValueError(f'Accessor `{r_accessor}` is not found in scope')

	async def _invoke_atomic(self, instance: OperatorInstanceRecord, operator):
		interpreter  = await self.dapi.interpreter_service.require(operator.interpreter)
		datum_input  = await self.dapi.operator_service.get_input_datum(operator.name)
		datum_output = await self.dapi.operator_service.get_output_datum(operator.name)
		
		# Pass both input and output datums to interpreter
		result = await interpreter.invoke(
			operator_name = operator.name,
			code          = operator.code,
			input         = datum_input.from_dict(instance.input),
			output        = datum_output,
			meta          = operator.meta
		)
		
		# Get the result data to store in the instance
		instance.output = result.to_dict()
		print(f"Debug - Output after invocation: {instance.output}")

	async def _invoke_composite(self, instance: OperatorInstanceRecord, operator):
		definition      = operator.meta.get('definition', {})
		transactions    = definition.get('transactions', [])
		scope           = Datum(operator.input_type).from_dict(instance.input)
		children_ids    = []
		scope_instances = {}

		for tx in transactions:
			tx_operator = tx['operator']
			tx_name     = tx['name']
			tx_input     = {}

			for a in tx.get('assignments', []):
				l_accessor = a['l_accessor']
				r_accessor = a['r_accessor']
				value = self._resolve_accessor(r_accessor, scope, instance)
				tx_input[l_accessor] = value

			child_instance = self.create(
				operator_name = tx_operator,
				instance_name = tx_name,
				input_data    = tx_input
			)
			invoked        = self.invoke(child_instance.id)
			scope[tx_name] = Datum(invoked.output)
			
			children_ids.append(child_instance.id)

		instance.output = scope.to_dict()
		instance.children = children_ids

	#############################################################################

	async def create(
		self,
		operator_name : str,
		instance_name : str  = None,
		input_data    : dict = {}
	) -> OperatorInstanceSchema:
		instance_id = str(uuid4())
		instance = OperatorInstanceRecord(
			id         = instance_id,                   # Unique id
			name       = instance_name or instance_id,  # Variable name
			operator   = operator_name,                 # Operator class name

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
		is_composite = operator.interpreter == 'composite'

		await self._set_status(instance, OperatorInstanceStatus.running)

		try:
			if is_composite : await self._invoke_composite(instance, operator)
			else            : await self._invoke_atomic(instance, operator)

			await self._set_status(instance, OperatorInstanceStatus.invoked)
		except Exception as e:
			print(e)
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
