import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from client.lib.client import Client
from dapi.lib.datum    import Datum

class NumberType(Datum.Pydantic):
	x: float

Client.create_type('number_type', NumberType)


##########################################################################################

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

##########################################################################################

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


##########################################################################################

input_data = { 'x': 3 }
print('code:', combo_code)
print('input:', input_data)
result = Client.invoke('double_then_square', input_data)
print('result:', result)

expected_result = {'x': (input_data['x'] * 2) ** 2}
print('expected result:', expected_result)
