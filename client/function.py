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
	interpreter = 'python'
)

Client.create_operator(
	name        = 'cube',
	input_type  = 'number_type',
	output_type = 'number_type',
	code        = 'Given a number {{input.x}}, return its cube as { "x": input.x ** 3 }',
	interpreter = 'llm',
	config      = {
		'model_id'    : 'ollama::gemma3:4b',
		'temperature' : 0.0,
		'system'      : 'You are a helpful math assistant'
	}
)

# Client.create_operator(
# 	name        = 'cube',
# 	input_type  = 'number_type',
# 	output_type = 'number_type',
# 	code        = '{{output.x}} = {{input.x}} ** 3',
# 	interpreter = 'python'
# )

Client.create_operator(
	name        = 'square_then_cube',
	input_type  = 'number_type',
	output_type = 'number_type',
	code        = '', 
	interpreter = 'function',
	scope       = {}
)

if not (square_tx := Client.create_transaction('square1', 'square')):
	square_tx = Client.get_transaction('square1', 'square')

if not (cube_tx := Client.create_transaction('cube1', 'cube')):
	cube_tx = Client.get_transaction('cube1', 'cube')

if not (return_tx := Client.create_transaction('this', 'return')):
	return_tx = Client.get_transaction('this', 'return')


Client.assign(square_tx['id'], 'square1.input', 'this.input')  
Client.assign(cube_tx['id'],   'cube1.input',   'square1.output')
Client.assign(return_tx['id'], 'this.output',   'cube1.output')

Client.set_operator_transactions('square_then_cube', [square_tx['id'], cube_tx['id'], return_tx['id']])

# Step 4: Invoke the function with input data
input_data = { 'x': 5 }
print('Input:', input_data)
result = Client.invoke('square_then_cube', input_data)
print('Result:', result)

# # Direct operator invocation for comparison
# print('\nDirect operator invocations:')
# square_result = Client.invoke('square', input_data)
# print('Square result:', square_result)
# cube_result = Client.invoke('cube', input_data)
# print('Cube result:', cube_result)
