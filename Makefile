SHELL := /bin/bash

VENV=./venv
REQUIREMENTS_SERVER=server/requirements.txt

ifeq ($(OS),Windows_NT)
	VENV_BIN=$(VENV)/Scripts
else
	VENV_BIN=$(VENV)/bin
endif

USER_FILE = users.txt
USERS = $(shell cat $(USER_FILE))

DB=

.PHONY: $(VENV)_upgrade start psql psql_users users


start:
	docker compose down
	docker compose up --build

users: $(USERS)

%:
	@docker exec lensql_db /app/add_user $@
	@docker exec lensql_db_users /app/add_user $@

psql:
	docker exec -it lensql_db psql -U postgres $(BD)

psql_users:
	docker exec -it lensql_db_users psql -U postgres $(DB)

$(VENV):
	python -m venv $(VENV)
	$(VENV_BIN)/python -m pip install --upgrade -r $(REQUIREMENTS_SERVER)

$(VENV)_upgrade: $(VENV)
	$(VENV_BIN)/python -m pip install --upgrade -r $(REQUIREMENTS_SERVER)
