import traceback
from pathlib           import Path

from fastapi           import HTTPException
from starlette.status  import HTTP_400_BAD_REQUEST


class DapiException(HTTPException):
	HALT   = 'halt'
	BEWARE = 'beware'
	FYI    = 'fyi'

	def __init__(
		self,
		status_code : int         = HTTP_400_BAD_REQUEST,
		detail      : str         = 'An error occurred',
		severity    : str         = None,
		headers     : dict | None = None,
		context     : dict | None = None
	):
		severity = severity if severity in [self.HALT, self.BEWARE, self.FYI] else self.HALT

		data = {
			'detail'   : detail,
			'severity' : severity,
		}
		if context:
			data.update(context)

		super().__init__(
			status_code = status_code,
			headers     = headers,
			detail      = data
		)

	########################################################################

	@staticmethod
	def consume(e: Exception) -> 'DapiException':
		# raise e
		# from dapi.lib.mini_python import MiniPythonRuntimeError
		error = None
		
		'''
		Converts any Exception into a uniform DapiException,
		preserving structure, avoiding nested wrapping.
		'''
		# print('\n====== CONSUMING ERROR ======')
		# print('type:', type(e))
		# print('str :', str(e))
		# print('repr:', repr(e))
		# print('==============================\n')

		if isinstance(e, DapiException):
			error = e
		# elif isinstance(e, MiniPythonRuntimeError):
		# 	print('MPE', str(e))
		# 	error = DapiException(
		# 		status_code = 500,
		# 		severity    = 'halt',
		# 		detail      = e.msg,
		# 		context     = {
		# 			'line'    : e.line,
		# 			'operator': e.operator,
		# 			'trace'   : e.trace
		# 		}
		# 	)
		else:
			error_type = e.__class__.__name__
			# print('ELSE', str(e), error_type)
			message    = str(e).strip()
			tb_lines   = traceback.extract_tb(e.__traceback__)
			# print(tb_lines)
			filename   = tb_lines[-1].filename if tb_lines else '?'
			lineno     = tb_lines[-1].lineno   if tb_lines else '?'
			operator   = getattr(e, 'operator', None)

			if not operator:
				for frame in reversed(tb_lines):
					if 'operators' in frame.filename:
						operator = Path(frame.filename).stem
						break

			# Optional: cut trace
			traceback.print_exception(type(e), e, e.__traceback__, limit=5)

			return DapiException(
				status_code = 500,
				severity    = DapiException.HALT,
				detail      = f'{error_type}: {message}',
				context     = {
					'error_type': error_type,
					'file'      : filename,
					'line'      : lineno,
					'operator'  : operator
				}
			)
			
		return error
