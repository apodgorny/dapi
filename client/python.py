from lib.client import Client


# step 1: define a type for numbers
number_type = {
	'title'     : 'number_type',
	'type'      : 'object',
	'properties': {
		'x': { 'type': 'integer' }
	},
	'required': ['x']
}
Client.create_type('number_type', number_type)

# Client.delete_operator('square')

square_code = '''
def square(input):
	x = input['x']
	return {'x': x * x}
'''

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
square_result = Client.invoke('square', input_data)
print('result:', square_result)

# Let's manually test the calculation to verify
expected_result = {'x': input_data['x'] ** 2}
print('expected result:', expected_result)
