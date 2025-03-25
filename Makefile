SHELL=/bin/bash
VENV=venv
REQUIREMENTS=requirements.txt
ENV=.env

ifeq ($(OS),Windows_NT)
	VENV_BIN=$(VENV)/Scripts
else
	VENV_BIN=$(VENV)/bin
endif


.PHONY: $(VENV)_upgrade start

start: $(VENV) $(ENV) $(JUPYTER_CONFIG_DIR)
	sudo service postgresql start
	source $(ENV) && source $(VENV_BIN)/activate && jupyterhub

$(VENV):
	python -m venv --clear $(VENV)
	touch -a $(REQUIREMENTS)
	$(VENV_BIN)/python -m pip install -r $(REQUIREMENTS)

$(VENV)_upgrade: $(VENV)
	$(VENV_BIN)/python -m pip install --upgrade -r $(REQUIREMENTS)

$(ENV):
	cp ENV.template $(ENV)

$(JUPYTER_CONFIG_DIR):
	source $(ENV) && $(VENV_BIN)/jupyter-lab --generate-config





