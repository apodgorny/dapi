from lib.client import Client


# Step 1: define a type for numbers
number_type = {
	'title'     : 'number_type',
	'type'      : 'object',
	'properties': {
		'x': { 'type': 'integer' }
	},
	'required': ['x']
}
Client.create_type('number_type', number_type)


# Step 2: define operator: square
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


# Step 3: define operator: double_then_square (calls square inside)
combo_code = '''
def double_then_square(input):
	doubled = input['x'] * 2
	squared = square({'x': doubled})
	return {'x': squared['x']}
'''
Client.create_operator(
	name        = 'double_then_square',
	input_type  = 'number_type',
	output_type = 'number_type',
	code        = combo_code,
	interpreter = 'python',
)


# Step 4: invoke the combined operator
input_data = { 'x': 3 }
print('code:', combo_code)
print('input:', input_data)
result = Client.invoke('double_then_square', input_data)
print('result:', result)

expected_result = {'x': (input_data['x'] * 2) ** 2}
print('expected result:', expected_result)
