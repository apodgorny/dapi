import os
from fastapi                          import FastAPI
from fastapi.middleware.cors  	      import CORSMiddleware

from dapi.controller import dapi
from dapi.middleware import enhance_openapi_schema

os.environ['PROJECT_PATH'] = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
app = FastAPI()

app.add_middleware(
	CORSMiddleware,
	allow_origins=['*'],  # or ['http://127.0.0.1:8000']
	allow_credentials=True,
	allow_methods=['*'],
	allow_headers=['*'],
)
app.middleware('http')(enhance_openapi_schema)

dapi.start(app)

@app.get('/')
async def root():
	return { 'message': 'DAPI is awesome.' }
