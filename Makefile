SHELL := /bin/bash

VENV=./venv
REQUIREMENTS_SERVER=server/requirements.txt

ifeq ($(OS),Windows_NT)
	VENV_BIN=$(VENV)/Scripts
else
	VENV_BIN=$(VENV)/bin
endif

.PHONY: $(VENV)_upgrade start deploy setup psql psql_users active_users dump clean

start:
	docker compose --profile dev down
	docker compose --profile dev up --build

deploy:
	docker compose --profile prod down
	docker compose --profile prod up -d --build

setup:
	docker exec lensql_server python /app/server/setup.py

psql:
	docker exec -it lensql_db_admin psql -U postgres

psql_users:
	docker exec -it lensql_db_users psql -U postgres

active_users:
	docker exec -t lensql_db_admin psql -U postgres -c "SELECT * FROM lensql.v_active_users;"

dump:
	docker exec -t lensql_db_admin pg_dump -U postgres -n lensql > dump_admin_$(shell date +'%Y.%m.%d-%H.%M.%S').sql
	docker exec -t lensql_db_admin pg_dumpall -U postgres > dump_users_$(shell date +'%Y.%m.%d-%H.%M.%S').sql

$(VENV):
	python -m venv $(VENV)
	$(VENV_BIN)/python -m pip install --upgrade -r $(REQUIREMENTS_SERVER)

$(VENV)_upgrade: $(VENV)
	$(VENV_BIN)/python -m pip install --upgrade -r $(REQUIREMENTS_SERVER)

clean:
	find . -type d -name '__pycache__' -print0 | xargs -0 rm -r

