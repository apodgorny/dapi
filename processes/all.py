from dapi.lib import Datum, Operator


################################################################

# Define the square operator class that extends Operator
class square(Operator):
	class InputType(Datum.Pydantic):
		x: float

	class OutputType(Datum.Pydantic):
		x: float

	async def invoke(self, input):
		x = input['x']
		return { 'x' : x * x }

################################################################

class ollama_add_one(Operator):
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

# Define the double_then_square operator class that extends Operator
class double_then_square(Operator):
	class InputType(Datum.Pydantic):
		x: float

	class OutputType(Datum.Pydantic):
		x: float

	async def invoke(self, input):
		doubled     = await times_two({'x' : input['x']})           # Plugin
		squared     = await square({'x': doubled['x']})          # Python
		incremented = await ollama_add_one({'x': squared['x']})  # LLM
		return { 'x' : incremented['x'] }


################################################################

# Process class with entry point
class Process:
	entry = double_then_square  # Set the entry point to the double_then_square operator
