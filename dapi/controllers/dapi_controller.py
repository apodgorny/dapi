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

	FunctionSchema,

	OperatorInputSchema,
	TransactionInputSchema,
	OutputSchema
)

dapi = DAPI(
	TypeService,
	OperatorService
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
	name = await dapi.operator_service.create(operator)
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

@dapi.router.post('/invoke_operator', response_model=OutputSchema)
async def invoke_operator(input: OperatorInputSchema):
	result = await dapi.operator_service.invoke(input.name, input.input)
	print(f"Invoke operator result: {result}")
	return result


# TRANSACTION endpoints
###########################################################################

@dapi.router.post('/create_transaction', response_model=TransactionCreateSchema)
async def create_transaction(input: TransactionSchema):
	'''Creates a transaction that wraps the invocation of a given operator.'''
	tx_id = dapi.transaction_service.create(input)
	return TransactionInfoSchema(id=tx_id, operator=input.operator)

@dapi.router.post('/create_transaction_assignment', response_model=AssignmentSchema)
async def create_transaction_assignment(input: AssignmentSchema):
	'''Creates an assignment that transfers values into the transaction input.'''
	assign = dapi.assignment_service.create(input)
	return AssignmentInfoSchema(id=assign.id, **input.model_dump())

@dapi.router.post('/list_transactions', response_model=AssignmentsSchema)
async def list_transactions(input: EmptySchema):
	'''Returns a list of existing transactions (if not yet invoked).'''
	records = dapi.transaction_service.get_all()
	return AssignmentsSchema(data=records)

@dapi.router.post('/delete_transaction', response_model=StatusSchema)
async def delete_transaction(input: IdSchema):
	'''Removes a transaction from the system before it is invoked.'''
	dapi.transaction_service.delete(input.id)
	return {'status': 'success'}

@dapi.router.post('/invoke_transaction', response_model=OutputSchema)
async def invoke_transaction(input: OperatorInputSchema):
    '''Runs a transaction and returns its output; then deletes the transaction.'''
    # TODO: TransactionService.invoke
    return InvokeTransactionOutputSchema(output={'value': 42})


# FUNCTION endpoint
###########################################################################

@dapi.router.post('/create_function', response_model=FunctionSchema)
async def create_function(input: FunctionSchema):
    '''Creates a function composite operator from transaction chain and shared scope.'''
    # TODO: ScopeService.create
    return FunctionSchema(**input.model_dump())

# Dynamic operator handler - catches any /dapi/{operator_name} requests
@dapi.router.post('/{operator_name}', include_in_schema=False)
async def dynamic_operator_handler(operator_name: str, payload: dict):
	'''Generic handler for all dynamically created operators'''
	print(f"Dynamic operator handler called for: {operator_name} with payload: {payload}")
	
	# Check if the operator exists in the database
	try:
		operator = dapi.operator_service.require(operator_name)
		print(f"Found operator: {operator.name}")
		
		# For now, just implement a simple doubling operation for testing
		if "value" in payload:
			return {"value": payload["value"] * 2}
		elif "number" in payload:
			return {"number": payload["number"] * 2}
		else:
			return {"error": f"Input for operator {operator_name} missing 'value' or 'number' field"}
	except Exception as e:
		print(f"Error processing dynamic operator {operator_name}: {e}")
		# raise HTTPException(status_code=404, detail=f"Operator {operator_name} not found or error: {str(e)}")
		exit()
