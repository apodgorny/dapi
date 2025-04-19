import os, sys, httpx
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dapi.lib import Datum


class Client:
	base_url = 'http://localhost:8000/dapi'
	
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
		color = Client._color(severity)
		Client.print(f'{color}{severity.upper()}{Client._reset()}: \x1B[3m{message}\x1B[0m')
		if severity == 'halt':
			exit(1)

	@staticmethod
	def request(method: str, path: str, **kwargs):
		Client.print('-' * 40)
		Client.print(f'Calling `{path}`')
		
		# Print request parameters if they exist
		if 'json' in kwargs:
			for key, val in kwargs['json'].items():
				Client.print(f'  {key:<14}: `{val}`')
		print()
		url = f'{Client.base_url}/{path.lstrip("/")}'
		
		# Set 2-minute timeout if not specified
		if 'timeout' not in kwargs:
			kwargs['timeout'] = 120.0  # 2 minutes in seconds
			
		try:
			res = httpx.request(method, url, **kwargs)
			res.raise_for_status()
			return res.json()
		except httpx.HTTPStatusError as e:
			try:
				detail   = e.response.json()['detail']
				message  = detail.get('message', 'Unknown error')
				severity = detail.get('severity', 'halt')
				Client.error(severity, message)
			except Exception:
				Client.print('Error:', e.response.text)

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
	def create_transaction(operator):
		return Client.request('POST', '/create_transaction', json={ 'operator': operator })

	@staticmethod
	def delete_transaction(tx_id: str):
		res = Client.request('POST', '/delete_transaction', json={ 'tx_id': tx_id })
		Client.success(f'transaction `{tx_id}` deleted')
		return res

	@staticmethod
	def assign(tx_id, from_, to):
		return Client.request('POST', '/create_transaction_assignment', json={
			'tx_id': tx_id,
			'from' : from_,
			'to'   : to
		})

	@staticmethod
	def invoke_transaction(tx_id):
		return Client.request('POST', '/invoke_transaction', json={ 'tx_id': tx_id })

	@staticmethod
	def invoke(name: str, input_data: dict):
		return Client.request('POST', '/invoke_operator', json={
			'name' : name,
			'input': input_data
		})
