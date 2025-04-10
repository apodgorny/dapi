from fastapi           import FastAPI, APIRouter
from pydantic          import create_model, Field
from fastapi.responses import JSONResponse
from typing            import Any

app    = FastAPI()
router = APIRouter(prefix='/dapi')

@app.on_event('startup')
async def load_dapi():
	print('Hello, DAPI!')
	# operator_store = OperatorStore()
	# registrar      = APIRouterRegistrar(router)

	# for operator in operator_store.list_all():
	# 	await operator_service.register_operator(operator, registrar.define)

# def register_operator_from_schemas(
# 	name         : str,
# 	input_schema : dict,
# 	output_schema: dict
# ):
# 	# Dynamically create input/output models
# 	InputModel  = create_model(f'{name.capitalize()}Input',  **{
# 		k: (field_type(v), Field(..., description=f'{k} field')) for k, v in input_schema['properties'].items()
# 	})

# 	OutputModel = create_model(f'{name.capitalize()}Output', **{
# 		k: (field_type(v), Field(..., description=f'{k} field')) for k, v in output_schema['properties'].items()
# 	})

# 	# Create handler function with model-annotated argument
# 	async def handler(data: InputModel) -> OutputModel:
# 		# dummy logic: return the same values
# 		return OutputModel(**data.model_dump())

# 	handler.__name__ = f'{name}_handler'

# 	# Register route
# 	router.add_api_route(
# 		path           = f'/{name}',
# 		endpoint       = handler,
# 		methods        = ['POST'],
# 		response_model = OutputModel,
# 		name           = f'dapi:{name}',
# 		response_class = JSONResponse
# 	)

# # Helper to map JSON Schema types to Python
# def field_type(json_schema: dict) -> type:
# 	t = json_schema.get('type')
# 	if t == 'number' : return float
# 	if t == 'integer': return int
# 	if t == 'string' : return str
# 	if t == 'boolean': return bool
# 	if t == 'array'  : return list
# 	if t == 'object' : return dict
# 	return Any

# # Register test operator
# register_operator_from_schemas(
# 	name='double',
# 	input_schema={
# 		'type'      : 'object',
# 		'properties': { 'value': { 'type': 'number' } },
# 		'required'  : ['value']
# 	},
# 	output_schema={
# 		'type'      : 'object',
# 		'properties': { 'value': { 'type': 'number' } },
# 		'required'  : ['value']
# 	}
# )

# app.include_router(router)
