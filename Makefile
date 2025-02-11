########## Makefile start ##########
# Author: Davide Ponzini

VENV=venv
REQUIREMENTS=requirements.txt

ifeq ($(OS),Windows_NT)
	VENV_BIN=$(VENV)/Scripts
else
	VENV_BIN=$(VENV)/bin
endif


venv:
	python -m venv --clear $(VENV)
	touch -a $(REQUIREMENTS)
	$(VENV_BIN)/python -m pip install --upgrade -r $(REQUIREMENTS)


########## Makefile end ##########

JUPYTER_CONFIG_DIR=notebook/.config

$(JUPYTER_CONFIG_DIR):
	export JUPYTER_CONFIG_DIR=$(JUPYTER_CONFIG_DIR) && $(VENV_BIN)/jupyter notebook --generate-config

start:
	export JUPYTER_CONFIG_DIR=$(JUPYTER_CONFIG_DIR) && $(VENV_BIN)/jupyter notebook

