import os
import inspect
from pathlib           import Path
from dapi.lib          import Datum, Interpreter
from dapi.lib.module   import Module
from dapi.lib.operator import Operator  # assuming the base class is defined here


class PluginInterpreter(Interpreter):
	'''Executes standalone plugin classes that extend Operator.

	The operator name must match a file in the operators directory (e.g. "square" loads operators/square.py)
	'''

	OPERATOR_DIR = os.path.join(
		os.environ.get('PROJECT_PATH'),
		os.environ.get('OPERATOR_DIR', 'operators')
	)

	async def invoke(
		self,
		operator_name : str,  # plugin file/module name (e.g. "square")
		code          : str,   # unused
		input         : Datum,
		output        : Datum,
		config        : dict = {}
	) -> Datum:
		file_path      = os.path.join(self.OPERATOR_DIR, f'{operator_name}.py')
		operator_class = Module.find_class_by_base(Operator, file_path)

		if not operator_class:
			raise ValueError(f'Plugin operator `{operator_name}` must be a subclass of `Operator`')

		if not hasattr(operator_class, 'invoke') or not callable(getattr(operator_class, 'invoke')):
			raise ValueError(f'Plugin operator `{operator_name}` must define static method `invoke(input)`')

		# Check if the invoke method is async
		if not inspect.iscoroutinefunction(operator_class.invoke):
			raise ValueError(f'Plugin operator `{operator_name}` must define an async invoke method')

		# Define a wrapper for operator_service.invoke that returns the actual output
		async def invoke_wrapper(name, data):
			result = await self.dapi.operator_service.invoke(name, data)
			# Extract the actual output from the result
			if isinstance(result, dict) and 'output' in result:
				return result['output']
			return result
			
		config_with_invoke = {**config, 'invoke': invoke_wrapper}

		try:
			# Pass input data and config to the plugin
			input_dict = input.to_dict()
			result     = await operator_class.invoke(input_dict, config_with_invoke)
			expected   = output.schema.model_validate(result)

			return output.from_dict(expected.model_dump())
		except Exception as e:
			import traceback
			raise ValueError(f'Execution error in `{operator_name}`: {e}\n{traceback.format_exc()}')
