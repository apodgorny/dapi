import os

from fastapi                 import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from dapi.controller         import dapi


os.environ['PROJECT_PATH'] = os.path.dirname(
	os.path.dirname(
		os.path.abspath(__file__)
	)
)

app = FastAPI()
app.add_middleware(
	CORSMiddleware,
	allow_origins     = ['*'], # or ['http://127.0.0.1:8000']
	allow_methods     = ['*'],
	allow_headers     = ['*'],
	allow_credentials = True,
)
dapi.start(app)

@app.on_event('startup')
async def startup_event():
	await dapi.initialize_services()