from dapi.lib import Datum, Operator


################################################################

class Square(Operator):
	class InputType(Datum.Pydantic):
		x: float

	class OutputType(Datum.Pydantic):
		x: float

	async def invoke(self, x):
		return x * x

################################################################

class OllamaAddOne(Operator):
	class InputType(Datum.Pydantic):
		x: float

	class OutputType(Datum.Pydantic):
		x: float

	code = '''
		'Given a number {{input.x}}, return its increment by one as { "x": input.x + 1 }'
	'''

	interpreter = 'llm'
	config = {
		'model_id'    : 'ollama::gemma3:4b',
		'temperature' : 0
	}

################################################################

class DoubleThenSquare(Operator):
	class InputType(Datum.Pydantic):
		x: float

	class OutputType(Datum.Pydantic):
		x: float

	async def invoke(self, x):
		x = await times_two(x)       # Full Python
		x = await square(x)          # Mini Python
		x = await ollama_add_one(x)  # LLM
		return x

################################################################

class Process:
	entry = DoubleThenSquare
