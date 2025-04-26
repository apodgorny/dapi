import os
import ast
import types
import inspect
import asyncio
import traceback

from typing import Callable, Any, Optional

from .python import Python

# OperatorService.invoke()
#   ↳ FullPython.__init__()  ──> вызывает Python.__init__() ──> FullPython._initialize()
#       ↳ _initialize()  ──> _instrument_ast()  (запускает CallRewriter)
#                       ──> exec(compiled, {'__fullpython_call_with_trace__':self._wrap_call})
#   ↳ FullPython.invoke()   ──> уже запущенный код «в памяти»  


class FullPython(Python):
	'''Executes arbitrary Python code with hooks for unknown calls and external stack tracing.'''

	def _initialize(self):
		compiled = self._instrument_ast(self.code)

		ctx = {
			'__fullpython_call_with_trace__': self._wrap_call
		}

		exec(compiled, ctx)
		self.ctx = ctx  # сохраняем для вызова operator_class

	############################################################################

	def _instrument_ast(self, code_str: str) -> types.CodeType:
		'''Transform code to inject context.push/pop around external operator calls.'''
		tree = ast.parse(code_str, filename='<fullpython>')

		class CallRewriter(ast.NodeTransformer):
			def visit_Call(self, node: ast.Call) -> ast.AST:
				if isinstance(node.func, ast.Name):
					kw_dict = ast.Dict(
						keys   = [ast.Constant(kw.arg) for kw in node.keywords if kw.arg],
						values = [kw.value for kw in node.keywords if kw.arg]
					)
					new_node = ast.Call(
						func     = ast.Name(id='__fullpython_call_with_trace__', ctx=ast.Load()),
						args     = [
							ast.Constant(node.func.id),
							ast.List(elts=node.args, ctx=ast.Load()),
							kw_dict,
							ast.Constant(node.lineno)
						],
						keywords = []
					)
					return ast.copy_location(new_node, node)
				return self.generic_visit(node)

		return compile(CallRewriter().visit(tree), filename='<fullpython>', mode='exec')


	############################################################################

	def _wrap_call(self, name: str, args_list: list[Any], kwargs_dict: dict, line: int) -> Any:
	# def _wrap_call(self, name: str, args: list[Any], line: int) -> Any:
		'''Wrap call with context push/pop and error transformation.'''
		return asyncio.get_event_loop().run_until_complete(
			self._wrap_call_async(name, args_list, kwargs_dict, line)
		)

	async def _wrap_call_async(self, name: str, args_list: list[Any], kwargs_dict: dict, line: int) -> Any:
		self.execution_context.push(name, line, 'full')
		try:
			return self.call_external_operator(name, kwargs_dict, self.execution_context, de='full')
		finally:
			self.execution_context.pop()

	############################################################################

	async def _get_invoke_method(self):
		operator_class = self.ctx.get(self.operator_class_name)
		if not operator_class:
			raise ValueError(f'[{self.__class__.__name__}] Class `{self.operator_class_name}` not found in code')

		instance = operator_class()
		invoke_method = getattr(instance, 'invoke', None)

		if not invoke_method:
			raise RuntimeError(f'[{self.__class__.__name__}] Method `invoke` not found in `{self.operator_class_name}`')

		return invoke_method

	############################################################################

	async def invoke(self):
		try:
			self.execution_context.push(self.operator_name, 1, 'full')
			invoke_method = await self._get_invoke_method()

			# parameters are ready
			parameters = dict(self.input)

			#----------------------------------
			result = await invoke_method(**parameters)
			#----------------------------------
			# print(self.i, f'{self.operator_class_name}.invoke result', result)
			return result

		finally:
			self.execution_context.pop()