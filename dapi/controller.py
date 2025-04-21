from dapi.lib.dapi     import Dapi
from dapi.services     import OperatorService, InterpreterService, InstanceService
from dapi.schemas      import (
	NameSchema,
	EmptySchema,
	StatusSchema,
	TypeSchema,
	TypesSchema,
	OperatorSchema,
	OperatorsSchema,
	OperatorInputSchema,
	OutputSchema
)


dapi = Dapi(
	# TypeService,
	OperatorService,
	InterpreterService,
	InstanceService
)


# TYPE endpoints
############################################################################

# @dapi.router.post('/create_type', response_model=TypeSchema)
# async def create_type(input: TypeSchema):
# 	await dapi.type_service.create(name=input.name, schema=input.schema)
# 	return input

# @dapi.router.post('/get_type', response_model=TypeSchema)
# async def get_type(input: NameSchema):
# 	record = await dapi.type_service.get(input.name)
# 	return TypeSchema(name=record['name'], schema=record['schema'])

# @dapi.router.post('/get_all_types', response_model=TypesSchema)
# async def get_all_types(input: EmptySchema):
# 	records = await dapi.type_service.get_all()
# 	return TypesSchema(items=[TypeSchema(name=r['name'], schema=r['schema']) for r in records])

# @dapi.router.post('/delete_type', response_model=StatusSchema)
# async def delete_type(input: NameSchema):
# 	await dapi.type_service.delete(input.name)
# 	return {'status': 'success'}


# OPERATOR endpoints
############################################################################

@dapi.router.post('/create_operator', response_model=OperatorSchema)
async def create_operator(input: OperatorSchema):
	name = await dapi.operator_service.create(input)
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

@dapi.router.post('/invoke_operator', response_model=OutputSchema)
async def invoke_operator(input: OperatorInputSchema):
	result = await dapi.operator_service.invoke(input.name, input.input)
	return OutputSchema(output=result if isinstance(result, dict) else {})


# DYNAMIC fallback
############################################################################

@dapi.router.post('/{operator_name}', include_in_schema=False)
async def dynamic_operator_handler(operator_name: str, input: dict):
	return await dapi.operator_service.invoke(operator_name, input)
