import ast
import types
import traceback
from typing import Callable, Any, Optional


class FullPython:
    '''Executes arbitrary Python code with hooks for unknown calls and external stack tracing.'''

    def __init__(
        self,
        code                   : str,
        execution_context      : Any,
        call_external_operator : Callable[[str, list[Any]], Any],
        globals_dict           : Optional[dict[str, Any]] = None
    ):
        self.code                   = code
        self.context                = execution_context
        self.call_external_operator = call_external_operator

        compiled = self._instrument_ast(self.code)
        ctx      = {
            '__fullpython_call_with_trace__' : self._wrap_call
        }
        if globals_dict:
            ctx.update(globals_dict)
        exec(compiled, ctx)
        self.globals = ctx

    ############################################################################

    def _instrument_ast(self, code_str: str) -> types.CodeType:
        '''Transform code to inject context.push/pop around external operator calls.'''
        tree = ast.parse(code_str, filename='<fullpython>')

        class CallRewriter(ast.NodeTransformer):
            def visit_Call(self, node: ast.Call) -> ast.AST:
                # Check for unknown name, assume it's external
                if isinstance(node.func, ast.Name):
                    name = node.func.id
                    line = node.lineno
                    new_node = ast.Call(
                        func = ast.Name(id='__fullpython_call_with_trace__', ctx=ast.Load()),
                        args = [
                            ast.Constant(name),
                            ast.List(elts=node.args, ctx=ast.Load()),
                            ast.Constant(line)
                        ],
                        keywords = []
                    )
                    return ast.copy_location(new_node, node)
                return self.generic_visit(node)

        return compile(CallRewriter().visit(tree), filename='<fullpython>', mode='exec')

    ############################################################################

    def _wrap_call(self, name: str, args: list[Any], line: int) -> Any:
        '''Wrap call with context push/pop and error transformation.'''
        self.context.push(name, line)
        try:
            return self.call_external_operator(name, args)
        finally:
            self.context.pop()

    ############################################################################

    async def invoke_class(self, operator_name: str, class_name: str, input_data: dict) -> Any:
        '''Instantiate the class by class_name and invoke its 'invoke' method with input_data.'''
        self.context.push(operator_name, 1, 'full')  # Push context for the operator class
        try:
            # Find the class in the globals dictionary populated by exec
            operator_class = self.globals.get(class_name)
            if not operator_class:
                raise ValueError(f'Operator class "{class_name}" not found in provided code.')

            # Instantiate the class
            operator_instance = operator_class()

            # Call the invoke() method on the instance and return the result
            result = await operator_instance.invoke(input_data)

            return result

        finally:
            self.context.pop()  # Pop context after invocation
