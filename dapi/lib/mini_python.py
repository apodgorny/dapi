import ast
from typing import Callable, Optional, Awaitable


class ExternalOperatorCall(Exception):
	'''Raised when an undefined operator is encountered during interpretation.'''
	def __init__(self, operator_name: str, input_data: dict):
		self.operator_name = operator_name
		self.input_data    = input_data
		super().__init__(f'External operator call: `{operator_name}`')


class MiniPython:
	def __init__(
		self,
		operators              : dict[str, str],
		call_operator_callback : Optional[Callable[[str, dict], Awaitable[dict]]] = None
	):
		self.functions              = {}   # name -> FunctionDef
		self.env_stack              = []   # call stack
		self.call_operator_callback = call_operator_callback
		self._root_operator_name    = None
		self._was_called            = False  # Changed: flag to detect if top-level function was already executed

		for op in operators:
			name = op['name']
			code = op['code']
			if op.get('interpreter') == 'python' and isinstance(code, str):
				tree = ast.parse(code)
				for node in tree.body:
					if isinstance(node, ast.FunctionDef) and node.name == name:
						self.functions[name] = node
			else:
				self.functions[name] = None  # Register non-Python operators

	async def call_operator(self, name: str, input_dict: dict) -> dict:
		if not self.call_operator_callback:
			raise Exception(f'Callback for external operators was not provided')

		# Check if this is a registered operator (Python or external)
		if name not in self.functions:
			raise Exception(f'Unknown function call `{name}` in operator `{self._root_operator_name}`')
		
		return await self.call_operator_callback(name, input_dict)

	async def call_main(self, name: str, input_dict: dict) -> dict:
		if self._was_called:
			return await self.call_operator(name, input_dict)

		if name not in self.functions:
			raise Exception(f'Root function `{name}` not defined')

		self._was_called         = True
		self._root_operator_name = name

		self.env_stack.append({'input': input_dict})
		try:
			return await self.eval(self.functions[name])
		finally:
			self.env_stack.pop()

	async def eval(self, node):
		if isinstance(node, ast.FunctionDef):
			for stmt in node.body:
				ret = await self.eval(stmt)
				if isinstance(ret, dict):
					return ret

		elif isinstance(node, ast.Return):
			return await self.eval(node.value)

		elif isinstance(node, ast.Expr):
			return await self.eval(node.value)

		elif isinstance(node, ast.Call):
			func_name = node.func.id
			arg       = await self.eval(node.args[0])
			if not isinstance(arg, dict):
				raise Exception(f'Argument to `{func_name}` must be dict')
			return await self.call_operator(func_name, arg)

		elif isinstance(node, ast.Assign):
			name  = node.targets[0].id
			value = await self.eval(node.value)
			self.env_stack[-1][name] = value

		elif isinstance(node, ast.Name):
			for scope in reversed(self.env_stack):
				if node.id in scope:
					return scope[node.id]
			raise Exception(f'Variable `{node.id}` not found')

		elif isinstance(node, ast.Constant):
			return node.value

		elif isinstance(node, ast.Subscript):
			value = await self.eval(node.value)
			key   = await self.eval(node.slice)
			return value[key]

		elif isinstance(node, ast.Dict):
			return {
				await self.eval(k): await self.eval(v)
				for k, v in zip(node.keys, node.values)
			}

		elif isinstance(node, ast.BinOp):
			left  = await self.eval(node.left)
			right = await self.eval(node.right)
			match node.op:
				case ast.Add():  return left + right
				case ast.Sub():  return left - right
				case ast.Mult(): return left * right
				case ast.Div():  return left / right
				case ast.Mod():  return left % right
				case _: raise Exception('Unsupported binary operation')

		elif isinstance(node, ast.Compare):
			left  = await self.eval(node.left)
			right = await self.eval(node.comparators[0])
			match node.ops[0]:
				case ast.Lt():     return left < right
				case ast.LtE():    return left <= right
				case ast.Gt():     return left > right
				case ast.GtE():    return left >= right
				case ast.Eq():     return left == right
				case ast.NotEq():  return left != right
				case _: raise Exception('Unsupported comparison')

		elif isinstance(node, ast.If):
			if await self.eval(node.test):
				for stmt in node.body:
					ret = await self.eval(stmt)
					if isinstance(ret, dict):
						return ret
			else:
				for stmt in node.orelse:
					ret = await self.eval(stmt)
					if isinstance(ret, dict):
						return ret

		elif isinstance(node, ast.For):
			iterable = await self.eval(node.iter)
			var_name = node.target.id
			for item in iterable:
				self.env_stack[-1][var_name] = item
				for stmt in node.body:
					ret = await self.eval(stmt)
					if isinstance(ret, dict):
						return ret

		elif isinstance(node, ast.UnaryOp):
			operand = await self.eval(node.operand)
			match node.op:
				case ast.USub(): return -operand
				case ast.UAdd(): return +operand
				case ast.Not():  return not operand
				case _: raise Exception('Unsupported unary operation')

		elif isinstance(node, ast.BoolOp):
			values = [await self.eval(v) for v in node.values]
			if isinstance(node.op, ast.And): return all(values)
			if isinstance(node.op, ast.Or):  return any(values)
			raise Exception('Unsupported boolean operation')

		elif isinstance(node, ast.List):
			return [await self.eval(elt) for elt in node.elts]

		elif isinstance(node, ast.Tuple):
			return tuple(await self.eval(elt) for elt in node.elts)

		else:
			raise Exception(f'Unsupported AST node: {type(node).__name__}')
