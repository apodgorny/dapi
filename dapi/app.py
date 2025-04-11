from fastapi                          import FastAPI
from fastapi.middleware.cors  	      import CORSMiddleware

from dapi.controllers.dapi_controller import dapi


app = FastAPI()

app.add_middleware(
	CORSMiddleware,
	allow_origins=['*'],  # or ['http://127.0.0.1:8000']
	allow_credentials=True,
	allow_methods=['*'],
	allow_headers=['*'],
)

dapi.start(app)

@app.get('/')
async def root():
	return { 'message': 'It works' }
