import ast


class MiniPython(ast.NodeVisitor):
	def __init__(self, operator_sources: dict[str, str]):
		self.functions  = {}  # name -> FunctionDef
		self.env_stack = []  # stack of dicts, one per function call

		for name, code in operator_sources.items():
			tree = ast.parse(code)
			for node in tree.body:
				if isinstance(node, ast.FunctionDef) and node.name == name:
					self.functions[name] = node

	def call_operator(self, name: str, input_dict: dict) -> dict:
		if name not in self.functions:
			raise Exception(f'Function `{name}` not defined')

		self.env_stack.append({'input': input_dict})
		try:
			result = self.visit(self.functions[name])
			if isinstance(result, dict):
				return result
			else:
				raise Exception(f'Function `{name}` did not return dict')
		finally:
			self.env_stack.pop()

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
		arg = self.visit(node.args[0])
		if not isinstance(arg, dict):
			raise Exception(f'Arguments to `{func_name}` must be dict')
		return self.call_operator(func_name, arg)

	def visit_Assign(self, node):
		name = node.targets[0].id
		value = self.visit(node.value)
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
		key = self.visit(node.slice)
		return value[key]

	def visit_Index(self, node):
		return self.visit(node.value)

	def visit_BinOp(self, node):
		left = self.visit(node.left)
		right = self.visit(node.right)
		op = node.op
		if isinstance(op, ast.Add): return left + right
		if isinstance(op, ast.Sub): return left - right
		if isinstance(op, ast.Mult): return left * right
		if isinstance(op, ast.Div): return left / right
		if isinstance(op, ast.Mod): return left % right
		raise Exception('Unsupported binary operation')

	def visit_Compare(self, node):
		left = self.visit(node.left)
		right = self.visit(node.comparators[0])
		op = node.ops[0]
		if isinstance(op, ast.Lt): return left < right
		if isinstance(op, ast.LtE): return left <= right
		if isinstance(op, ast.Gt): return left > right
		if isinstance(op, ast.GtE): return left >= right
		if isinstance(op, ast.Eq): return left == right
		if isinstance(op, ast.NotEq): return left != right
		raise Exception('Unsupported comparison')

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
		raise Exception(f'Unsupported node: {type(node).__name__}')
