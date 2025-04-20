import re
import json
import codecs
import asyncio
import ollama
from pydantic import BaseModel

from dapi.lib import Model


class ModelOllama(Model):
	def __init__(self, name: str):
		self.name = name
		self.client = ollama

	def _sanitize_output(self, output: str) -> str:
		output = re.sub(r'<0x([0-9a-fA-F]{2})>', lambda m: chr(int(m[1], 16)), output)
		output = re.sub(r'\\u[0-9a-fA-F]{4}', lambda m: codecs.decode(m[0], 'unicode_escape'), output)
		try:
			output = output.encode('latin1').decode('utf-8')
		except UnicodeError:
			pass
		return output

	async def __call__(
		self,
		prompt          : str,
		response_schema : BaseModel,
		role            : str = 'user',
		temperature     : float = 0.0,
		system          : str | None = None
	) -> dict:
		params = {
			"model": self.name,
			"messages": [{
				"role": role,
				"content": prompt
			}],
			"format": response_schema.model_json_schema(),
			"options": {
				"temperature": temperature,
				"keep_alive": 60
			}
		}

		if system:
			params["messages"].insert(0, {"role": "system", "content": system})

		response = await asyncio.to_thread(self.client.chat, **params)
		text     = response['message']['content']
		sanitized = self._sanitize_output(text)
		return json.loads(sanitized)
