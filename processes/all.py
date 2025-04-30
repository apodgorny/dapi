import os, sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from pydantic import BaseModel
from typing   import List, Dict, Any, Optional

from wordwield.wordwield import Operator, WordWield as ww


################################################################

class Square(Operator):
	class InputType(BaseModel):
		x: float

	class OutputType(BaseModel):
		x: float

	async def invoke(self, x):
		return x * x

################################################################

class OllamaAddOne(Operator):
	class InputType(BaseModel):
		x: float

	class OutputType(BaseModel):
		x: float

	prompt = '''
		'Given a number {{x}}, return its increment by one as { "x": x + 1 }'
	'''

	async def invoke(self, x):
		return await ask(
			input           = { 'x': x },
			prompt          = self.prompt,
			response_schema = self.output_type
		)
		return {}


################################################################

class DoubleThenSquare(Operator):
	class InputType(BaseModel):
		x: float

	class OutputType(BaseModel):
		x: float

	async def invoke(self, x):
		# exec('x = 2')
		x = await times_two(x)       # Full Python
		x = await square(x)          # Mini Python
		x = await ollama_add_one(x)  # LLM
		return x

################################################################

ww.init()
ww.invoke('double_then_square', {
	'x' : 3
})

