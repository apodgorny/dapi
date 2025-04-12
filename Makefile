#!make
include .env

.PHONY: start clear test apitest check

check:
	echo $(PROJECT_PATH)

run:
	clear && cd $(PROJECT_PATH) && PYTHONPATH=$(pwd) uvicorn app.app:app --reload

test:
	clear && PYTHONPATH=$(PROJECT_PATH) pytest

apitest:
	clear && schemathesis run http://127.0.0.1:8000/openapi.json --base-url=http://localhost:8000 --experimental=openapi-3.1 || true && rm "$(PROJECT_PATH)/dapi.db"

clear:
	clear && rm "$(PROJECT_PATH)/dapi.db" && echo "Cleared database"
