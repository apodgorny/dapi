from lib.client import Client


# step 1: define a type for numbers
number_type = {
	'title'     : 'number_type',
	'type'      : 'object',
	'properties': {
		'x': { 'type': 'number' }
	},
	'required': ['x']
}
Client.create_type('number_type', number_type)


# step 2: delete operator if it exists
# Client.delete_operator('cube')
cube_code = 'Given a number {{input.x}}, return its cube as { "x": input.x ** 3 }'

Client.create_operator(
	name        = 'cube',
	input_type  = 'number_type',
	output_type = 'number_type',
	code        = cube_code,
	interpreter = 'llm',
	meta        = {
		'model_id': 'ollama::gemma3:4b',
		'temperature': 0.0
	}
)


# step 4: directly invoke the operator
input_data = { 'x': 7 }
print('code:', cube_code)
print('input:', input_data)
result = Client.invoke('cube', input_data)
print('result:', result)
