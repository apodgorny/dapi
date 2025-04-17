from lib.client import Client

number_type = {
	'title'     : 'number_type',
	'type'      : 'object',
	'properties': {
		'x': { 'type': 'number' }
	},
	'required': ['x']
}
Client.create_type('number_type', number_type)

# Client.delete_operator('cube')

Client.create_operator(
	name        = 'square',
	input_type  = 'number_type',
	output_type = 'number_type',
	code        = '{{output.x}} = {{input.x}} ** 2',
	interpreter = 'python',
)

Client.create_operator(
	name        = 'cube',
	input_type  = 'number_type',
	output_type = 'number_type',
	code        = 'Given a number {{input.x}}, return its cube as { "x": input.x ** 3 }',
	interpreter = 'llm',
	meta        = {
		'model_id': 'ollama::gemma3:4b',
		'temperature': 0.0
	}
)

Client.create_




# step 4: directly invoke the operator
input_data = { 'x': 7 }
print('code:', cube_code)
print('input:', input_data)
result = Client.invoke('cube', input_data)
print('result:', result)
