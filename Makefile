SHELL := /bin/bash

VENV=./venv
REQUIREMENTS_SERVER=server/requirements.txt
REQUIREMENTS_DOCKER=docker/requirements.txt
REQUIREMENTS_PYPI=pypi/requirements.txt

ifeq ($(OS),Windows_NT)
	VENV_BIN=$(VENV)/Scripts
else
	VENV_BIN=$(VENV)/bin
endif

.PHONY: $(VENV)_upgrade run start psql


start:
	docker compose down
	docker rmi lensql-server
	docker compose up -d

psql:
	docker exec -it lensql-db-1 psql -U postgres

run: $(VENV)
	make -C pypi install VENV=../$(VENV)
	$(VENV_BIN)/jupyter-lab docker/notebook.ipynb


$(VENV):
	python -m venv $(VENV)
	$(VENV_BIN)/python -m pip install --upgrade -r $(REQUIREMENTS_SERVER) -r $(REQUIREMENTS_DOCKER) -r $(REQUIREMENTS_PYPI)

$(VENV)_upgrade: $(VENV)
	$(VENV_BIN)/python -m pip install --upgrade -r $(REQUIREMENTS_SERVER) -r $(REQUIREMENTS_DOCKER) -r $(REQUIREMENTS_PYPI)
