import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from client.lib.client import Client
from dapi.lib.datum    import Datum

class NumberType(Datum.Pydantic):
	x: float

Client.create_type('number_type', NumberType)

##########################################################################################

cube_code = 'Given a number {{input.x}}, return its cube as { "x": input.x ** 3 }'
Client.create_operator(
	name        = 'cube',
	input_type  = 'number_type',
	output_type = 'number_type',
	code        = cube_code,
	interpreter = 'llm',
	config      = {
		'model_id': 'ollama::gemma3:4b',
		'temperature': 0.0
	}
)

##########################################################################################

input_data = { 'x': 7 }
print('code:', cube_code)
print('input:', input_data)
result = Client.invoke('cube', input_data)
print('result:', result)
expected_result = {'x': input_data['x'] ** 3}
print('Expected result:', expected_result)
