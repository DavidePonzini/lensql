SHELL := /bin/bash

VENV=./venv
REQUIREMENTS_SERVER=server/requirements.txt

ifeq ($(OS),Windows_NT)
	VENV_BIN=$(VENV)/Scripts
else
	VENV_BIN=$(VENV)/bin
endif

.PHONY: $(VENV)_upgrade start psql psql_users


start:
	docker compose down
	docker rmi lensql-server || :
	make -C webui copy
	docker compose up

psql:
	docker exec -it lensql_db psql -U postgres

psql_users:
	docker exec -it lensql_db_users psql -U postgres

$(VENV):
	python -m venv $(VENV)
	$(VENV_BIN)/python -m pip install --upgrade -r $(REQUIREMENTS_SERVER)

$(VENV)_upgrade: $(VENV)
	$(VENV_BIN)/python -m pip install --upgrade -r $(REQUIREMENTS_SERVER)
