import os, sys, httpx, json, ast
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from .datum  import Datum
from .code   import Code
from .module import Module
from .string import String

PROJECT_PATH = os.environ.get('PROJECT_PATH')
DAPI_CODE    = os.path.join(PROJECT_PATH, os.environ.get('DAPI_CODE'))
DAPI_URL     = os.environ.get('DAPI_URL')


class Client:

	####################################################################################

	@staticmethod
	def print(*args, **kwargs):
		kwargs['flush'] = True
		color = kwargs.pop('color', None)
		if color:
			args = [String.color(arg, color) for arg in args]
		print(*args, **kwargs)

	@staticmethod
	def _color(severity):
		return {
			'fyi'    : String.LIGHTBLUE,
			'beware' : String.LIGHTYELLOW,
			'halt'   : String.LIGHTRED,
			'success': String.LIGHTGREEN
		}.get(severity, '')

	@staticmethod
	def _highlight(s):
		s = String.highlight(s, {
			String.CYAN    : 'async def self return await class float int str bool'.split(),
			String.GRAY    : '{ } [ ] : = - + * /, . ; \" \''.split(),
			String.MAGENTA : '( )'.split()
		})
		s = String.color_between(s, '#', '\n', String.GRAY)
		return s

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

			# Append trace as a separate element to be printed later
			return severity, message, trace

		except Exception as e:
			return 'halt', f'Could not parse DAPI error: {e}\nOriginal error: {json.dumps(data, indent=4)}', None



	####################################################################################

	@staticmethod
	def success(message):
		prefix = String.color('SUCCESS:', Client._color('success'))
		Client.print(f'{prefix} {message}')

	@staticmethod
	def error(severity, message):
		message = str(message).replace('\\n', '\n')
		prefix  = String.color(severity.upper() + ':', Client._color(severity))

		if '\nTraceback' in message:
			head, trace = message.split('\nTraceback', 1)
			Client.print(f'{prefix} {head}')
			Client.print(String.color('Traceback' + trace, String.GRAY))
		else:
			Client.print(f'{prefix} {message}')

		if severity == 'halt':
			exit(1)

	@staticmethod
	def request(method: str, path: str, **kwargs):
		Client.print('\n' + ('-' * 45) + '\n')
		Client.print(String.underlined(f'Calling `{path}`'))
		bar = f'  {"- " * 22}'
		if 'json' in kwargs:
			Client.print(f'\n{bar}', color=String.DARK_GRAY)
			for key, val in kwargs['json'].items():
				Client.print(f'  {key:<16}{String.color(":", color=String.GRAY)} ', end='')
				if len(str(val)) < 20:
					val = Client._highlight(str(val))
					Client.print(f'`{val}`')
					Client.print(bar, color=String.DARK_GRAY)
				elif isinstance(val, dict):
					val = '    ' + json.dumps(val, indent=4).replace('\n', '\n    ')
					val = Client._highlight(val)
					Client.print(f'\n{bar}', color=String.DARK_GRAY)
					print(val)
					Client.print(bar, color=String.DARK_GRAY)
				else:
					val = str(val).strip()
					val = Client._highlight(val)
					Client.print(f'\n{bar}', color=String.DARK_GRAY)
					Client.print(f'    {val}')
					Client.print(bar, color=String.DARK_GRAY)

		print()
		url = f'{DAPI_URL}/{path.lstrip("/")}'
		kwargs.setdefault('timeout', 1200.0)

		try:
			res = httpx.request(method, url, **kwargs)
			res.raise_for_status()
			return res.json()
		except httpx.ConnectError as e:
			Client.error('halt', e)
		except httpx.HTTPStatusError as e:
			severity, message, trace = Client._extract_dapi_error(e.response)
			Client.print(
				f'{String.color(severity.upper(), Client._color(severity))}: {message}'
			)
			if trace:
				Client.print(String.color(trace, String.GRAY))
			if severity == 'halt':
				exit(1)

	@staticmethod
	def create_operator(name, class_name, input_type, output_type, code, interpreter, description, config=None):
		data = {
			'name'        : name,
			'class_name'  : class_name,
			'input_type'  : input_type,
			'output_type' : output_type,
			'code'        : code,
			'interpreter' : interpreter,
			'description' : description
		}
		if config is not None:
			data['config'] = config

		res = Client.request('POST', '/create_operator', json=data)
		Client.success(f'Operator `{name}` created')
		return res

	@staticmethod
	def delete_operator(name: str):
		res = Client.request('POST', '/delete_operator', json={ 'name': name })
		Client.success(f'Operator `{name}` deleted')
		return res

	@staticmethod
	def list_operators():
		return Client.request('POST', '/list_operators', json={})

	@staticmethod
	def invoke(name: str, input_data: dict):
		res = Client.request('POST', f'/{name}', json=input_data)
		Client.success(f'Invoked operator `{name}`:\n')
		Client.print(Client._highlight(json.dumps(res, indent=4)))
		return res

	@staticmethod
	def reset():
		res = Client.request('POST', '/reset', json={})
		Client.success(f'{res}')

	@staticmethod
	def compile(code_path):
		definitions = Code.serialize(code_path)
		for op_name, op_data in definitions['operators'].items():
			Client.create_operator(**op_data)

		return definitions
