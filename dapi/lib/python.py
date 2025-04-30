import ast, types
from typing import Callable, Any, Optional, Awaitable
from .execution_context import ExecutionContext


class Python:
	BLOCKED_CALLS   = {'eval', 'exec', 'getattr', 'setattr', '__import__'}
	BLOCKED_ATTRS   = {'__dict__', '__class__', '__globals__', '__code__'}
	BLOCKED_GLOBALS = [
		'__import__', 'eval', 'exec', 'open', 'compile', 'globals', 'locals',
		'vars', 'getattr', 'setattr', 'delattr', 'super', 'type', 'object', 'dir'
	]
	ALLOWED_GLOBALS = {
		'int': int, 'float': float, 'str': str, 'bool': bool,
		'dict': dict, 'list': list, 'tuple': tuple, 'len': len,
		'range': range, 'enumerate': enumerate, 'zip': zip,
		'sum': sum, 'min': min, 'max': max, 'print': print
	}

	def __init__(
		self,
		operator_name          : str,
		operator_class_name    : str,
		input_dict             : dict,
		code                   : str,
		execution_context      : Optional[ExecutionContext],
		operator_globals       : dict,
		call_external_operator : Callable[[str, dict, ExecutionContext], Awaitable[Any]],
		get_operator_class     : Callable[[str], type],
		restrict               : bool = True
	):
		self.operator_name          = operator_name
		self.operator_class_name    = operator_class_name
		self.input                  = input_dict
		self.code                   = code
		self.call_external_operator = call_external_operator
		self.get_operator_class     = get_operator_class
		self.execution_context      = execution_context
		self.globals                = { **operator_globals }
		self.i                      = execution_context.i
		self.restrict               = restrict

	############################################################################

	async def _initialize(self):
		self.env_stack = []

		if self.restrict:
			tree     = ast.parse(self.code, filename='<python>')
			self._detect_dangerous_calls(tree)
			compiled = self._rewrite_calls(self.code)
			self._apply_restrictions(self.globals)
		else:
			compiled = compile(self.code, filename='<python>', mode='exec')

		self.globals['_wrap_call_async'] = self._wrap_call_async

		async def call_wrapper(name, *args, **kwargs):
			if len(args) == 1 and isinstance(args[0], dict) and not kwargs:
				kwargs = args[0]
				args   = []

			return await self.call_external_operator(
				name     = name,
				args     = list(args),
				kwargs   = kwargs,
				context  = self.execution_context
			)

		self.globals['call'] = call_wrapper
		exec(compiled, self.globals)

	############################################################################

	def _detect_dangerous_calls(self, tree: ast.AST):
		class DangerousCallDetector(ast.NodeVisitor):
			def visit_Import(self, node):
				raise ValueError('Use of `import` is not allowed')

			def visit_ImportFrom(self, node):
				raise ValueError('Use of `from ... import` is not allowed')

			def visit_Call(self, node):
				if isinstance(node.func, ast.Name) and node.func.id in Python.BLOCKED_CALLS:
					raise ValueError(f'Use of `{node.func.id}` is not allowed')
				self.generic_visit(node)

			def visit_Attribute(self, node):
				if node.attr in Python.BLOCKED_ATTRS:
					raise ValueError(f'Access to `{node.attr}` is not allowed')
				self.generic_visit(node)

		DangerousCallDetector().visit(tree)

	############################################################################

	def _rewrite_calls(self, code_str: str) -> types.CodeType:
		tree = ast.parse(code_str, filename='<python>')

		class CallRewriter(ast.NodeTransformer):
			def visit_Call(self, node: ast.Call) -> ast.AST:
				self.generic_visit(node)
				if isinstance(node.func, ast.Name):
					# Handle special funciton "call"
					if node.func.id == 'call':
						return node

					return ast.copy_location(ast.Call(
						func = ast.Name(id='_wrap_call_async', ctx=ast.Load()),
						args = [
							ast.Constant(node.func.id),
							ast.List(elts=node.args, ctx=ast.Load()),
							ast.Dict(
								keys   = [ast.Constant(kw.arg) for kw in node.keywords if kw.arg],
								values = [kw.value for kw in node.keywords if kw.arg]
							),
							ast.Constant(node.lineno)
						],
						keywords = []
					), node)
				return node

		tree = CallRewriter().visit(tree)
		ast.fix_missing_locations(tree)
		return compile(tree, filename='<python>', mode='exec')

	############################################################################

	def _apply_restrictions(self, globals_dict: dict):
		for name in Python.BLOCKED_GLOBALS:
			globals_dict[name] = None

		globals_dict.update(Python.ALLOWED_GLOBALS)

	############################################################################

	async def _wrap_call_async(self, name: str, args_list: list[Any], kwargs_dict: dict, line: int) -> Any:
		self.execution_context.push(name, line)
		try:
			return await self.call_external_operator(
				name, args_list, kwargs_dict, self.execution_context
			)
		finally:
			self.execution_context.pop()

	############################################################################

	async def invoke(self):
		await self._initialize()
		self.execution_context.push(self.operator_name, 1, 'restricted' if self.restrict else 'unrestricted')
		try:
			operator_class = self.globals.get(self.operator_class_name)
			if not operator_class:
				raise ValueError(f'Class `{self.operator_class_name}` not found')

			instance = operator_class(
				self.call_external_operator,
				self.get_operator_class,
				print
			)
			invoke_method = getattr(instance, 'invoke', None)
			if not invoke_method:
				raise ValueError(f'Method `invoke` not found in `{self.operator_class_name}`')

			return await invoke_method(**self.input)
		finally:
			self.execution_context.pop()

	############################################################################

	def _instance_wrapper(self):
		return type('SelfWrapper', (), {
			'print': print,
			'call' : lambda *a, **kw: self.call_external_operator(*a, **kw)
		})()