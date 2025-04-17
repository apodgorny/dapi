import json
from fastapi import Request, Response

from dapi.controller import dapi

async def enhance_openapi_schema(request: Request, call_next):
	'''
	Middleware that intercepts OpenAPI schema requests to add dynamic operator endpoints.
	This makes all registered operators visible in the API documentation.
	'''
	if request.url.path == '/openapi.json':
		# Get the original OpenAPI schema
		response = await call_next(request)
		
		# Extract content from the response (handle both streaming and regular responses)
		response_body = b""
		async for chunk in response.body_iterator:
			response_body += chunk
		
		# Parse the schema from the response body
		schema = json.loads(response_body)
		
		# Add paths for all operators in the database
		try:
			operators = await dapi.operator_service.get_all()
			for op in operators:
				name = op['name']
				path = f'/dapi/{name}'
				
				# Skip if path already exists in schema
				if path in schema['paths']:
					continue
				
				# Add operator endpoint to schema
				schema['paths'][path] = {
					'post': {
						'summary': f'Dynamic operator: {name}',
						'description': op.get('description', f'Executes the {name} operator'),
						'operationId': f'invoke_{name}',
						'requestBody': {
							'content': {
								'application/json': {
									'schema': {'type': 'object'}
								}
							},
							'required': True
						},
						'responses': {
							'200': {
								'description': 'Successful response',
								'content': {
									'application/json': {
										'schema': {'type': 'object'}
									}
								}
							}
						},
						'tags': ['Operators']
					}
				}
			
			# Return the enhanced schema
			return Response(
				content=json.dumps(schema),
				media_type='application/json',
				status_code=response.status_code
			)
		except Exception as e:
			print(f'Error enhancing OpenAPI schema: {e}')
			return response
			
	# For all other requests, pass through
	return await call_next(request)
