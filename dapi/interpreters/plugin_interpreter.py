import sys
import os
import inspect

from pathlib           import Path
from dapi.lib          import Datum, Interpreter
from dapi.lib.module   import Module
from dapi.lib.operator import Operator  # assuming the base class is defined here


class PluginInterpreter(Interpreter):
	'''
	Executes standalone plugin classes that extend Operator.
	The operator name must match a file in the operators directory
	(e.g. "square" loads operators/square.py)
	'''

	OPERATOR_DIR = os.path.join(
		os.environ.get('PROJECT_PATH'),
		os.environ.get('OPERATOR_DIR', 'operators')
	)

	def _validate(self, operator_name, operator_class):
		if not operator_class:
			raise ValueError(f'Plugin operator `{operator_name}` must be a subclass of `Operator`')

		if not hasattr(operator_class, 'invoke') or not callable(getattr(operator_class, 'invoke')):
			raise ValueError(f'Plugin operator `{operator_name}` must define static method `invoke(input)`')

		if not inspect.iscoroutinefunction(operator_class.invoke):
			raise ValueError(f'Plugin operator `{operator_name}` must define an async invoke method')

	async def _invoke(name, data):
		result = await self.dapi.operator_service.invoke(name, data)
		if isinstance(result, dict) and 'output' in result:  # Extract the actual output from the result
			return result['output']
		return result

	# def inject_functions_to_plugin_operator_class(self, operator_class) -> None:
	# 	'''Inject functions into the actual Python module where the operator class is defined.'''
	# 	functions = self.dapi.operator_service.plugin_operator_functions
	# 	module    = sys.modules.get(operator_class.__module__)
	# 	if not module:
	# 		raise ImportError(f'Cannot locate module for {operator_class.__module__}')

	# 	for name, fn in functions.items():
	# 		setattr(module, name, fn)

	async def invoke(
		self,
		operator_name : str,   # plugin file/module name (e.g. "square")
		code          : str,   # unused
		input         : Datum,
		output        : Datum,
		config        : dict = {}
	) -> Datum:

		file_path          = os.path.join(self.OPERATOR_DIR, f'{operator_name}.py')
		operator_class     = Module.find_class_by_base(Operator, file_path)

		self._validate(operator_name, operator_class)

		# # Inject plugin functions as globals (e.g. call, print, main, etc.)
		# print('injecting', file_path)
		# self.inject_functions_to_plugin_operator_class(operator_class)

		config_with_invoke = {
			**config,
			'invoke': self._invoke
		}
		
		try:
			# Pass input data and config to the plugin
			input_dict = input.to_dict()
			result     = await operator_class.invoke(input_dict, config_with_invoke)
			expected   = output.schema.model_validate(result)

			return output.from_dict(expected.model_dump())
		except Exception as e:
			import traceback
			raise ValueError(f'Execution error in `{operator_name}`: {e}\n{traceback.format_exc()}')
