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
	interpreter = 'python'
)

##########################################################################################

cube_code = 'Given a number {{input.x}}, return its cube as { "x": {{input.x}} ** 3 }'
Client.create_operator(
	name        = 'cube',
	input_type  = 'number_type',
	output_type = 'number_type',
	code        = cube_code,
	interpreter = 'llm',
	config      = {
		'model_id'   : 'ollama::gemma3:4b',
		'temperature': 0.0
	}
)

##########################################################################################

combo_code = '''
def square_then_cube(input):
	sqr = square({'x': input['x']})
	cub = cube({'x': sqr['x']})
	return {'x': cub['x']}
'''
Client.create_operator(
	name        = 'square_then_cube',
	input_type  = 'number_type',
	output_type = 'number_type',
	code        = combo_code,
	interpreter = 'python'
)

##########################################################################################


# Вызов
input_data = { 'x': 7 }
print('code:', combo_code)
print('input:', input_data)
result = Client.invoke('square_then_cube', input_data)
print('result:', result)

expected = {'x': (input_data['x'] ** 2) ** 3}
print('expected:', expected)
