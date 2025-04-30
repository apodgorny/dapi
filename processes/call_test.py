import os, sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from pydantic import BaseModel
from typing   import List, Dict, Any, Optional

from wordwield.wordwield import Operator, WordWield as ww

################################################################

class Main(Operator):
	class InputType(BaseModel):
		operator : str
		message  : str

	class OutputType(BaseModel):
		call_result : dict

	async def invoke(self, operator, message):
		return await call(operator, message)

################################################################

ww.init()
ww.invoke('main', 
	operator = 'log',
	message  = 'haha'
)
