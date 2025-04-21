import os, ast, inspect
from pathlib import Path

from pydantic        import BaseModel
from dapi.lib        import String
from dapi.lib.module import Module


class OperatorDefinition:
	interpreter = 'python'
	def invoke(input):
		pass


class Code:
	@staticmethod
	def _is_operator_class(node):
		return any((getattr(base, 'id', '') == 'OperatorDefinition') for base in node.bases)

	@staticmethod
	def _is_class(node):
		return isinstance(node, ast.ClassDef)

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
				code     = inspect.getsource(operator.invoke).replace('invoke', operator.__name__, 1)
				operators[node.name] = {
					'name'        : node.name,
					'input_type'  : operator.InputType.model_json_schema(),
					'output_type' : operator.OutputType.model_json_schema(),
					'code'        : String.unindent(code),
					'interpreter' : 'python',
					'config'      : {}
				}

		entry_name  = getattr(module.Process.entry, '__name__')

		print('operators', operators)

		return {
			'operators'  : operators,
			'entry_name' : entry_name
		}
