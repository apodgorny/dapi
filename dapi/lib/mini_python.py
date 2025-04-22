import ast
from typing import Callable, Optional, Awaitable


class ExternalOperatorCall(Exception):
	def __init__(self, operator_name: str, input_data: dict):
		self.operator_name = operator_name
		self.input_data    = input_data
		super().__init__(f'External operator call: `{operator_name}`')


class BreakSignal(Exception): pass
class ContinueSignal(Exception): pass


class MiniPythonRuntimeError(Exception):
	def __init__(self, msg: str, *, line: int = None, func: str = None, stack: list[tuple[str, int]] = None):
		self.line  = line
		self.func  = func
		self.stack = stack or []
		trace      = '\n'.join(f'  in {f} @ line {l}' for f, l in self.stack)
		prefix     = f'[{func or "<anonymous>"} @ line {line}]'
		self.trace = trace
		self.msg   = msg
		self.data  = {
			'message': msg,
			'line'   : line,
			'func'   : func,
			'trace'  : self.stack
		}
		super().__init__(f'{prefix} {msg}')


class MiniPython:
	def __init__(
			self,
			operators              : dict[str, str],
			call_operator_callback : Optional[Callable[[str, dict], Awaitable[dict]]] = None
	):
		self.functions              = {}
		self.env_stack              = []
		self.call_operator_callback = call_operator_callback
		self._root_operator_name    = None
		self._was_called            = False
		self.call_stack             = []
		self.allowed_builtins       = {'print', 'len', 'type', 'isinstance'}
		self.env_types = {
			'list': list, 'dict': dict, 'str': str,
			'int' : int,  'float': float, 'bool': bool,
			'set' : set,  'tuple': tuple
		}
		
		# Add built-in functions to the environment
		self.builtins = {
			'print': print,
			'len': len,
			'type': type,
			'isinstance': isinstance
		}

		for op in operators:
			name = op['name']
			code = op['code']
			if op.get('interpreter') == 'python' and isinstance(code, str):
				tree = ast.parse(code)
				for node in tree.body:
					if (isinstance(node, ast.FunctionDef) or isinstance(node, ast.AsyncFunctionDef)) and node.name == name:
						self.functions[name] = node
			else:
				self.functions[name] = None

	async def call_operator(self, name: str, input_dict: dict) -> dict:
		if not self.call_operator_callback:
			raise Exception('Callback for external operators was not provided')
		if name not in self.functions:
			raise Exception(f'Unknown function call `{name}` in operator `{self._root_operator_name}`')
		if 'args' in input_dict and len(input_dict['args']) == 1 and not input_dict.get('kwargs'):
			arg = input_dict['args'][0]
			if isinstance(arg, dict):
				input_dict = arg
		return await self.call_operator_callback(name, input_dict)

	async def call_main(self, name: str, input_dict: dict) -> dict:
		if self._was_called:
			return await self.call_operator(name, input_dict)
		if name not in self.functions:
			raise Exception(f'Root function `{name}` not defined')
		self._was_called         = True
		self._root_operator_name = name
		env = {'input': input_dict, **self.env_types, **self.builtins}
		self.env_stack.append(env)
		try:
			return await self.eval(self.functions[name])
		finally:
			self.env_stack.pop()

	async def eval(self, node):
		func = self._root_operator_name or '<anonymous>'
		line = getattr(node, 'lineno', '?')
		self.call_stack.append((func, line))
		try:
			match node:
				case ast.Await():
					value = await self.eval(node.value)
					if hasattr(value, '__await__'):
						return await value
					return value

				case ast.Return():
					return await self.eval(node.value)

				case ast.Attribute():
					value = await self.eval(node.value)
					# Standard Python behavior: no special handling for dictionaries
					if hasattr(value, node.attr): return getattr(value, node.attr)
					raise Exception(f"Attribute `{node.attr}` not found on {type(value).__name__}")

				case ast.Subscript():
					container = await self.eval(node.value)
					key       = await self.eval(node.slice)
					return container[key]

				case ast.Call():
					func_node = node.func
					args      = [await self.eval(arg) for arg in node.args]
					kwargs    = {kw.arg: await self.eval(kw.value) for kw in node.keywords if kw.arg is not None}

					if isinstance(func_node, ast.Name):
						# Check if it's a built-in function first
						if func_node.id in self.builtins:
							return self.builtins[func_node.id](*args, **kwargs)
							
						# Otherwise look in the environment
						func = None
						for scope in reversed(self.env_stack):
							if func_node.id in scope:
								func = scope[func_node.id]
								break
						
						if callable(func):
							return await func(*args, **kwargs)
							
						# If not in builtins or environment, try as operator
						return await self.call_operator(func_node.id, {
							'args'   : args,
							'kwargs' : kwargs
						})

					elif isinstance(func_node, ast.Attribute):
						method = await self.eval(func_node)
						if not callable(method):
							raise Exception(f'Attribute call is not callable')
						return await method(*args, **kwargs)

					raise Exception('Unsupported call expression')

				case ast.Module():
					for stmt in node.body:
						ret = await self.eval(stmt)
						if isinstance(ret, dict): return ret
					return None

				case ast.FunctionDef() | ast.AsyncFunctionDef():
					for stmt in node.body:
						ret = await self.eval(stmt)
						if isinstance(ret, dict): return ret
					return None

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
						return await self.eval(node.body)
					return _lambda

				case ast.Expr():
					return await self.eval(node.value)

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
						case ast.Add():  return left + right
						case ast.Sub():  return left - right
						case ast.Mult(): return left * right
						case ast.Div():  return left / right
						case ast.Mod():  return left % right
						case _: raise Exception('Unsupported binary operator')
				
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
							case ast.Eq(): result = left == right
							case ast.NotEq(): result = left != right
							case ast.Lt(): result = left < right
							case ast.LtE(): result = left <= right
							case ast.Gt(): result = left > right
							case ast.GtE(): result = left >= right
							case ast.Is(): result = left is right
							case ast.IsNot(): result = left is not right
							case ast.In(): result = left in right
							case ast.NotIn(): result = left not in right
							case _: raise Exception(f'Unsupported comparison operator: {type(op).__name__}')
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
						case ast.Not(): return not operand
						case ast.USub(): return -operand
						case ast.UAdd(): return +operand
						case _: raise Exception(f'Unsupported unary operator: {type(node.op).__name__}')
				
				case ast.IfExp():
					condition = await self.eval(node.test)
					if condition:
						return await self.eval(node.body)
					else:
						return await self.eval(node.orelse)
				
				case ast.Pass():
					return None

				case _: raise Exception(f'Unsupported node: {type(node).__name__}')
		except MiniPythonRuntimeError:
			raise
		except Exception as e:
			# Create a more concise error message
			error_msg = f"{type(e).__name__}: {str(e)}"
			raise MiniPythonRuntimeError(
				error_msg,
				line  = line,
				func  = func,
				stack = list(self.call_stack)
			)
		finally:
			self.call_stack.pop()

	async def _match_case(self, value, pattern):
		match pattern:
			case ast.MatchValue():     return value == await self.eval(pattern.value)
			case ast.MatchSingleton(): return value is pattern.value
			case ast.MatchAs():        return True if pattern.name else False
			case _: raise Exception(f'Unsupported match pattern: {type(pattern).__name__}')
