import re
from dapi.lib   import Datum, Interpreter
from dapi.lib.struct import Struct


class PythonInterpreter(Interpreter):
	'''
    Interprets free-form Python with templated I/O.  
    Access input/output as objects with dot notation.
    '''

	async def invoke(
		self,
		operator_name : str,
		code          : str,
		input         : Datum,
		output        : Datum  # empty datum, just the schema
	) -> Datum:

		# Collect paths referenced as {{input.x}} or {{output.y}}
		input_paths  = set(m.group(1) for m in re.finditer(r'\{\{\s*input\.([a-zA-Z0-9_.]+)\s*\}\}',  code))
		output_paths = set(m.group(1) for m in re.finditer(r'\{\{\s*output\.([a-zA-Z0-9_.]+)\s*\}\}', code))

		# Validate all referenced paths exist
		for path in input_paths:
			if path not in input:
				raise ValueError(f'Invalid input path `{path}` in operator `{operator_name}`')
				
		# Remove all {{ ... }} wrappers to expose plain expressions
		code = re.sub(r'\{\{\s*(.*?)\s*\}\}', r'\1', code)

		# Wrap input/output as Structs
		input_struct  = Struct.from_dict(input.to_dict())
		output_struct = Struct.from_dict(output.to_empty_dict())

		print('input', input_struct)
		print('output', output_struct)
		print('code', code)
		print('compile', compile(code, operator_name, 'exec'))

		# Prepare global scope
		safe_globals = {
			'input'  : input_struct,
			'output' : output_struct,
		}

		# Execute and return
		try:
			exec(compile(code, operator_name, 'exec'), safe_globals)
			output.from_dict(output_struct.to_dict())
			return output if not output.is_empty() else input
		except SyntaxError as e:
			raise ValueError(f'Syntax error in `{operator_name}`: {e}')
		except Exception as e:
			raise ValueError(f'Runtime error in `{operator_name}`: {e}')
