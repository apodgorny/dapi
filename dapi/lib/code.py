import os, ast, inspect
from pathlib import Path

from pydantic        import BaseModel
from dapi.lib        import String
from dapi.lib.module import Module


class Operator:
	interpreter = 'mini'
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
	def _get_code(node: ast.ClassDef, lines: list[str]) -> str:
		'''Return source of class node, unindented, without using inspect.'''
		start = node.lineno - 1
		end   = node.end_lineno
		src   = '\n'.join(lines[start:end])
		return String.unindent(src)

	@staticmethod
	def _get_interpreter(operator):
		if hasattr(operator, 'interpreter'):
			return operator.interpreter
		if not hasattr(operator, 'invoke'):
			return 'llm'
		return 'mini'

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
				operator       = getattr(module, node.name, None)
				class_name     = node.name
				operator_name  = String.camel_to_snake(class_name)
				input_type     = getattr(operator, 'InputType', None)
				output_type    = getattr(operator, 'OutputType', None)

				if not input_type or not output_type:
					raise ValueError(f'Operator `{operator_name}` missing InputType or OutputType')

				operators[operator_name] = {
					'name'        : operator_name,
					'class_name'  : class_name,
					'input_type'  : input_type.model_json_schema(),
					'output_type' : output_type.model_json_schema(),
					'code'        : Code._get_code(node, lines),
					'interpreter' : Code._get_interpreter(operator),
					'description' : 'Foobar',
					'config'      : {}
				}

		entry_name = String.camel_to_snake(getattr(module.Process.entry, '__name__'))

		return {
			'operators'  : operators,
			'entry_name' : entry_name
		}

