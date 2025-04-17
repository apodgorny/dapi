import os
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
		file_path = os.path.join(self.OPERATOR_DIR, f'{operator_name}.py')
		klass     = Module.find_class_by_base(Operator, file_path)

		if not klass:
			raise ValueError(f'Plugin `{operator_name}` does not define a subclass of `Operator`')

		if not hasattr(klass, 'invoke') or not callable(getattr(klass, 'invoke')):
			raise ValueError(f'Plugin `{operator_name}` must define static method `invoke(input)`')

		try:
			# Pass input data and config to the plugin
			result   = klass.invoke(input.to_dict(), config)
			expected = output.schema.model_validate(result)
			return output.from_dict(expected.model_dump())
		except Exception as e:
			raise ValueError(f'Execution error in `{operator_name}`: {e}')
