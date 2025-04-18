import ast
from typing import Callable, Optional


class ExternalOperatorCall(Exception):
	'''Raised when an undefined operator is encountered during interpretation.'''
	def __init__(self, operator_name: str, input_data: dict):
		self.operator_name = operator_name
		self.input_data    = input_data
		super().__init__(f'External operator call: `{operator_name}`')


class MiniPython(ast.NodeVisitor):
	def __init__(
		self,
		operator_sources       : dict[str, str],
		call_operator_callback : Optional[Callable[[str, dict], dict]] = None
	):
		self.functions              = {}   # name -> FunctionDef
		self.env_stack              = []   # call stack
		self.call_operator_callback = call_operator_callback

		for name, code in operator_sources.items():
			tree = ast.parse(code)
			for node in tree.body:
				if isinstance(node, ast.FunctionDef) and node.name == name:
					self.functions[name] = node

	def call_operator(self, name: str, input_dict: dict) -> dict:
		if name in self.functions:
			self.env_stack.append({'input': input_dict})
			try:
				result = self.visit(self.functions[name])
				if isinstance(result, dict):
					return result
				raise Exception(f'Function `{name}` did not return dict')
			finally:
				self.env_stack.pop()

		if self.call_operator_callback:
			return self.call_operator_callback(name, input_dict)

		raise Exception(f'Function `{name}` not defined')

	def visit_FunctionDef(self, node):
		for stmt in node.body:
			ret = self.visit(stmt)
			if isinstance(ret, dict):
				return ret

	def visit_Return(self, node):
		return self.visit(node.value)

	def visit_Expr(self, node):
		return self.visit(node.value)

	def visit_Call(self, node):
		func_name = node.func.id
		arg       = self.visit(node.args[0])
		if not isinstance(arg, dict):
			raise Exception(f'Argument to `{func_name}` must be dict')
		return self.call_operator(func_name, arg)

	def visit_Assign(self, node):
		name                   = node.targets[0].id
		value                  = self.visit(node.value)
		self.env_stack[-1][name] = value

	def visit_Name(self, node):
		for scope in reversed(self.env_stack):
			if node.id in scope:
				return scope[node.id]
		raise Exception(f'Variable `{node.id}` not found')

	def visit_Constant(self, node):
		return node.value

	def visit_Subscript(self, node):
		value = self.visit(node.value)
		key   = self.visit(node.slice)
		return value[key]

	def visit_Dict(self, node):
		return {
			self.visit(k): self.visit(v)
			for k, v in zip(node.keys, node.values)
		}

	def visit_BinOp(self, node):
		left  = self.visit(node.left)
		right = self.visit(node.right)
		match node.op:
			case ast.Add():  return left + right
			case ast.Sub():  return left - right
			case ast.Mult(): return left * right
			case ast.Div():  return left / right
			case ast.Mod():  return left % right
			case _: raise Exception('Unsupported binary operation')

	def visit_Compare(self, node):
		left  = self.visit(node.left)
		right = self.visit(node.comparators[0])
		match node.ops[0]:
			case ast.Lt():     return left < right
			case ast.LtE():    return left <= right
			case ast.Gt():     return left > right
			case ast.GtE():    return left >= right
			case ast.Eq():     return left == right
			case ast.NotEq():  return left != right
			case _: raise Exception('Unsupported comparison')

	def visit_If(self, node):
		if self.visit(node.test):
			for stmt in node.body:
				ret = self.visit(stmt)
				if isinstance(ret, dict):
					return ret
		else:
			for stmt in node.orelse:
				ret = self.visit(stmt)
				if isinstance(ret, dict):
					return ret

	def visit_For(self, node):
		iterable = self.visit(node.iter)
		var_name = node.target.id
		for item in iterable:
			self.env_stack[-1][var_name] = item
			for stmt in node.body:
				ret = self.visit(stmt)
				if isinstance(ret, dict):
					return ret

	def generic_visit(self, node):
		raise Exception(f'Unsupported AST node: {type(node).__name__}')
