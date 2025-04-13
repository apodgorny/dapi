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


Client.delete_operator('square')

# step 2: define the operator 'square'
square_code = '{{output.x}} = {{input.x}} ** 2'

Client.create_operator(
	name        = 'square',
	input_type  = 'number_type',
	output_type = 'number_type',
	code        = square_code,
	interpreter = 'python',
)


# step 3: directly invoke the operator
input_data = { 'x': 7 }
print('code:', square_code)
print('input:', input_data)
result     = Client.invoke('square', input_data)
print('result:', result)
