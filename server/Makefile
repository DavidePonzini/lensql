SHELL := /bin/bash

VENV=./venv
ENV=.env
REQUIREMENTS=requirements.txt

ifeq ($(OS),Windows_NT)
	VENV_BIN=$(VENV)/Scripts
else
	VENV_BIN=$(VENV)/bin
endif

.PHONY: start start_bg $(VENV)_upgrade

start: $(ENV) $(VENV)
	sudo service postgresql start
	source $(ENV) && $(VENV_BIN)/python ./main.py

start_bg: $(ENV) $(VENV)
	sudo service postgresql start
	mkdir -p log
	source $(ENV) && nohup $(VENV_BIN)/python ./main.py > log/$(shell date +%Y-%m-%d.%H:%M:%S).txt 2>&1 &

$(ENV):
	cp $(ENV).template $(ENV)

$(VENV):
	python -m venv $(VENV)
	$(VENV_BIN)/python -m pip install --upgrade -r $(REQUIREMENTS)

$(VENV)_upgrade: $(VENV)
	$(VENV_BIN)/python -m pip install --upgrade -r $(REQUIREMENTS)