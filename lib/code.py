import inspect

from lib import Operator, O, String


class Code:
	'''Encapsulates all code generation and inspection logic for operators and types.'''

	type_pool     = {}
	operator_pool = {}

	@staticmethod
	def get_code_and_schema(obj):
		try:
			code = String.unindent(inspect.getsource(obj))
		except TypeError as e:
			raise ValueError(f'Cannot get source code of `{obj.__name__}`. Ensure it is imported normally.') from e

		if issubclass(obj, Operator):
			input_type  = obj.InputType.to_schema()  if hasattr(obj, 'InputType')  else {}
			output_type = obj.OutputType.to_schema() if hasattr(obj, 'OutputType') else {}
			return {
				'name'        : String.to_snake_case(obj.__name__),
				'class_name'  : obj.__name__,
				'input_type'  : input_type,
				'output_type' : output_type,
				'code'        : code,
				'description' : inspect.getdoc(obj) or '',
				'config'      : getattr(obj, 'config', {})
			}
		else:
			raise TypeError('Unsupported object type for code and schema extraction')

	@staticmethod
	def collect_operators(objects):
		Code.operator_pool = {
			String.to_snake_case(obj.__name__): Code.get_code_and_schema(obj)
			for name, obj in objects.items()
			if inspect.isclass(obj)
			and issubclass(obj, Operator)
			and obj is not Operator
			and name not in ['Agent', 'AgentOnGrid']
		}
		return list(Code.operator_pool.values())

	@staticmethod
	def collect_types(objects):
		Code.type_pool = {}
		seen = {}

		def collect(cls):
			name = cls.__name__
			if name in seen:
				return seen[name]

			if not inspect.isclass(cls) or not issubclass(cls, O):
				raise TypeError(f'Cannot collect non-O type: {cls}')

			entry = {
				'name'        : name,
				'class_name'  : name,
				'code'        : String.unindent(inspect.getsource(cls)),
				'description' : inspect.getdoc(cls) or ''
			}

			Code.type_pool[name] = entry
			seen[name] = entry
			return entry

		#################################

		for name, obj in objects.items():
			if inspect.isclass(obj):
				if issubclass(obj, O) and obj is not O:
					collect(obj)

		return list(Code.type_pool.values())

