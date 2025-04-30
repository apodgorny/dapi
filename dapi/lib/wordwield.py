import os, sys, inspect, httpx, ast, json
from pathlib import Path

from .string    import String
from .highlight import Highlight
from .datum     import Datum


PROJECT_PATH = os.environ.get('PROJECT_PATH')
DAPI_CODE    = os.path.join(PROJECT_PATH, os.environ.get('DAPI_CODE'))
DAPI_URL     = os.environ.get('DAPI_URL')


class Operator:
	pass


class WordWield:
	VERBOSE = True

	####################################################################################

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
		message = str(message).replace('\\n', '\n')
		WordWield.print(f'{prefix} {message}')

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

	####################################################################################

	@staticmethod
	def serialize_operator_class(operator_class):
		'''Serializes a single Python class to operator definition.'''
		try:
			code = String.unindent(inspect.getsource(operator_class))
		except TypeError as e:
			raise ValueError(f'Cannot get source code of `{operator_class.__name__}`. Ensure it is imported normally.') from e

		return {
			'name'        : String.to_snake_case(operator_class.__name__),
			'class_name'  : operator_class.__name__,
			'input_type'  : Datum(operator_class.InputType).to_dict(schema=True),
			'output_type' : Datum(operator_class.OutputType).to_dict(schema=True),
			'code'        : code,
			'description' : inspect.getdoc(operator_class) or '',
			'config'      : getattr(operator_class, 'config', {})
		}

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
	def create_operator(operator_class):
		source = WordWield.serialize_operator_class(operator_class)
		data = {
			'name'        : source['name'],
			'class_name'  : source['class_name'],
			'input_type'  : source['input_type'],
			'output_type' : source['output_type'],
			'code'        : source['code'],
			'description' : source.get('description', '')
		}
		if 'config' in source:
			data['config'] = source['config']

		res = WordWield.request('POST', '/create_operator', json=data)
		WordWield.success(f'Operator `{data["name"]}` created')
		return res

	@staticmethod
	def init():
		'''Create all Operator subclasses defined in the caller scope.'''
		# 1. Получить frame, в котором вызван init()
		frame = inspect.currentframe().f_back
		locals_dict = frame.f_locals

		# 2. Пройтись по всем локальным классам
		for name, obj in locals_dict.items():
			if (
				inspect.isclass(obj)
				and issubclass(obj, Operator)
				and obj is not Operator
			):
				WordWield.create_operator(obj)

	@staticmethod
	def invoke(name: str, input_data: dict):
		res = WordWield.request('POST', f'{name}', json=input_data)
		WordWield.success(f'Invoked operator `{name}`:\n')
		WordWield.print(Highlight.python(json.dumps(res, ensure_ascii=False, indent=4)))
		return res


# Alias for easy import
ww = WordWield