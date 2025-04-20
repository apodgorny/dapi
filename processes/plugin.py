import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from client.lib.client import Client
from dapi.lib.datum    import Datum

class NumberType(Datum.Pydantic):
	x: float

Client.create_type('number_type', NumberType)

##########################################################################################

Client.create_operator(
	name        = 'times_two',
	input_type  = 'number_type',
	output_type = 'number_type',
	code        = '',  # Not used for plugin operators
	interpreter = 'plugin',
	config      = {}  # Optional configuration if needed
)

##########################################################################################

input_data = {'x': 21}
print('Input:', input_data)
result = Client.invoke('times_two', input_data)
print('Result:', result)
expected_result = {'x': input_data['x'] * 2}
print('Expected result:', expected_result)
