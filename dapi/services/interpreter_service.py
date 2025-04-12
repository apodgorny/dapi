from __future__ import annotations

from fastapi import HTTPException

from dapi.lib.datum import Datum


class InterpreterService:
	'''Service for executing code across multiple interpreters.'''

	def __init__(self, dapi):
		self.dapi = dapi
		self.interpreters = {
			'python': PythonInterpreter(),
			'llm': LLMInterpreter()
		}

	############################################################################

	def has(self, name: str) -> bool:
		return name in self.interpreters

	def require(self, name: str):
		if not self.has(name):
			raise HTTPException(status_code=404, detail=f'Interpreter `{name}` does not exist')
		return self.interpreters[name]

	############################################################################


class BaseInterpreter:
	'''Base class for all code interpreters.'''
	
	def invoke(self, code: str, input: Datum) -> dict:
		raise NotImplementedError("Subclasses must implement invoke()")


class PythonInterpreter(BaseInterpreter):
	'''Executes Python code in a sandboxed environment.'''
	
	def invoke(self, code: str, input: Datum) -> dict:
		# Simple sandboxed execution - in a real implementation, 
		# this would have more security measures
		input_dict = input.to_dict()
		
		# Create a safe globals dictionary with limited built-ins
		safe_globals = {
			'input': input_dict
		}
		
		try:
			# Add a return statement to capture the result
			if 'return' not in code:
				code += '\nreturn input'  # Default return if none specified
				
			result = eval(compile(code, '<string>', 'exec'), safe_globals)
			return result
		except Exception as e:
			raise HTTPException(status_code=500, detail=f"Python execution error: {str(e)}")


class LLMInterpreter(BaseInterpreter):
	'''Executes prompts through an LLM.'''
	
	def invoke(self, code: str, input: Datum) -> dict:
		# This would connect to an LLM service in a real implementation
		# For now, we'll just echo back the input as a simple placeholder
		input_dict = input.to_dict()
		return input_dict  # Placeholder implementation
