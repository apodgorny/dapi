from lib.client import Client


# Тип данных: number_type
number_type = {
	'title'     : 'number_type',
	'type'      : 'object',
	'properties': {
		'x': { 'type': 'number' }
	},
	'required': ['x']
}
Client.create_type('number_type', number_type)


# Оператор square (MiniPython)
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


# Оператор cube (LLM/Ollama)
cube_code = 'Given a number {{input.x}}, return its cube as { "x": input.x ** 3 }'

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


# Оператор square_then_cube (комбинирует оба)
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


# Вызов
input_data = { 'x': 2 }
print('code:', combo_code)
print('input:', input_data)
result = Client.invoke('square_then_cube', input_data)
print('result:', result)

expected = {'x': (input_data['x'] ** 2) ** 3}
print('expected:', expected)
