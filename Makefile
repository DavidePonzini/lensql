SHELL=/bin/bash
VENV=venv
REQUIREMENTS=requirements.txt
ENV=.env
JUPYTER_CONFIG_DIR=jupyterhub

ifeq ($(OS),Windows_NT)
	VENV_BIN=$(VENV)/Scripts
else
	VENV_BIN=$(VENV)/bin
endif


.PHONY: $(VENV)_upgrade start

start: $(VENV) $(ENV) allowed_users
	@if [ "$$EUID" -ne 0 ]; then $(VENV_BIN)/python -m dav_tools.messages error "Server must be started by root user"; exit 1; fi
	npm install -g configurable-http-proxy
	service postgresql start
# sets LLM key
# activates venv, needed to be able to run jupyterhub-singleuser properly
# changes directory to keep generated files in the right place
	source $(ENV) && source $(VENV_BIN)/activate && cd $(JUPYTER_CONFIG_DIR) && jupyterhub

$(VENV):
	python -m venv --clear $(VENV)
	touch -a $(REQUIREMENTS)
	$(VENV_BIN)/python -m pip install -r $(REQUIREMENTS)

$(VENV)_upgrade: $(VENV)
	$(VENV_BIN)/python -m pip install --upgrade -r $(REQUIREMENTS)

$(ENV):
	cp $(ENV).template $(ENV)

allowed_users:
	touch allowed_users



