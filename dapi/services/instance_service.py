from uuid      import uuid4
from datetime  import datetime

from sqlalchemy.orm                 import Session
from dapi.db                        import OperatorInstanceRecord, OperatorInstanceStatus, TransactionRecord, AssignmentRecord
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
		
		# Pass both input and output datums to interpreter
		result = await interpreter.invoke(
			operator_name = operator.name,
			code          = operator.code,
			input         = datum_input.from_dict(instance.input),
			output        = datum_output,
			config        = operator.config
		)
		
		# Get the result data to store in the instance
		instance.output = result.to_dict()
		self.dapi.db.commit()

	async def _invoke_composite(self, instance: OperatorInstanceRecord, operator):
		# Get transactions directly from the operator record
		transactions = operator.transactions
		
		# Validate transactions exist
		if not transactions:
			raise ValueError(f'Function operator `{operator.name}` has no transactions defined. Use set_operator_transactions to add transactions.')
		
		scope           = Datum(OperatorScopeSchema)
		children_ids    = []
		scope_instances = {}

		scope['this.input']  = instance.input
		scope['this.output'] = instance.output

		print(scope.to_json())

		for tx_id in transactions:
			tx = self.dapi.db.get(TransactionRecord, tx_id)
			print('----------------------------------')
			print('transaction', tx.name, tx.operator)
			if not tx:
				raise ValueError(f'Transaction `{tx_id}` not found')
				
			assignments = self.dapi.db.query(AssignmentRecord).filter_by(transaction_id=tx_id).all()

			for assignment in assignments:
				l_accessor = assignment.l_accessor
				r_accessor = assignment.r_accessor
				print('--- ASSIGNMENT ---', l_accessor, '??', r_accessor)

				if not r_accessor in scope:
					raise ValueError(f'Accessor `{r_accessor}` is not in scope')

				print(l_accessor, '=', r_accessor)
				scope[l_accessor] = scope[r_accessor]
				print('set', l_accessor, scope[l_accessor])
				print('SCOPE', scope.to_json())

			if tx.operator != 'return':
				child_instance = await self.create(
					operator_name = tx.operator,
					instance_name = tx.name,
					input_data    = scope[f'{tx.name}.input']
				)
				child_instance = await self.invoke(child_instance.id)
				print('child_instance.output', child_instance.output)
				scope[f'{tx.name}.output'] = child_instance.output
				print('set', f'{tx.name}.output', scope[f'{tx.name}.output'])
				
				children_ids.append(child_instance.id)
				

		instance.children = children_ids
		instance.output = scope['this.output']
		print('Done function', instance.name, instance.output)

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
		is_composite = operator.interpreter == 'function'

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
