import asyncio, traceback
from typing  import Any, Callable, Type, List, Dict
from fastapi import APIRouter
from fastapi.responses import JSONResponse

from dapi.db         import Base, engine, SessionLocal
from dapi.lib.string import String

from fastapi          import HTTPException
from starlette.status import HTTP_400_BAD_REQUEST
from enum             import Enum


########################################################################

class DapiException(HTTPException):
	HALT   = 'halt'    # Client must stop processing
	BEWARE = 'beware'  # Client may continue
	FYI    = 'fyi'     # Purely informational

	def __init__(
		self,
		status_code : int         = HTTP_400_BAD_REQUEST,
		detail      : str         = 'An error occurred',
		severity    : str         = None,
		headers     : dict | None = None
	):
		severity = 'halt' if severity not in ['halt','beware','fyi'] else severity
		super().__init__(status_code=status_code, detail={
			'message'  : detail,
			'severity' : severity,
		}, headers=headers)

########################################################################

class Dapi:
	def __init__(self, *services):
		self.router = APIRouter(prefix='/dapi')
		self.db     = SessionLocal()
		self.app    = None

		for cls in services:
			setattr(self, String.camel_to_snake(cls.__name__), cls(self))

		Base.metadata.create_all(bind=engine)

		print('DAPI Controller is initiated')

	def start(self, app):
		self.app = app
		self.app.include_router(self.router)
		
	async def initialize_services(self):
		"""Initialize all services asynchronously."""
		for service_name in dir(self):
			service = getattr(self, service_name)
			if isinstance(service, DapiService) and hasattr(service, 'initialize'):
				await service.initialize()

########################################################################		

class DapiService:
	'''Base service with exception-wrapping decorator.'''

	def __init__(self, dapi):
		self.dapi = dapi

	async def initialize(self):
		print('Initializing service', self.__class__.__name__)

	@classmethod
	def wrap_exceptions(cls, handler_map=None):
		'''Class decorator that wraps all public methods with exception handling.'''
		handler_map = handler_map or {}
		
		def handle_exception(e):
			if isinstance(e, tuple(handler_map.keys())):
				status, severity = handler_map[type(e)]
				raise DapiException(status_code=status, detail=str(e), severity=severity)
			elif isinstance(e, DapiException):
				raise e
			else:
				raise DapiException(status_code=500, detail=f'Unhandled error: {traceback.format_exc()}', severity='halt')
		
		def create_wrapper(method):
			if asyncio.iscoroutinefunction(method):
				async def wrapper(*args, **kwargs):
					try:
						return await method(*args, **kwargs)
					except Exception as e:
						return handle_exception(e)
			else:
				def wrapper(*args, **kwargs):
					try:
						return method(*args, **kwargs)
					except Exception as e:
						return handle_exception(e)
			
			return wrapper

		def decorate(target_cls):
			for attr_name in dir(target_cls):
				if attr_name.startswith('_'):
					continue
				method = getattr(target_cls, attr_name)
				if callable(method):
					setattr(target_cls, attr_name, create_wrapper(method))
			return target_cls

		return decorate

########################################################################
