from dapi.lib.dapi import Dapi
from dapi.services import TypeService, OperatorService, TransactionService
from dapi.services import AssignmentService, FunctionService, InterpreterService, InstanceService
from dapi.schemas  import (
	IdSchema,
    NameSchema,
	EmptySchema,
	StatusSchema,
	
	TypeSchema,
	TypesSchema,
	
	OperatorSchema,
	OperatorsSchema,
	
	TransactionCreateSchema,
	TransactionSchema,
	TransactionsSchema,

	AssignmentSchema,

	OperatorInputSchema,
	TransactionInputSchema,
	OutputSchema
)

dapi = Dapi(
	TypeService,
	OperatorService,
	TransactionService,
	AssignmentService,
	FunctionService,
	InterpreterService,
	InstanceService
)

# # Example dynamic operator
# ###########################################################################

# from pydantic import create_model, Field

# ExampleInput  = create_model('ExampleInput',  value=(int, Field(...)))
# ExampleOutput = create_model('ExampleOutput', value=(int, Field(...)))

# async def double_handler(input: ExampleInput) -> ExampleOutput:  # type: ignore[arg-type]
#     return ExampleOutput(value=input.value * 2)

# dapi.define_operator_route(
# 	'double',
# 	ExampleInput,
# 	ExampleOutput,
# 	'Doubles the input value',
# 	double_handler
# )

# TYPE endpoints
###########################################################################

@dapi.router.post('/create_type', response_model=TypeSchema)
async def create_type(input: TypeSchema):
	'''Creates a new type in the DAPI system using a name and JSON schema.'''
	await dapi.type_service.create(name=input.name, schema=input.schema)
	return TypeSchema(name=input.name, schema=input.schema)

@dapi.router.post('/get_type', response_model=TypeSchema)
async def get_type(input: NameSchema):
	'''Returns a single type definition by name.'''
	record = await dapi.type_service.get(input.name)
	return TypeSchema(name=record['name'], schema=record['schema'])

@dapi.router.post('/get_all_types', response_model=TypesSchema)
async def get_all_types(input: EmptySchema):
	'''Returns a list of all registered types with full definitions.'''
	records = await dapi.type_service.get_all()
	return TypesSchema(items=[TypeSchema(name=r['name'], schema=r['schema']) for r in records])

@dapi.router.post('/delete_type', response_model=StatusSchema)
async def delete_type(input: NameSchema):
	'''Removes a type from the system by name.'''
	await dapi.type_service.delete(input.name)
	return {'status': 'success'}
	

# OPERATOR endpoints
###########################################################################

@dapi.router.post('/create_operator', response_model=OperatorSchema)
async def create_operator(input: OperatorSchema):
	'''Defines a new operator by name, input/output types, and executable code.'''
	operator = OperatorSchema(**input.model_dump())
	name = await dapi.operator_service.create(operator)
	return await dapi.operator_service.get(name)

@dapi.router.post('/get_all_operators', response_model=OperatorsSchema)
async def get_all_operators(input: EmptySchema):
	'''Returns a list of all registered operators.'''
	records = await dapi.operator_service.get_all()
	return OperatorsSchema(items=records)

@dapi.router.post('/delete_operator', response_model=StatusSchema)
async def delete_operator(input: NameSchema):
	'''Removes an operator from the system by name.'''
	await dapi.operator_service.delete(input.name)
	return {'status': 'success'}

@dapi.router.post('/get_operator', response_model=OperatorSchema)
async def get_operator(input: NameSchema):
	'''Returns a single operator by name.'''
	return await dapi.operator_service.get(input.name)

@dapi.router.post('/invoke_operator', response_model=OutputSchema)
async def invoke_operator(input: OperatorInputSchema):
	result = await dapi.operator_service.invoke(input.name, input.input)
	print(f"Invoke operator result: {result}")
	return OutputSchema(output=result if isinstance(result, dict) else {})


# TRANSACTION endpoints
###########################################################################

@dapi.router.post('/create_transaction', response_model=TransactionSchema)
async def create_transaction(input: TransactionSchema):
	'''Creates a transaction that wraps the invocation of a given operator.'''
	tx_id = await dapi.transaction_service.create(input)
	return TransactionSchema(id=tx_id, operator=input.operator)

@dapi.router.post('/create_transaction_assignment', response_model=AssignmentSchema)
async def create_transaction_assignment(input: AssignmentSchema):
	'''Creates an assignment that transfers values into the transaction input.'''
	assign = await dapi.assignment_service.create(input)
	return AssignmentSchema(id=assign.id, **input.model_dump())

@dapi.router.post('/get_all_transactions', response_model=TransactionsSchema)
async def get_all_transactions(input: EmptySchema):
	'''Returns a list of existing transactions (if not yet invoked).'''
	records = await dapi.transaction_service.get_all()
	return TransactionsSchema(items=records)

@dapi.router.post('/delete_transaction', response_model=StatusSchema)
async def delete_transaction(input: IdSchema):
	'''Removes a transaction from the system before it is invoked.'''
	await dapi.transaction_service.delete(input.id)
	return {'status': 'success'}

# @dapi.router.post('/invoke_transaction', response_model=OutputSchema)
# async def invoke_transaction(input: TransactionInputSchema):
#     '''Runs a transaction and returns its output; then deletes the transaction.'''
#     result = await dapi.transaction_service.invoke(input.name, input.input)
#     return OutputSchema(output=result)


# FUNCTION endpoint
###########################################################################

@dapi.router.post('/create_function', response_model=OperatorSchema)
async def create_function(input: OperatorSchema):
    '''Creates a function composite operator from transaction chain and shared scope.'''
    # TODO: ScopeService.create
    result = await dapi.function_service.create(input)
    return OperatorSchema(**input.model_dump())


# DYNAMIC endpoint
###########################################################################

@dapi.router.post('/{operator_name}', include_in_schema=False)
async def dynamic_operator_handler(operator_name: str, input: dict):
	'''Generic handler for all dynamically created operators'''
	return await dapi.operator_service.invoke(operator_name, input)
