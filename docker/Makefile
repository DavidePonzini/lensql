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

.PHONY: run build

run: build
	docker run --rm -p 8888:8888 $(DOCKER_IMAGE)

build:
	docker build -t $(DOCKER_IMAGE) .

$(ENV):
	cp $(ENV).template $(ENV)


