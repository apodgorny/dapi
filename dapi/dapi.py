from fastapi                  import FastAPI
from fastapi.middleware.cors  import CORSMiddleware
from dapi.controllers         import controller

dapi = FastAPI()

dapi.add_middleware(
	CORSMiddleware,
	allow_origins=['*'],  # or ['http://127.0.0.1:8000']
	allow_credentials=True,
	allow_methods=['*'],
	allow_headers=['*'],
)

dapi.include_router(controller.router)

@dapi.get('/')
async def root():
	return { 'message': 'It works' }
