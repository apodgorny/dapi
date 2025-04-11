from dapi.lib.dapi import DAPI
from dapi.services import TypeService, OperatorService
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

	AssignmentSchema,
	AssignmentsSchema,

	FunctionSchema
)

dapi = DAPI(
	TypeService,
	OperatorService
)

# Example dynamic operator
###########################################################################

from pydantic import create_model, Field

ExampleInput  = create_model('ExampleInput',  value=(int, Field(...)))
ExampleOutput = create_model('ExampleOutput', value=(int, Field(...)))

async def double_handler(input: ExampleInput) -> ExampleOutput:  # type: ignore[arg-type]
    return ExampleOutput(value=input.value * 2)

dapi.define_operator_route(
	'double',
	ExampleInput,
	ExampleOutput,
	double_handler,
	description='Doubles the input value'
)

# TYPE endpoints
###########################################################################

@dapi.router.post('/create_type', response_model=TypeSchema)
async def create_type(input: TypeSchema):
	'''Creates a new type in the DAPI system using a name and JSON schema.'''
	dapi.type_service.create(name=input.name, schema=input.schema)
	return TypeSchema(name=input.name, schema=input.schema)

@dapi.router.post('/get_type', response_model=TypeSchema)
async def get_type(input: NameSchema):
	'''Returns a single type definition by name.'''
	record = dapi.type_service.get(input.name)
	return TypeInfoSchema(**record)

@dapi.router.post('/get_all_types', response_model=TypesSchema)
async def get_all_types(input: EmptySchema):
	'''Returns a list of all registered types with full definitions.'''
	records = dapi.type_service.get_all()
	return ListTypesOutputSchema(data=[TypeInfoSchema(**r) for r in records])

@dapi.router.post('/delete_type', response_model=StatusSchema)
async def delete_type(input: NameSchema):
	'''Removes a type from the system by name.'''
	dapi.type_service.delete(input.name)
	return {'status': 'success'}
	

# OPERATOR endpoints
###########################################################################

@dapi.router.post('/create_operator', response_model=OperatorSchema)
async def create_operator(input: OperatorSchema):
	'''Defines a new operator by name, input/output types, and executable code.'''
	operator = OperatorSchema(**input.model_dump())
	name = dapi.operator_service.create(operator)
	return dapi.operator_service.get(name)

@dapi.router.post('/list_operators', response_model=OperatorsSchema)
async def list_operators(input: EmptySchema):
	'''Returns a list of all registered operators.'''
	records = dapi.operator_service.get_all()
	return ListOperatorsOutputSchema(data=records)

@dapi.router.post('/delete_operator', response_model=StatusSchema)
async def delete_operator(input: NameSchema):
	'''Removes an operator from the system by name.'''
	dapi.operator_service.delete(input.name)
	return {'status': 'success'}

@dapi.router.post('/get_operator', response_model=OperatorSchema)
async def get_operator(input: NameSchema):
	'''Returns a single operator by name.'''
	return dapi.operator_service.get(input.name)


# TRANSACTION endpoints
###########################################################################

@dapi.router.post('/create_transaction', response_model=TransactionCreateSchema)
async def create_transaction(input: TransactionSchema):
    '''Creates a transaction that wraps the invocation of a given operator.'''
    # TODO: TransactionService.create_transaction
    return TransactionInfoSchema(id='tx_1', operator=input.operator)

@dapi.router.post('/create_transaction_assignment', response_model=AssignmentSchema)
async def create_transaction_assignment(input: AssignmentSchema):
    '''Creates an assignment that transfers values into the transaction input.'''
    # TODO: AssignmentService.create
    return AssignmentInfoSchema(id='as_1', **input.model_dump())

# @dapi.router.post('/invoke_transaction', response_model=InvokeTransactionOutputSchema)
# async def invoke_transaction(input: InvokeTransactionInputSchema):
#     '''Runs a transaction and returns its output; then deletes the transaction.'''
#     # TODO: TransactionService.invoke
#     return InvokeTransactionOutputSchema(output={'value': 42})

@dapi.router.post('/list_transactions', response_model=AssignmentsSchema)
async def list_transactions(input: EmptySchema):
    '''Returns a list of existing transactions (if not yet invoked).'''
    return AssignmentsSchema(data=[])

@dapi.router.post('/delete_transaction', response_model=StatusSchema)
async def delete_transaction(input: IdSchema):
    '''Removes a transaction from the system before it is invoked.'''
    # TODO: TransactionService.delete
    return {'status': 'success'}


# SCOPE endpoint
###########################################################################

@dapi.router.post('/create_function', response_model=FunctionSchema)
async def create_function(input: FunctionSchema):
    '''Creates a function composite operator from transaction chain and shared scope.'''
    # TODO: ScopeService.create
    return FunctionSchema(**input.model_dump())
