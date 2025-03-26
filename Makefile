SHELL=/bin/bash
VENV=venv
REQUIREMENTS=requirements.txt
ENV=.env
DOCKER_IMAGE=davideponzini/lensql

ifeq ($(OS),Windows_NT)
	VENV_BIN=$(VENV)/Scripts
else
	VENV_BIN=$(VENV)/bin
endif

.PHONY: $(VENV)_upgrade start build

run: build
	docker run --rm -p 8888:8888 $(DOCKER_IMAGE)

build:
	docker build -t $(DOCKER_IMAGE) .

start: $(VENV) $(ENV)
	source $(ENV) && $(VENV_BIN)/jupyter-lab

$(VENV):
	python -m venv $(VENV)
	touch -a $(REQUIREMENTS)
	$(VENV_BIN)/python -m pip install -r $(REQUIREMENTS)

$(VENV)_upgrade: $(VENV)
	$(VENV_BIN)/python -m pip install --upgrade -r $(REQUIREMENTS)

$(ENV):
	cp $(ENV).template $(ENV)



