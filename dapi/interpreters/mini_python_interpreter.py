from dapi.lib import MiniPython, DapiException, Interpreter
from dapi.lib import String


class MiniPythonInterpreter(Interpreter):
	'''
	Executes MiniPython code passed as a string. Assumes code is valid and defines a root function.
	All operator calls are routed through the external callback.
	'''

	type = 'mini'

	async def invoke(self) -> dict:
		try:
			# Initialize the MiniPython interpreter with the provided code, context, and callback
			mini_python = MiniPython(
				code                   = self.code,
				call_external_operator = self.call,
				context                = self.context,
				globals_dict           = {.......}
			)

			result = await mini_python.invoke_class(self.name, self.class_name, self.input)

			return result

		except Exception as e:
			raise DapiException.consume(e)




# import traceback

# from dapi.lib import (
# 	Datum,
# 	Interpreter,
# 	DapiException,
# 	Struct,
# 	MiniPython,
# 	ExecutionContext
# )


# class MiniPythonRuntimeError(Exception):
# 	def __init__(
# 		self,
# 		msg      : str,
# 		*,
# 		line     : int = None,
# 		operator : str = None,
# 		stack    : list[tuple[str, int, str]] = None
# 	):
# 		self.line     = line
# 		self.operator = operator
# 		self.stack    = stack or []
# 		self.trace    = self._format_trace(self.stack)
# 		self.msg      = msg
# 		super().__init__(msg)

# 	@staticmethod
# 	def _format_trace(stack):
# 		lines = []
# 		for entry in stack:
# 			if len(entry) == 3:
# 				op, ln, interp = entry
# 				lines.append(f'  in {op} @ line {ln} [{interp}]')
# 			elif len(entry) == 2:
# 				op, ln = entry
# 				lines.append(f'  in {op} @ line {ln}')
# 		return '\n'.join(lines)


# class PythonInterpreter(Interpreter):
# 	'''
# 	Executes MiniPython operator code, supporting async external operator calls.
# 	'''

# 	def __init__(self, dapi=None):
# 		self.dapi = dapi

# 	async def invoke_external_operator(
# 		self,
# 		name       : str,
# 		input_dict : dict,
# 		context    : ExecutionContext = None
# 	) -> dict:
# 		result = await self.dapi.operator_service.invoke(
# 			name    = name,
# 			input   = input_dict,
# 			context = context
# 		)
# 		return result['output'] if 'output' in result else result


# 	async def invoke(
# 		self,
# 		operator_name : str,
# 		code          : str,
# 		input         : Datum,
# 		output        : Datum,
# 		config        : dict,
# 		context       : ExecutionContext
# 	) -> Datum:

# 		if context is None: raise ValueError('ExecutionContext must be explicitly provided')
# 		config     = config or {}
# 		operators  = await self.dapi.operator_service.get_all()
# 		input_dict = input.to_dict()
# 		# print([o['name'] for o in operators])

# 		try:
# 			output_dict = await MiniPython(
# 				operators         = operators,
# 				operator_callback = self.invoke_external_operator,
# 				context           = context
# 			).call_main(
# 				name              = operator_name,
# 				input_dict        = input_dict
# 			)
# 		except MiniPythonRuntimeError:
# 			raise
# 		except Exception as e:
# 			from dapi.lib.dapi_exception import DapiException

# 			# Получаем строку, номер и стек вызовов
# 			current_line     = getattr(node, 'lineno', '?')
# 			current_operator = self._root_operator_name

# 			if isinstance(e, DapiException):
# 				detail     = e.detail if isinstance(e.detail, dict) else {}
# 				error_msg  = detail.get('detail', str(e))
# 				line       = detail.get('line', current_line)
# 				operator   = detail.get('operator', current_operator)
# 			else:
# 				error_msg  = str(e)
# 				line       = current_line
# 				operator   = current_operator

# 			raise MiniPythonRuntimeError(
# 				msg      = error_msg,
# 				line     = line,
# 				operator = operator,
# 				stack    = self.context.stack
# 			)
# 		# finally:
# 		# 	self.context.pop()
# 		# except Exception as e:
# 		# 	raise DapiException.consume(e)

# 		output.from_dict(output_dict)
# 		return output
