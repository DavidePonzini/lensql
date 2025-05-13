SHELL := /bin/bash

VENV=./venv
REQUIREMENTS_SERVER=server/requirements.txt

ifeq ($(OS),Windows_NT)
	VENV_BIN=$(VENV)/Scripts
else
	VENV_BIN=$(VENV)/bin
endif

USER_FILE = users.csv
USERS = $(shell cat $(USER_FILE))

DB=

.PHONY: $(VENV)_upgrade start psql psql_users users


start:
	docker compose down
	docker compose up --build

users:
	@while IFS=, read -r user password; do \
		docker exec lensql_server python /app/add_user.py "$$user" "$$password"; \
	done < $(USER_FILE)

psql:
	docker exec -it lensql_db_admin psql -U postgres

psql_users:
	docker exec -it lensql_db_users psql -U postgres $(DB)

$(VENV):
	python -m venv $(VENV)
	$(VENV_BIN)/python -m pip install --upgrade -r $(REQUIREMENTS_SERVER)

$(VENV)_upgrade: $(VENV)
	$(VENV_BIN)/python -m pip install --upgrade -r $(REQUIREMENTS_SERVER)
