import httpx


class Client:
	base_url = 'http://localhost:8000/dapi'

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
		print(f"{Client._color('success')}✓ {message}{Client._reset()}")

	@staticmethod
	def error(severity, message):
		color = Client._color(severity)
		print(f'{color}{severity.upper()}{Client._reset()}: \x1B[3m{message}\x1B[0m')
		if severity == 'halt':
			exit(1)

	@staticmethod
	def request(method: str, path: str, **kwargs):
		url = f'{Client.base_url}/{path.lstrip("/")}'
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
				print('Error:', e.response.text)

	############################################################################

	@staticmethod
	def create_type(name: str, schema: dict):
		res = Client.request('POST', '/create_type', json={
			'name'       : name,
			'json_schema': schema
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
	def create_operator(name, input_type, output_type, code, interpreter):
		res = Client.request('POST', '/create_operator', json={
			'name'       : name,
			'input_type' : input_type,
			'output_type': output_type,
			'code'       : code,
			'interpreter': interpreter
		})
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