import os, sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from pydantic import BaseModel
from typing   import List, Dict, Any, Optional

from lib import Operator, WordWield as ww


################################################################

class Disp(Operator):
	class InputType(BaseModel):
		s: str

	class OutputType(BaseModel):
		s: str

	async def invoke(self, s):
		return print('DISP-', s)

################################################################

class Repeat(Operator):
	class InputType(BaseModel):
		s: str

	class OutputType(BaseModel):
		s: str

	async def invoke(self, s):
		await disp(s + ' (1)')
		await disp(s + ' (2)')
		return s

################################################################

ww.init()
ww.invoke('repeat',
	s = 'foobar'
)

