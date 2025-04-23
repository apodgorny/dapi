import os, ast, inspect
from pathlib import Path

from pydantic        import BaseModel
from dapi.lib        import String
from dapi.lib.module import Module


class Operator:
	interpreter = 'python'
	def invoke(input):
		pass


class Code:
	@staticmethod
	def _is_operator_class(node):
		return any((getattr(base, 'id', '') == 'Operator') for base in node.bases)

	@staticmethod
	def _is_class(node):
		return isinstance(node, ast.ClassDef)

	@staticmethod
	def _get_code(operator, operator_name):
		interpreter = Code._get_interpreter(operator)
		code = ''
		if interpreter == 'llm':
			code = operator.code
		else:
			code = inspect.getsource(operator.invoke).replace('invoke', operator_name, 1)
		return String.unindent(code)

	@staticmethod
	def _get_interpreter(operator):
		if hasattr(operator, 'interpreter'):
			return operator.interpreter
		if not hasattr(operator, 'invoke'):
			return 'llm'
		return 'python'

	@staticmethod
	def serialize(path: str) -> dict:
		text        = Path(path).read_text()
		tree        = ast.parse(text)
		lines       = text.splitlines()
		module_name = os.path.splitext(os.path.basename(path))[0]
		module      = Module.import_module(module_name, path)

		operators = {}

		for node in tree.body:
			if Code._is_class(node) and Code._is_operator_class(node):
				operator = getattr(module, node.name, None)
				operator_name = String.camel_to_snake(node.name)
				operators[operator_name] = {
					'name'        : operator_name,
					'input_type'  : operator.InputType.model_json_schema(),
					'output_type' : operator.OutputType.model_json_schema(),
					'code'        : Code._get_code(operator, operator_name),
					'interpreter' : Code._get_interpreter(operator),
					'config'      : {}
				}

		entry_name  = String.camel_to_snake(getattr(module.Process.entry, '__name__'))

		return {
			'operators'  : operators,
			'entry_name' : entry_name
		}
