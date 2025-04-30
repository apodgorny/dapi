from dapi.lib       import Dapi, ExecutionContext
from dapi.services  import OperatorService
from dapi.schemas   import (
	NameSchema,
	EmptySchema,
	StatusSchema,
	OperatorSchema,
	OperatorsSchema,
	OperatorInputSchema,
	OutputSchema
)

dapi = Dapi(
	OperatorService
)

# OPERATOR endpoints
############################################################################

@dapi.router.post('/create_operator', response_model=OperatorSchema)
async def create_operator(input: OperatorSchema):
	name = await dapi.operator_service.create(input, replace=True)
	return await dapi.operator_service.get(name)

@dapi.router.post('/get_operator', response_model=OperatorSchema)
async def get_operator(input: NameSchema):
	return await dapi.operator_service.get(input.name)

@dapi.router.post('/get_all_operators', response_model=OperatorsSchema)
async def get_all_operators(input: EmptySchema):
	records = await dapi.operator_service.get_all()
	return OperatorsSchema(items=records)

@dapi.router.post('/delete_operator', response_model=StatusSchema)
async def delete_operator(input: NameSchema):
	await dapi.operator_service.delete(input.name)
	return {'status': 'success'}

@dapi.router.post('/reset', response_model=StatusSchema)
async def reset_operators(input: EmptySchema):
	await dapi.operator_service.delete_all()
	return { 'status' : 'success' }

# DYNAMIC invoke
############################################################################

@dapi.router.post('/{operator_name}', include_in_schema=False)
async def dynamic_operator_handler(operator_name: str, input: dict):
	context = ExecutionContext()
	result  = await dapi.operator_service.invoke(operator_name, input, context)
	return OutputSchema(output=result if isinstance(result, dict) else {})
