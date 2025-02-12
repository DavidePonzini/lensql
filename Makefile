########## Makefile start ##########
# Author: Davide Ponzini

VENV=venv
REQUIREMENTS=requirements.txt

ifeq ($(OS),Windows_NT)
	VENV_BIN=$(VENV)/Scripts
else
	VENV_BIN=$(VENV)/bin
endif


$(VENV):
	python -m venv --clear $(VENV)
	touch -a $(REQUIREMENTS)
	$(VENV_BIN)/python -m pip install -r $(REQUIREMENTS)

$(VENV)_upgrade: $(VENV)
	$(VENV_BIN)/python -m pip install --upgrade -r $(REQUIREMENTS)


########## Makefile end ##########

JUPYTER_CONFIG_DIR=config

$(JUPYTER_CONFIG_DIR):
	export JUPYTER_CONFIG_DIR=$(JUPYTER_CONFIG_DIR) && $(VENV_BIN)/jupyter notebook --generate-config

start:
	sudo service postgresql start
	$(VENV_BIN)/jupyter notebook --config=$(JUPYTER_CONFIG_DIR)/jupyter_notebook_config.py
