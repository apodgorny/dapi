import os
import ast
import sys
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
			'__fullpython_call_with_trace__' : self._wrap_call_async
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
					func_name = ast.copy_location(
						ast.Name(id='__fullpython_call_with_trace__', ctx=ast.Load()),
						node.func
					)

					arg_func_id = ast.copy_location(
						ast.Constant(node.func.id),
						node.func
					)

					arg_args_list = ast.copy_location(
						ast.List(elts=node.args, ctx=ast.Load()),
						node.args[0] if node.args else node
					)

					kw_keys = [ast.copy_location(ast.Constant(kw.arg), kw.value) for kw in node.keywords if kw.arg]
					kw_values = [kw.value for kw in node.keywords if kw.arg]
					kw_dict = ast.copy_location(
						ast.Dict(keys=kw_keys, values=kw_values),
						node.keywords[0].value if node.keywords else node
					)

					arg_lineno = ast.copy_location(
						ast.Constant(node.lineno),
						node
					)

					new_node = ast.Call(
						func=func_name,
						args=[arg_func_id, arg_args_list, kw_dict, arg_lineno],
						keywords=[]
					)

					return ast.copy_location(new_node, node)
				return self.generic_visit(node)

		return compile(CallRewriter().visit(tree), filename='<fullpython>', mode='exec')

	############################################################################

	async def _wrap_call_async(self, name: str, args_list: list[Any], kwargs_dict: dict, line: int) -> Any:
		self.execution_context.push(name, line)
		try:
			return await self.call_external_operator(
				name,
				args_list,
				kwargs_dict,
				self.execution_context,
				de='full'
			)
		finally:
			self.execution_context.pop()

	############################################################################

	async def _get_invoke_method(self):
		operator_class = self.ctx.get(self.operator_class_name)
		if not operator_class:
			raise ValueError(f'[{self.__class__.__name__}] Class `{self.operator_class_name}` not found in code')

		async def call_external_operator(name, kwargs):
			return await self.call_external_operator(name, [], kwargs, self.execution_context, de='full')

		instance = operator_class(call_external_operator, print)
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
			print(self.operator_name, parameters)
			#----------------------------------
			result = await invoke_method(**parameters)
			#----------------------------------
			# print(self.i, f'{self.operator_class_name}.invoke result', result)
			return result
		finally:
			self.execution_context.pop()