import os, sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from pydantic import BaseModel
from typing   import List, Dict, Any, Optional

from wordwield.wordwield import Operator, WordWield as ww


################################################################

class Disp(Operator):
	class InputType(BaseModel):
		s: str

	class OutputType(BaseModel):
		s: str

	async def invoke(self, s):
		return print('==========> DISP-', s)

################################################################

class Recurse(Operator):
	class InputType(BaseModel):
		s: str
		n: int

	class OutputType(BaseModel):
		s: str

	async def invoke(self, s, n):
		if n > 0:
			await disp(s + f' ({n})')
			await recurse(s, n - 1)
			
		return s

################################################################

ww.init()
ww.invoke('recurse',
	s = 'foobar',
	n = 2
)

