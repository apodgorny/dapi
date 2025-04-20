import os, sys, httpx, json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from .datum  import Datum
from .code   import Code
from .module import Module

PROJECT_PATH = os.environ.get('PROJECT_PATH')
DAPI_CODE    = os.path.join(PROJECT_PATH, os.environ.get('DAPI_CODE'))
DAPI_URL     = os.environ.get('DAPI_URL')


class Client:

	@staticmethod
	def print(*args, **kwargs):
		kwargs['flush'] = True
		print(*args, **kwargs)

	@staticmethod
	def _color(severity):
		return {
			'fyi'    : '\033[94m',
			'beware' : '\033[93m',
			'halt'   : '\033[91m',
			'success': '\033[92m'
		}.get(severity, '')

	@staticmethod
	def _reset():
		return '\033[0m'

	@staticmethod
	def success(message):
		Client.print(f"{Client._color('success')}✓ {message}{Client._reset()}")

	@staticmethod
	def error(severity, message):
		color   = Client._color(severity)
		message = message.replace('\\n', '\n')
		Client.print(f'{color}{severity.upper()}{Client._reset()}: \x1B[3m{message}\x1B[0m')
		if severity == 'halt':
			exit(1)

	@staticmethod
	def request(method: str, path: str, **kwargs):
		Client.print('-' * 40)
		Client.print(f'Calling `{path}`')

		if 'json' in kwargs:
			for key, val in kwargs['json'].items():
				Client.print(f'  {key:<14}: `{val}`')
		print()
		url = f'{DAPI_URL}/{path.lstrip("/")}'

		if 'timeout' not in kwargs:
			kwargs['timeout'] = 1200.0

		try:
			res = httpx.request(method, url, **kwargs)
			res.raise_for_status()
			return res.json()
		except httpx.ConnectError as e:
			Client.error('halt', e)
		except httpx.HTTPStatusError as e:
			try:
				print(json.dumps(e.__dict__, indent=4))
				detail   = e.response.json()['detail']
				message  = detail.get('message', 'Unknown error')
				severity = detail.get('severity', 'halt')
				Client.error(severity, message)
			except Exception:
				Client.print('Error:', e.response.text.replace('\\n', '\n').replace('\\', ''))

	############################################################################

	@staticmethod
	def create_type(name: str, model: Datum.Pydantic):
		schema = Datum(model).to_dict(schema=True)
		res = Client.request('POST', '/create_type', json={
			'name'  : name,
			'schema': schema
		})
		Client.success(f'type `{name}` created')
		return res

	@staticmethod
	def delete_type(name: str):
		res = Client.request('POST', '/delete_type', json={ 'name': name })
		Client.success(f'type `{name}` deleted')
		return res

	@staticmethod
	def list_types():
		return Client.request('GET', '/list_types')

	@staticmethod
	def create_operator(name, input_type, output_type, code, interpreter, config=None):
		data = {
			'name'       : name,
			'input_type' : input_type,
			'output_type': output_type,
			'code'       : code,
			'interpreter': interpreter
		}
		if config is not None:
			data['config'] = config

		res = Client.request('POST', '/create_operator', json=data)
		Client.success(f'operator `{name}` created')
		return res

	@staticmethod
	def delete_operator(name: str):
		res = Client.request('POST', '/delete_operator', json={ 'name': name })
		Client.success(f'operator `{name}` deleted')
		return res

	@staticmethod
	def list_operators():
		return Client.request('GET', '/list_operators')

	@staticmethod
	def invoke(name: str, input_data: dict):
		return Client.request('POST', '/invoke_operator', json={
			'name'  : name,
			'input' : input_data
		})

	##################################################################################

	@staticmethod
	def compile(code_path):
		# self.reset()
		definitions = Code.serialize(code_path)

		entry_name = definitions.get('entry_name')
		if entry_name:
			entry_io = definitions['functions'][entry_name]
			for type_name in [entry_io['input_type'], entry_io['output_type']]:
				if type_name not in definitions['types']:
					raise TypeError(f'Type `{type_name}` is not defined in `{code_path}`')
		else:
			raise ValueError(f'Entry point is not defined in process `{code_path}`')
		
		for type_name, type_data in definitions['types'].items():
			model = type(type_name, (Datum.Pydantic,), {})
			model.model_json_schema = lambda: type_data['schema']
			Client.create_type(type_name, model)

		for op_name, op_data in definitions['functions'].items():
			Client.create_operator(
				name        = op_name,
				input_type  = op_data['input_type'],
				output_type = op_data['output_type'],
				code        = op_data['code'],
				interpreter = op_data['interpreter'],
				config      = op_data.get('config')
			)

		return definitions

	@staticmethod
	def reset():
		print("RESET")
		for operator in Client.list_operators():
			Client.delete_operator(operator['name'])
		for type_ in Client.list_types():
			Client.delete_type(type_['name'])
