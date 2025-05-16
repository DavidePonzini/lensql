SHELL := /bin/bash

VENV=./venv
REQUIREMENTS_SERVER=server/requirements.txt

ifeq ($(OS),Windows_NT)
	VENV_BIN=$(VENV)/Scripts
else
	VENV_BIN=$(VENV)/bin
endif

DEV_DOCKER_COMPOSE_FILE = docker-compose.yml
PROD_DOCKER_COMPOSE_FILE = docker-compose.prod.yml

.PHONY: $(VENV)_upgrade start start_prod psql psql_users setup

start:
	docker compose -f $(DEV_DOCKER_COMPOSE_FILE) down
	docker compose -f $(DEV_DOCKER_COMPOSE_FILE) up --build

deploy:
	docker compose -f $(PROD_DOCKER_COMPOSE_FILE) down
	docker compose -f $(PROD_DOCKER_COMPOSE_FILE) up -d --build

setup:
	docker exec lensql_server python /app/setup.py

psql:
	docker exec -it lensql_db_admin psql -U postgres

psql_users:
	docker exec -it lensql_db_users psql -U postgres

dump:
	docker exec -t lensql_db_admin pg_dump -U postgres -n lensql > dump_$(shell date +'%Y.%m.%d-%H.%M.%S').sql

$(VENV):
	python -m venv $(VENV)
	$(VENV_BIN)/python -m pip install --upgrade -r $(REQUIREMENTS_SERVER)

$(VENV)_upgrade: $(VENV)
	$(VENV_BIN)/python -m pip install --upgrade -r $(REQUIREMENTS_SERVER)
