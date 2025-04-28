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
			'interpreter' : getattr(operator_class, 'interpreter', 'full'),
			'description' : inspect.getdoc(operator_class) or '',
			'config'      : getattr(operator_class, 'config', {})
		}

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
	def request(method: str, path: str, **kwargs):
		url = f'{DAPI_URL}/{path.lstrip("/")}'
		kwargs.setdefault('timeout', 1200.0)
		try:
			res = httpx.request(method, url, **kwargs)
			res.raise_for_status()
			return res.json()
		except httpx.ConnectError as e:
			raise ConnectionError(f'Failed to connect to DAPI server: {e}')
		except httpx.HTTPStatusError as e:
			severity, message, trace = WordWield._extract_dapi_error(e.response)
			raise RuntimeError(f'{severity.upper()}: {message}\n{trace or ""}')

	####################################################################################

	@staticmethod
	def create_operator(operator_class):
		'''Create and register an operator from a local Python class.'''
		source = WordWield.serialize_operator_class(operator_class)
		data = {
			'name'        : source['name'],
			'class_name'  : source['class_name'],
			'input_type'  : source['input_type'],
			'output_type' : source['output_type'],
			'code'        : source['code'],
			'interpreter' : source['interpreter'],
			'description' : source.get('description', '')
		}
		if 'config' in source:
			data['config'] = source['config']

		return WordWield.request('POST', '/create_operator', json=data)

	@staticmethod
	def invoke(name: str, input_data: dict):
		'''Invoke an existing operator by name.'''
		return WordWield.request('POST', f'{name}', json=input_data)


# Alias for easy import
ww = WordWield
