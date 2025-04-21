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

		for op in operators:
			name = op['name']
			code = op['code']
			if op.get('interpreter') == 'python' and isinstance(code, str):
				tree = ast.parse(code)
				for node in tree.body:
					if isinstance(node, ast.FunctionDef) and node.name == name:
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
		env = {'input': input_dict, **self.env_types}
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
				case ast.Return():
					return await self.eval(node.value)

				case ast.Attribute():
					value = await self.eval(node.value)
					if isinstance(value, dict): return value.get(node.attr)
					if hasattr(value, node.attr): return getattr(value, node.attr)
					raise Exception(f"Attribute `{node.attr}` not found")

				case ast.Subscript():
					container = await self.eval(node.value)
					key       = await self.eval(node.slice)
					return container[key]

				case ast.Call():
					func_node = node.func
					args      = [await self.eval(arg) for arg in node.args]
					kwargs    = {kw.arg: await self.eval(kw.value) for kw in node.keywords if kw.arg is not None}

					if isinstance(func_node, ast.Name):
						func = None
						for scope in reversed(self.env_stack):
							if func_node.id in scope:
								func = scope[func_node.id]
								break
						if callable(func):
							return await func(*args, **kwargs)
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

				case ast.FunctionDef():
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
				
				case ast.Pass():
					return None

				case _: raise Exception(f'Unsupported node: {type(node).__name__}')
		except MiniPythonRuntimeError:
			raise
		except Exception as e:
			raise MiniPythonRuntimeError(
				str(e),
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