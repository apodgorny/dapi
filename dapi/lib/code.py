import os, ast
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
	def _get_operator_class_definition(node: ast.ClassDef, lines: list[str], input_type: str, output_type: str) -> dict:
		name        = node.name
		interpreter = 'python'
		config      = {}

		# Extract function body from 'invoke'
		body = '# invoke method not found'
		for item in node.body:
			if isinstance(item, ast.FunctionDef) and item.name == 'invoke':
				start = item.lineno - 1
				end   = max(getattr(n, 'end_lineno', getattr(n, 'lineno', 0)) for n in ast.walk(item))
				block = [f'def {name}(input):'] + lines[start + 1:end]
				body  = String.unindent('\n'.join(block))
				break

		# Extract inline overrides (interpreter, code, config)
		for stmt in node.body:
			if not isinstance(stmt, ast.Assign): continue
			for target in stmt.targets:
				if not isinstance(target, ast.Name): continue
				id, value = target.id, stmt.value
				if id == 'interpreter' and isinstance(value, ast.Constant):
					interpreter = value.value
				elif id == 'code' and isinstance(value, ast.Constant):
					body = String.unindent(value.value)
				elif id == 'config':
					try:    config = ast.literal_eval(value)
					except: config = {}

		return {
			'name'        : name,
			'input_type'  : input_type,
			'output_type' : output_type,
			'code'        : body,
			'interpreter' : interpreter,
			'config'      : config
		}

	@staticmethod
	def _get_type_definition(node: ast.ClassDef, env: dict) -> dict:
		name = node.name
		try:    schema = env[name].model_json_schema()
		except: schema = { '$comment': 'Failed to load model schema' }
		return { 'name': name, 'schema': schema }

	@staticmethod
	def _get_entry_point(module_name, path: str) -> str:
		module = Module.import_module(module_name, path)
		if not hasattr(module, 'Process'):
			raise ValueError(f'File `{path}` does not define class `Process`')
		process = getattr(module, 'Process')
		if not isinstance(process, type):
			raise ValueError(f'`Process` in `{path}` is not a class')
		if not hasattr(process, 'entry'):
			raise ValueError(f'`Process` class in `{path}` does not define `entry` attribute')
		return getattr(process, 'entry').__name__

	@staticmethod
	def serialize(path: str) -> dict:
		text        = Path(path).read_text()
		tree        = ast.parse(text)
		lines       = text.splitlines()
		module_name = os.path.splitext(os.path.basename(path))[0]

		def base_id(x): return getattr(x, 'id', None) or getattr(x, 'attr', None)
		is_op   = lambda c: any(base_id(b) == 'OperatorDefinition' for b in c.bases)
		is_type = lambda c: any(base_id(b) in ('BaseModel', 'Pydantic') for b in c.bases)

		def get_io(node: ast.ClassDef) -> tuple[str, str]:
			inp, out = f'{node.name}_input', f'{node.name}_output'
			for stmt in node.body:
				if isinstance(stmt, ast.Assign):
					for t in stmt.targets:
						if isinstance(t, ast.Name) and isinstance(stmt.value, ast.Constant):
							if t.id == 'input_type':  inp = stmt.value.value
							if t.id == 'output_type': out = stmt.value.value
			return inp, out

		# Load only the required types
		required = {
			typ for node in tree.body if isinstance(node, ast.ClassDef) and is_op(node)
			for typ in get_io(node)
		}

		module = Module.import_module(module_name, path)
		env    = {k: v for k, v in vars(module).items() if isinstance(v, type) and k in required}

		funcs, types = {}, {}

		for node in tree.body:
			if not isinstance(node, ast.ClassDef): continue
			if is_type(node):
				types[node.name] = Code._get_type_definition(node, env)
			elif is_op(node):
				inp, out = get_io(node)
				funcs[node.name] = Code._get_operator_class_definition(node, lines, inp, out)

		# Get entry point and its operator metadata
		entry_name = Code._get_entry_point(module_name, path)

		if entry_name not in funcs:
			raise ValueError(f'Entry point `{entry}` not found among defined operators')

		entry_input_type  = funcs[entry_name]['input_type']
		entry_output_type = funcs[entry_name]['output_type']

		return {
			'functions'         : funcs,
			'types'             : types,
			'entry_name'        : entry_name,
			'entry_input_type'  : entry_input_type,
			'entry_output_type' : entry_output_type
		}
