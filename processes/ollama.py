from dapi.lib import Datum, OperatorDefinition

################################################################

class ollama_cube(OperatorDefinition):
	class InputType(Datum.Pydantic):
		x: float

	class OutputType(Datum.Pydantic):
		x: float

	code = '''
		'Given a number {{input.x}}, return its cube as { "x": input.x ** 3 }'
	'''

	interpreter = 'llm'
	config = {
		'model_id'    : 'ollama::gemma3:4b',
		'temperature' : 0
	}

################################################################

class Process:
	entry = ollama_cube
