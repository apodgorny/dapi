from fastapi                          import FastAPI
from fastapi.middleware.cors  	      import CORSMiddleware

from dapi.db                          import Base, engine
from dapi.controllers.dapi_controller import start_dapi


Base.metadata.create_all(bind=engine)

dapi = FastAPI()

dapi.add_middleware(
	CORSMiddleware,
	allow_origins=['*'],  # or ['http://127.0.0.1:8000']
	allow_credentials=True,
	allow_methods=['*'],
	allow_headers=['*'],
)

start_dapi(dapi)

@dapi.get('/')
async def root():
	return { 'message': 'It works' }
