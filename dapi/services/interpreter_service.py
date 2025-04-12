from __future__ import annotations

from dapi.lib       import DapiService, DapiException
from dapi.lib.datum import Datum


@DapiService.wrap_exceptions()
class InterpreterService(DapiService):
	'''Service for executing code across multiple interpreters.'''

	def __init__(self, dapi):
		self.dapi = dapi
		self.interpreters = {
			'python': PythonInterpreter(),
			'llm': LLMInterpreter()
		}

	############################################################################

	async def has(self, name: str) -> bool:
		return name in self.interpreters

	async def require(self, name: str):
		if not await self.has(name):
			raise DapiException(status_code=404, detail=f'Interpreter `{name}` does not exist', severity=DapiException.HALT)
		return self.interpreters[name]

	############################################################################


class BaseInterpreter:
	'''Base class for all code interpreters.'''
	
	async def invoke(self, code: str, input: Datum) -> dict:
		raise NotImplementedError("Subclasses must implement invoke()")


class PythonInterpreter(BaseInterpreter):
	'''Executes Python code in a sandboxed environment.'''
	
	async def invoke(self, code: str, input: Datum) -> dict:
		# Simple sandboxed execution - in a real implementation, 
		# this would have more security measures
		input_dict = input.to_dict()
		
		# Create a safe globals dictionary with limited built-ins
		safe_globals = {
			'input': input_dict
		}
		
		try:
			# Process template syntax: replace {{input.x}} with actual values
			for key, value in input_dict.items():
				code = code.replace(f'{{{{input.{key}}}}}', str(value))

			# Wrap code in a function if it's not already
			if 'def ' not in code and 'return ' not in code:
				# Indent each line of the code with a tab
				indented_code = '\n'.join(f'\t{line}' for line in code.strip().split('\n'))
				code = f'''
def _execute_code():
{indented_code}
	return output if "output" in locals() else input
result = _execute_code()
'''
			# Execute the code and capture the result
			local_vars = {}
			exec(compile(code, '<string>', 'exec'), safe_globals, local_vars)
			result = local_vars.get('result')
			if result is None:
				raise ValueError("Python code did not produce a result")
			return result
		except SyntaxError as e:
			raise ValueError(f"Python syntax error: {str(e)}")
		except Exception as e:
			raise ValueError(f"Python execution error: {str(e)}")


class LLMInterpreter(BaseInterpreter):
	'''Executes prompts through an LLM.'''
	
	async def invoke(self, code: str, input: Datum) -> dict:
		# This would connect to an LLM service in a real implementation
		try:
			# For now, we'll just echo back the input as a simple placeholder
			input_dict = input.to_dict()
			# In a real implementation, we would process the code as a prompt
			# and send it to an LLM service with the input data
			print(f"LLM Interpreter would execute prompt: {code[:50]}...")
			return input_dict  # Placeholder implementation
		except Exception as e:
			raise ValueError(f"LLM execution error: {str(e)}")
