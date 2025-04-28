from typing import Callable

from dapi.lib.datum             import Datum
from dapi.lib.string            import String
from dapi.lib.autoargs          import autodecorate
from dapi.lib.execution_context import ExecutionContext


class Operator:
	'''Base interface for any executable operator: static, dynamic, composite.'''

	@property
	def input_type(self):
		return self.__class__.InputType

	@property
	def output_type(self):
		return self.__class__.OutputType

	@property
	def name(self):
		return String.camel_to_snake(self.__class__.__name__)

	@classmethod
	def input_fields(cls) -> list[str]:
		return list(cls.InputType.model_fields.keys())

	@classmethod
	def output_fields(cls) -> list[str]:
		return list(cls.OutputType.model_fields.keys())

	def __init__(
		self,
		call_external_operator = None,
		get_operator_class     = None,
		real_print             = None
	):
		self.call_external_operator = call_external_operator
		self.get_operator_class     = get_operator_class
		self.print                  = real_print

	async def invoke(self) -> Datum:
		'''Execute operator and return output Datum.'''
		pass

	# def impose_output_fields(self, input, fields, from_operator):
	# 	model_a = self.__class__.InputType
	# 	fields_a = {n: f.annotation for n, f in self.input_type.model_fields.items()}
	# 	fields_b = {n: f.annotation for n, f in model.model_fields.items()}
		
	# 	missing  = fields_b.keys() - fields_a.keys()
	# 	extra    = fields_a.keys() - fields_b.keys()
	# 	mismatch = {n: (fields_a[n].__name__, fields_b[n].__name__) for n in fields_a.keys() & fields_b.keys() if fields_a[n] != fields_b[n]}
		
	# 	if missing or extra or mismatch:
	# 		parts = []
	# 		if missing:
	# 			parts.append(f'Input fields {missing} must be present in {self.name}')
	# 		if extra:
	# 			parts.append(f'Extra in {self.name}: {extra}')
	# 		if mismatch:
	# 			parts.append(f'Type mismatches in model_a: {mismatch}')
	# 		raise ValueError('Model_a inconsistency:\n' + '\n'.join(parts))

	# 	return True


	def __repr__(self) -> str:
		return f'<Operator {self.__class__.__name__}>'
