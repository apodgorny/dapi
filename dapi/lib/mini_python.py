import ast, os

from typing             import Callable, Optional, Awaitable, Any

from .execution_context import ExecutionContext
from .python            import Python


class MiniPython(Python):

	def _initialize(self):
		self.env_stack = []
		self.root      = None

		# self.builtins = {
		# 	'print'      : print,
		# 	'len'        : len,
		# 	'type'       : type,
		# 	'isinstance' : isinstance
		# }

		self.traceables = (
			ast.Call,
			ast.Assign,
			ast.Return,
			ast.Await,
			ast.BinOp,
			ast.If,
			ast.FunctionDef,
			ast.AsyncFunctionDef
		)

		self.root  = ast.parse(self.code)

	############################################################################

	async def _get_invoke_method(self):
		
		class_node = next(
			(n for n in self.root.body if isinstance(n, ast.ClassDef) and n.name == self.operator_class_name),
			None
		)
		if class_node is None:
			raise RuntimeError(f'[{self.__class__.__name__}] Class `{self.operator_class_name}` not found')

		invoke_method = next(
			(n for n in class_node.body if isinstance(n, (ast.AsyncFunctionDef, ast.FunctionDef)) and n.name == 'invoke'),
			None
		)
		if not invoke_method:
			raise RuntimeError(f'[{self.__class__.__name__}] Method `invoke` not found in `{self.operator_class_name}`')
		return invoke_method

	def _get_source_snippet(self, node):
		'''
			Returns the trimmed source line corresponding to the node, if available.
			Otherwise returns empty string.
		'''
		if hasattr(node, 'lineno'):
			lines  = self.code.splitlines()
			lineno = node.lineno - 1  # lineno is 1-based
			if 0 <= lineno < len(lines):
				return lines[lineno].strip()
		return ''

	############################################################################

	async def invoke(self):
		invoke_method = await self._get_invoke_method()

		# Prepare parameters from input
		parameters = dict(self.input)

		try:
			self.env_stack.append(parameters)
			#----------------------------------
			async_func = await self.eval(invoke_method)
			result     = await async_func(**parameters)
			#----------------------------------
			# print(self.i, f'{self.operator_class_name}.invoke result', result)
			return result
		finally:
			self.env_stack.pop()

	############################################################################

	async def eval(self, node):
		if not node:
			return None

		if type(node) in self.traceables:
			line      = getattr(node, 'lineno', '?')
			node_type = type(node).__name__.lower()

			# ✨ Универсальный push
			self.execution_context.push(
				lineno      = line,
				name        = node_type,
				line        = self._get_source_snippet(node),
				interpreter = 'mini'
			)
		try:
			match node:
				case ast.Await():
					value = await self.eval(node.value)
					if hasattr(value, '__await__'):
						return await value
					return value

				case ast.Return():
					result = await self.eval(node.value)
					return result

				case ast.Attribute():
					value = await self.eval(node.value)
					if hasattr(value, node.attr): return getattr(value, node.attr)
					raise Exception(f'Attribute `{node.attr}` not found on {type(value).__name__}')

				case ast.Subscript():
					container = await self.eval(node.value)
					key       = await self.eval(node.slice)
					return container[key]

				case ast.Call():
					func_node = node.func
					func_name = func_node.id
					args      = [await self.eval(arg) for arg in node.args]
					kwargs    = {kw.arg: await self.eval(kw.value) for kw in node.keywords if kw.arg is not None}

					if isinstance(func_node, ast.Name):
						if func_name in self.globals:
							return self.globals[func_name](*args, **kwargs)

						result = await self.call_external_operator(
							func_name,
							args    = args,
							kwargs  = kwargs,
							context = self.execution_context,
							de      = 'mini'
						)
						return result

					elif isinstance(func_node, ast.Attribute):
						method = await self.eval(func_node)
						if not callable(method):
							raise Exception(f'Attribute call is not callable')

						result = await method(*args, **kwargs)
						return result

					raise Exception('Unsupported call expression')

				case ast.Module():
					for stmt in node.body:
						ret = await self.eval(stmt)
						if isinstance(ret, dict): return ret
					return None

				case ast.FunctionDef():
					def _func(*args, **kwargs):
						local_env = dict(zip([arg.arg for arg in node.args.args], args))
						self.env_stack.append(local_env)
						try:
							for stmt in node.body:
								ret = asyncio.run(self.eval(stmt)) if asyncio.iscoroutinefunction(self.eval) else self.eval(stmt)
								if isinstance(ret, dict): return ret
						finally:
							self.env_stack.pop()
						return None
					return _func

				case ast.AsyncFunctionDef():
					async def _async_func(**kwargs):
						local_env = dict(kwargs)
						self.env_stack.append(local_env)
						try:
							for stmt in node.body:
								ret = await self.eval(stmt)
								if ret is not None:
									return ret
						finally:
							self.env_stack.pop()
						return None
					return _async_func


				case ast.Assign():
					target = node.targets[0]
					if isinstance(target, ast.Name):
						name  = target.id
						value = await self.eval(node.value)
						self.env_stack[-1][name] = value
						return None
					raise Exception('Unsupported assignment target')

				case ast.Dict():
					return {
						await self.eval(k): await self.eval(v)
						for k, v in zip(node.keys, node.values)
					}

				case ast.List():
					return [await self.eval(elt) for elt in node.elts]

				case ast.Tuple():
					return tuple(await self.eval(elt) for elt in node.elts)

				case ast.Set():
					return set(await self.eval(elt) for elt in node.elts)

				case ast.ListComp():
					result = []
					iterable = await self.eval(node.generators[0].iter)
					var = node.generators[0].target.id
					for item in iterable:
						self.env_stack[-1][var] = item
						if all([await self.eval(cond) for cond in node.generators[0].ifs]):
							result.append(await self.eval(node.elt))
					return result

				case ast.SetComp():
					result = set()
					iterable = await self.eval(node.generators[0].iter)
					var = node.generators[0].target.id
					for item in iterable:
						self.env_stack[-1][var] = item
						if all([await self.eval(cond) for cond in node.generators[0].ifs]):
							result.add(await self.eval(node.elt))
					return result

				case ast.DictComp():
					result = {}
					iterable = await self.eval(node.generators[0].iter)
					var = node.generators[0].target.id
					for item in iterable:
						self.env_stack[-1][var] = item
						if all([await self.eval(cond) for cond in node.generators[0].ifs]):
							k = await self.eval(node.key)
							v = await self.eval(node.value)
							result[k] = v
					return result

				case ast.Match():
					subject = await self.eval(node.subject)
					for case_ in node.cases:
						if await self._match_case(subject, case_.pattern):
							for stmt in case_.body:
								ret = await self.eval(stmt)
								if isinstance(ret, dict): return ret
							break
					return None

				case ast.Lambda():
					async def _lambda(*args):
						result = await self.eval(node.body)
						return result
					return _lambda

				case ast.Expr():
					result = await self.eval(node.value)
					return result

				case ast.Constant():
					return node.value

				case ast.Name():
					for scope in reversed(self.env_stack):
						if node.id in scope: return scope[node.id]
					raise Exception(f'Name `{node.id}` is not defined')

				case ast.BinOp():
					left  = await self.eval(node.left)
					right = await self.eval(node.right)
					match node.op:
						case ast.Add()  : return left + right
						case ast.Sub()  : return left - right
						case ast.Mult() : return left * right
						case ast.Div()  : return left / right
						case ast.Mod()  : return left % right
						case _          : raise Exception('Unsupported binary operator')
				
				case ast.JoinedStr():
					# Handle f-strings (JoinedStr nodes)
					result = ''
					for value in node.values:
						if isinstance(value, ast.Constant):
							result += str(value.value)
						elif isinstance(value, ast.FormattedValue):
							formatted_value = await self.eval(value.value)
							result += str(formatted_value)
						else:
							raise Exception(f'Unsupported f-string component: {type(value).__name__}')
					return result
				
				case ast.FormattedValue():
					# This is handled by JoinedStr
					value = await self.eval(node.value)
					return str(value)
				
				case ast.If():
					condition = await self.eval(node.test)
					if condition:
						for stmt in node.body:
							ret = await self.eval(stmt)
							if isinstance(ret, dict): return ret
					else:
						for stmt in node.orelse:
							ret = await self.eval(stmt)
							if isinstance(ret, dict): return ret
					return None
				
				case ast.Compare():
					left = await self.eval(node.left)
					for i, op in enumerate(node.ops):
						right = await self.eval(node.comparators[i])
						match op:
							case ast.Eq()    : result = left == right
							case ast.NotEq() : result = left != right
							case ast.Lt()    : result = left <  right
							case ast.LtE()   : result = left <= right
							case ast.Gt()    : result = left >  right
							case ast.GtE()   : result = left >= right
							case ast.Is()    : result = left is right
							case ast.IsNot() : result = left is not right
							case ast.In()    : result = left in right
							case ast.NotIn() : result = left not in right
							case _           : raise Exception(f'Unsupported comparison operator: {type(op).__name__}')
						if not result:
							return False
						left = right
					return True
				
				case ast.BoolOp():
					match node.op:
						case ast.And():
							for value in node.values:
								result = await self.eval(value)
								if not result: return False
							return True
						case ast.Or():
							for value in node.values:
								result = await self.eval(value)
								if result: return result
							return False
						case _: raise Exception(f'Unsupported boolean operator: {type(node.op).__name__}')
				
				case ast.UnaryOp():
					operand = await self.eval(node.operand)
					match node.op:
						case ast.Not()  : return not operand
						case ast.USub() : return -operand
						case ast.UAdd() : return +operand
						case _          : raise Exception(f'Unsupported unary operator: {type(node.op).__name__}')
				
				case ast.IfExp():
					condition = await self.eval(node.test)
					if condition:
						result = await self.eval(node.body)
					else:
						result = await self.eval(node.orelse)  
					return result
				
				case ast.Pass():
					return None

				case _: raise Exception(f'Unsupported node: {type(node)}')
		finally:
			if type(node) in self.traceables:
				self.execution_context.pop()

	async def _match_case(self, value, pattern):
		match pattern:
			case ast.MatchValue()     : return value == await self.eval(pattern.value)
			case ast.MatchSingleton() : return value is pattern.value
			case ast.MatchAs()        : return True if pattern.name else False
			case _                    : raise Exception(f'Unsupported match pattern: {type(pattern).__name__}')
