SHELL := /bin/bash

VENV=./venv
REQUIREMENTS_SERVER=server/requirements.txt

COMPOSE_PROJECT_NAME=$(subst .,,$(notdir $(patsubst %/,%,$(CURDIR))))

ifeq ($(OS),Windows_NT)
	VENV_BIN=$(VENV)/Scripts
else
	VENV_BIN=$(VENV)/bin
endif

.PHONY: $(VENV)_upgrade dev prod stop setup psql psql_users active_users dump clean locales_extract locales_compile

dev: stop locales_compile
	docker compose --profile dev up --build

prod: stop locales_compile
	docker compose --profile prod up -d --build

stop:
	docker compose --profile dev --profile prod down

setup:
	docker exec $(COMPOSE_PROJECT_NAME)_server python /app/server/setup.py

psql:
	docker exec -it $(COMPOSE_PROJECT_NAME)_db_admin psql -U postgres

psql_users:
	docker exec -it $(COMPOSE_PROJECT_NAME)_db_users psql -U postgres

active_users:
	docker exec -t $(COMPOSE_PROJECT_NAME)_db_admin psql -U postgres -c "SELECT * FROM lensql.v_active_users;"

dump:
	docker exec -t $(COMPOSE_PROJECT_NAME)_db_admin pg_dump -U postgres -n lensql > dump_admin_$(shell date +'%Y.%m.%d-%H.%M.%S').sql
	docker exec -t $(COMPOSE_PROJECT_NAME)_db_users pg_dumpall -U postgres > dump_users_$(shell date +'%Y.%m.%d-%H.%M.%S').sql

locales_extract: $(VENV)
	$(VENV_BIN)/pybabel extract -F server/babel.cfg -o server/messages.pot server/
	$(VENV_BIN)/pybabel update -i server/messages.pot -d server/locales
	rm -r server/messages.pot

locales_compile:
	$(VENV_BIN)/pybabel compile -d server/locales
	

$(VENV):
	python -m venv $(VENV)
	$(VENV_BIN)/python -m pip install --upgrade -r $(REQUIREMENTS_SERVER)

$(VENV)_upgrade: $(VENV)
	$(VENV_BIN)/python -m pip install --upgrade -r $(REQUIREMENTS_SERVER)

clean:
	find . -type d -name '__pycache__' -print0 | xargs -0 rm -r || true
	rm -f server/messages.pot
	find server/locales -name '*.mo' -delete

