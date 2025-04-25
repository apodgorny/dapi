import ast
from dapi.lib import DapiException, ExecutionContext, String, FullPython, Interpreter


class FullPythonInterpreter(Interpreter):
	'''
	Executes a full Python class operator from the provided code string.
	Assumes the code includes a valid Python class with async invoke().
	'''

	type = 'full'

	async def invoke(self) -> dict:
		try:
			# Initialize FullPython with the provided code, context, and external operator callback
			full_python = FullPython(
				code                   = self.code,
				execution_context      = self.context,
				call_external_operator = self.call,
				globals_dict           = self.globals_dict
			)

			# Call the invoke method directly within FullPython, passing the operator class name
			result = await full_python.invoke(self.name, self.class_name, self.input_data)

			return result

		except Exception as e:
			raise DapiException.consume(e)



# import sys
# import os
# import inspect

# from pathlib  import Path
# from dapi.lib import (
# 	Datum,
# 	DapiException,
# 	Interpreter,
# 	Module,
# 	Operator,
# 	ExecutionContext,
# 	FullPython
# )


# class FullPythonInterpreter(Interpreter):
# 	'''
# 	Executes standalone plugin classes that extend Operator.
# 	The operator name must match a file in the operators directory
# 	(e.g. "square" loads operators/square.py)
# 	'''

# 	OPERATOR_DIR = os.path.join(
# 		os.environ.get('PROJECT_PATH'),
# 		os.environ.get('OPERATOR_DIR', 'operators')
# 	)

# 	def _validate(self, operator_name, operator_class):
# 		if not operator_class:
# 			raise ValueError(f'Plugin operator `{operator_name}` must be a subclass of `Operator`')

# 		if not hasattr(operator_class, 'invoke') or not callable(getattr(operator_class, 'invoke')):
# 			raise ValueError(f'Plugin operator `{operator_name}` must define static method `invoke(input)`')

# 		if not inspect.iscoroutinefunction(operator_class.invoke):
# 			raise ValueError(f'Plugin operator `{operator_name}` must define an async invoke method')

# 	async def _invoke(self, name, data, context=None):
# 		# Ensure the context is passed to the operator service if it's not already provided
# 		if context is None:
# 			raise ValueError('ExecutionContext must be explicitly provided')
		
# 		# Invoke the operator service with the context
# 		result = await self.dapi.operator_service.invoke(name, data, context=context)
# 		if isinstance(result, dict) and 'output' in result:  # Extract the actual output from the result
# 			return result['output']
# 		return result

# 	async def invoke(
# 		self,
# 		operator_name : str,   # plugin file/module name (e.g. "square")
# 		code          : str,   # unused
# 		input         : Datum,
# 		output        : Datum,
# 		config        : dict,
# 		context       : ExecutionContext
# 	) -> Datum:

# 		# if context is None: raise ValueError('ExecutionContext must be explicitly provided')
# 		# config         = config or {}
# 		# file_path      = os.path.join(self.OPERATOR_DIR, f'{operator_name}.py')
# 		# operator_class = Module.find_class_by_base(Operator, file_path)

# 		# self._validate(operator_name, operator_class)

# 		# print('PUSHING Plugin ---------------->', operator_name)
# 		# context.push(operator_name, 1, 'plugin')

# 		# config_with_invoke = {
# 		# 	**config,
# 		# 	'invoke': self._invoke
# 		# }

# 		# try:
# 		# 	operator_context = self.dapi.operator_service.plugin_operator_functions
# 		# 	invoke           = self.dapi.operator_service.invoke
# 		# 	print(operator_context.keys())
# 		# 	operator_context.update(input.to_dict())
# 		# 	print(operator_context.keys())

# 		# 	op         = operator_class(invoke, context)
# 		# 	result     = await op.invoke(**operator_context)  # Magic!
# 		# 	expected   = output.schema.model_validate(result)

# 		# 	return output.from_dict(expected.model_dump())
# 		# except Exception as e:
# 		# 	import traceback
# 		# 	raise DapiException.consume(e)
# 		# finally:
# 		# 	context.pop()

# 		################################################################################

# 		if context is None: raise ValueError('ExecutionContext must be explicitly provided')
		
# 		config         = config or {}
# 		file_path      = os.path.join(self.OPERATOR_DIR, f'{operator_name}.py')
# 		operator_class = Module.find_class_by_base(Operator, file_path)

# 		self._validate(operator_name, operator_class)

# 		print('PUSHING Plugin ---------------->', operator_name)
# 		context.push(operator_name, 1, 'plugin')

# 		def call_external_operator(name, args):
# 			print('Calling external operator', name, args)
# 			exit()

# 		fullpy = FullPython(
# 			execution_context        = context,
# 			call_external_operator   = call_external_operator,
# 			exception_class          = Exception
# 		)
