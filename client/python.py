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

input_data = { 'x': 7 }
print('code:', square_code)
print('input:', input_data)
square_result = Client.invoke('square', input_data)
print('result:', square_result)
expected_result = {'x': input_data['x'] ** 2}
print('Expected result:', expected_result)
