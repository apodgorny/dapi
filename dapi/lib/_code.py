import ast
import json
from pathlib import Path
from pydantic import BaseModel
from typing import Any, Dict

from dapi.lib import String


class Code:
	@staticmethod
	def _get_function_definition(node: ast.FunctionDef, code_lines: list[str]) -> dict:
		name  = node.name
		print('----------', name)
		start = node.lineno - 1
		end   = max(getattr(n, 'end_lineno', getattr(n, 'lineno', 0)) for n in ast.walk(node))  # use end_lineno for full body span
		code  = '\n'.join(code_lines[start:end])

		try:
			local_env = {}
			exec(code, local_env)
			func = local_env.get(name)
			if callable(func):
				result = func({})
				if isinstance(result, dict) and 'interpreter' in result:
						if isinstance(result.get('code'), str):
							code_str = String.unindent(result['code'])
						else:
							code_str = code
						return {
						'name'        : name,
						'input_type'  : f'{name}_input',
						'output_type' : f'{name}_output',
						'code': code_str,
						'interpreter' : result['interpreter'],
						'config'      : result.get('config', {})
					}
		except Exception as e:
			print(str(e))

		return {
			'name'        : name,
			'input_type'  : f'{name}_input',
			'output_type' : f'{name}_output',
			'code'        : code,
			'interpreter' : 'python',
			'config'      : {}
		}
			
	@staticmethod
	def _get_type_definition(name: str, local_env: dict) -> dict:
		model = local_env[name]
		return {
			'name'   : name,
			'schema' : model.model_json_schema()
		}

	@staticmethod
	def serialize(path: str) -> dict:
		'''Extracts all standalone functions and Pydantic types from a Python file'''
		code       = Path(path).read_text()
		tree       = ast.parse(code)
		code_lines = code.splitlines()
		local_env: Dict[str, Any] = {}
		exec(code, local_env)

		functions = {}
		types     = {}

		for node in tree.body:
			if isinstance(node, ast.FunctionDef):
				functions[node.name] = Code._get_function_definition(node, code_lines)

			elif isinstance(node, ast.ClassDef):
				bases = [base.id for base in node.bases if isinstance(base, ast.Name)]
				if 'BaseModel' in bases and node.name in local_env:
					types[node.name] = Code._get_type_definition(node.name, local_env)

		return {
			'functions': functions,
			'types'    : types
		}
