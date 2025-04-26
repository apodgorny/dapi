from typing import Callable

from dapi.lib.datum             import Datum
from dapi.lib.autoargs          import autodecorate
from dapi.lib.execution_context import ExecutionContext


class Operator:
	'''Base interface for any executable operator: static, dynamic, composite.'''

	def __init__(self):
		pass

	# def __init__(self, invoke_operator, execution_context):
	# 	self.invoke_operator   = invoke_operator
	# 	self.execution_context = execution_context
	# 	autodecorate(self, ['invoke'])

	async def invoke(self) -> Datum:
		'''Execute operator and return output Datum.'''
		pass

	# @classmethod
	# def get_callable(
	# 	cls,
	# 	scope                 : dict[str, Callable],
	# 	invoke_operator       : Callable,
	# 	get_execution_context : Callable
	# ):
	# 	'''
	# 	Returns a function that accepts unpacked input arguments for the operator,
	# 	and injects the given scope (e.g., `call`, `log`, etc.) into its parameters.

	# 	This is meant to mirror interpreter-based execution with clean method calls.

	# 	Usage:
	# 		fn = MyOperator.get_callable(scope={'call': call})
	# 		await fn(x=1, y=2)  # call is automatically injected if expected
	# 	'''
	# 	if not hasattr(cls, 'InputType'):
	# 		raise ValueError(f'Operator `{cls.__name__}` must define an `InputType`')

	# 	field_names = list(cls.InputType.model_fields.keys())
	# 	scope_keys  = scope.keys()

	# 	async def callable_fn(*args, **kwargs):
	# 		# Map positional args to InputType field names
	# 		pos_map    = {k: v for k, v in zip(field_names, args)}
	# 		input_data = {**pos_map, **kwargs}
	# 		name       = cls.__name__.lower()

	# 		# Inject known names from scope if they match any expected parameter
	# 		matching_scope = {
	# 			k: v for k, v in scope.items()
	# 			if k not in input_data  # Don't override explicit input
	# 		}
	# 		input_data.update(matching_scope)
	# 		execution_context = get_execution_context()
	# 		print('PUSHING Plugin ---------------->', name)
	# 		execution_context.push(name, 1, 'plugin')

	# 		instance = cls(invoke_operator, execution_context)
	# 		return await instance.invoke(**input_data)

	# 	return callable_fn


	def __repr__(self) -> str:
		return f'<Operator {self.__class__.__name__}>'
