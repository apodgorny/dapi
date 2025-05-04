import os, sys, inspect, httpx, ast, json

from pathlib    import Path

from .string    import String
from .highlight import Highlight

from dapi.lib   import Operator, Agent, AgentOnGrid, Datum, O


PROJECT_PATH = os.environ.get('PROJECT_PATH')
DAPI_CODE    = os.path.join(PROJECT_PATH, os.environ.get('DAPI_CODE'))
DAPI_URL     = os.path.join(os.environ.get('DAPI_URL'))


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
			input_type  = Datum(obj.InputType).to_dict(schema=True)  if hasattr(obj, 'InputType')  else {}
			output_type = Datum(obj.OutputType).to_dict(schema=True) if hasattr(obj, 'OutputType') else {}
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

			# Start with shallow schema
			schema = Datum(cls).to_dict(schema=True)

			# Recursively replace $ref with actual type schemas
			def inline_refs(obj):
				if isinstance(obj, dict):
					if '$ref' in obj:
						ref_name = obj['$ref'].split('/')[-1]
						if ref_name not in objects:
							raise ValueError(f'Referenced type `{ref_name}` not found in objects')
						ref_cls = objects[ref_name]
						ref_schema = collect(ref_cls)['type_schema']
						return ref_schema
					return {k: inline_refs(v) for k, v in obj.items()}
				elif isinstance(obj, list):
					return [inline_refs(i) for i in obj]
				else:
					return obj

			final_schema = inline_refs(schema)

			entry = {
				'name'        : name,
				'class_name'  : name,
				'type_schema' : final_schema,
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


class WordWield:
	VERBOSE = True

	# Private methods
	############################################################################

	@staticmethod
	def _create_type(type_dict):
		res = WordWield.request('POST', '/create_type', json=type_dict)
		WordWield.success(f'Type `{type_dict["name"]}` created')
		return res

	@staticmethod
	def _create_operator(operator_dict):
		res = WordWield.request('POST', '/create_operator', json=operator_dict)
		WordWield.success(f'Operator `{operator_dict["name"]}` created')
		return res

	@staticmethod
	def _color(severity):
		return {
			'fyi'    : String.LIGHTBLUE,
			'beware' : String.LIGHTYELLOW,
			'halt'   : String.LIGHTRED,
			'success': String.LIGHTGREEN
		}.get(severity, '')

	@staticmethod
	def _extract_dapi_error(response: httpx.Response):
		data = response.json()
		try:
			detail      = data.get('detail', {})
			severity    = detail.get('severity', 'halt')
			message_raw = detail.get('detail', 'Unknown error')
			trace       = detail.get('trace')

			try:
				parsed = ast.literal_eval(message_raw)
				if isinstance(parsed, dict) and 'detail' in parsed:
					message = parsed['detail']
				else:
					message = message_raw
			except Exception:
				message = message_raw

			error_type = detail.get('error_type')
			operator   = detail.get('operator')
			lineno     = detail.get('line')
			filename   = detail.get('file')
			short_file = Path(filename).name if filename else None

			parts = []
			if error_type : parts.append(error_type)
			if operator   : parts.append(f'operator: {operator}')
			if lineno     : parts.append(f'line: {lineno}')
			if short_file : parts.append(f'file: {short_file}')

			if parts:
				message += f' ({", ".join(parts)})'

			return severity, message, trace

		except Exception as e:
			return 'halt', f'Could not parse DAPI error: {e}\nOriginal error: {json.dumps(data, indent=4)}', None

	# Public methods
	############################################################################

	@staticmethod
	def init():
		'''Create all Operator and O-descendant types defined in the caller scope.'''
		frame     = inspect.currentframe().f_back
		module    = inspect.getmodule(frame)
		objects   = vars(sys.modules[module.__name__])

		operators = Code.collect_operators(objects)

		Code.collect_types(objects)  # populates type_pool including nested

		for type_def in Code.type_pool.values():  # includes all, not just roots
			WordWield._create_type(type_def)

		for op_def in operators:
			WordWield._create_operator(op_def)

	@staticmethod
	def print(*args, **kwargs):
		kwargs['flush'] = True
		color = kwargs.pop('color', None)
		if color:
			args = [String.color(arg, color) for arg in args]
		print(*args, **kwargs)

	@staticmethod
	def success(message):
		if WordWield.VERBOSE:
			prefix = String.color('SUCCESS:', String.LIGHTGREEN)
			WordWield.print(f'{prefix} {message}')

	@staticmethod
	def error(severity, message):
		if not WordWield.VERBOSE:
			return
		prefix = String.color(severity.upper() + ':', WordWield._color(severity))
		message = str(message).replace('\n', '\n')
		WordWield.print(f'{prefix} {message}')

	@staticmethod
	def request(method: str, path: str, **kwargs):
		url = f'{DAPI_URL}/{path.lstrip("/")}'
		kwargs.setdefault('timeout', 1200.0)

		if WordWield.VERBOSE:
			bar = f'  {"- " * 22}'
			WordWield.print('\n' + ('-' * 45))
			WordWield.print(String.underlined(f'Calling `{path}`'))
			if 'json' in kwargs:
				WordWield.print(f'\n{bar}', color=String.DARK_GRAY)
				for key, val in kwargs['json'].items():
					WordWield.print(f'  {key:<16}{String.color(":", String.GRAY)} ', end='')
					if isinstance(val, dict):
						val = json.dumps(val, indent=2, ensure_ascii=False)
						val = Highlight.python(val)
						WordWield.print()
						for line in val.splitlines():
							WordWield.print(f'    {line}')
					else:
						val = Highlight.python(str(val))
						WordWield.print(val)
				WordWield.print(bar, color=String.DARK_GRAY)

		try:
			res = httpx.request(method, url, **kwargs)
			res.raise_for_status()
			return res.json()
		except httpx.HTTPStatusError as e:
			severity, message, trace = WordWield._extract_dapi_error(e.response)
			WordWield.error(severity, message)
			if trace:
				WordWield.print(String.color(trace, String.GRAY))
			if severity == 'halt':
				exit(1)
		except Exception as e:
			WordWield.error('halt', str(e))
			exit(1)

	@staticmethod
	def invoke(operator: Operator, *args, **kwargs):
		name = String.camel_to_snake(operator.__name__)
		if len(args) == 1 and isinstance(args[0], dict) and not kwargs:
			input_data = args[0]
		else:
			input_data = kwargs

		result = WordWield.request('POST', f'{name}', json=input_data)
		result = result['output']
		WordWield.success(f'Invoked operator `{name}`:\n')
		WordWield.print(Highlight.python(json.dumps(result, ensure_ascii=False, indent=4)))

		if isinstance(result, dict) and hasattr(operator, 'OutputType') and issubclass(operator.OutputType, O):
			return json.dumps(result, indent=4, ensure_ascii=False)

		result = tuple(result[k] for k in result)
		if len(result) == 1:
			result = result[0]
		return result
