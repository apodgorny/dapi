import ast
from typing import Callable, Optional, Awaitable, Any
from .execution_context import ExecutionContext


class BreakSignal(Exception): pass
class ContinueSignal(Exception): pass


class MiniPython:
	def __init__(
		self,
		code                   : str,
		call_external_operator : Callable[[str, dict, ExecutionContext], Awaitable[dict]],
		context                : Optional[ExecutionContext] = None,
		globals_dict           : Optional[dict[str, Any]]   = None
	):
		self.functions              = {}
		self.env_stack              = []
		self.call_external_operator = call_external_operator
		self._root_operator_name    = None
		self._was_called            = False
		self.context                = context
		self.globals                = globals_dict or {}

		self.allowed_builtins = {'print', 'len', 'type', 'isinstance'}
		self.env_types        = {
			'list' : list, 'dict'  : dict,  'str'  : str,
			'int'  : int,  'float' : float, 'bool' : bool,
			'set'  : set,  'tuple' : tuple
		}
		self.builtins = {
			'print'      : print,
			'len'        : len,
			'type'       : type,
			'isinstance' : isinstance
		}

		tree = ast.parse(code)
		for node in tree.body:
			if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
				self.functions[node.name] = node

	############################################################################

	async def invoke_class(self, operator_name: str, class_name: str, input_dict: dict) -> dict:
		'''Finds the class by name, instantiates it, and invokes its `invoke()` method with input_dict.'''

		self.context.push(operator_name, 1, 'mini')  # Push context for the operator class
		self._operator_name = operator_name          # Save the operator name for context
		try:
			# Check if class exists in globals
			operator_class = self.globals.get(class_name)
			if not operator_class:
				raise Exception(f'Operator class `{class_name}` not found')

			# Instantiate the operator class
			operator_instance = operator_class()

			# Call its `invoke()` method and return the result
			return await operator_instance.invoke(input_dict)

		finally:
			self.context.pop()  # Pop context after invocation

	############################################################################

	async def call_operator(self, name: str, input_dict: dict) -> dict:
		'''Calls the external operator callback.'''
		if name not in self.functions:
			raise Exception(f'Unknown function call `{name}`')
		return await self.call_external_operator(name, input_dict, self.context)

	############################################################################

	async def eval(self, node):
		operator = self._root_operator_name or '<unknown>'
		line     = getattr(node, 'lineno', '?')
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
						result = await func(*args, **kwargs)
						return result
						
					result = await self.invoke_class(
						func_node.id,
						String.snake_to_camel(func_node.id),
						{
							'args'   : args,
							'kwargs' : kwargs
						}
					)

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
					result = await self.eval(node.body)
				else:
					result = await self.eval(node.orelse)
				return result
			
			case ast.Pass():
				return None

			case _: raise Exception(f'Unsupported node: {type(node).__name__}')

	async def _match_case(self, value, pattern):
		match pattern:
			case ast.MatchValue():     return value == await self.eval(pattern.value)
			case ast.MatchSingleton(): return value is pattern.value
			case ast.MatchAs():        return True if pattern.name else False
			case _: raise Exception(f'Unsupported match pattern: {type(pattern).__name__}')
