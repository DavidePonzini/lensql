SHELL=/bin/bash
NAME=lensql
VENV=./venv
ENV=.env
REQUIREMENTS=requirements.txt

ifeq ($(OS),Windows_NT)
	VENV_BIN=$(VENV)/Scripts
else
	VENV_BIN=$(VENV)/bin
endif

.PHONY: $(VENV)_upgrade run install build uninstall documentation test upload download

$(VENV):
	python -m venv $(VENV)
	touch -a $(REQUIREMENTS)
	$(VENV_BIN)/python -m pip install --upgrade -r $(REQUIREMENTS)

$(VENV)_upgrade: $(VENV)
	$(VENV_BIN)/python -m pip install --upgrade -r $(REQUIREMENTS)

$(ENV):
	cp $(ENV).template $(ENV)

run: $(ENV) install
	source $(ENV) && $(VENV_BIN)/jupyter-lab docker/notebook.ipynb

install: uninstall build
	$(VENV_BIN)/python -m pip install ./dist/*.whl

build: venv
	rm -rf dist/
	$(VENV_BIN)/python -m build

uninstall:
	$(VENV_BIN)/python -m pip uninstall -y $(NAME)

documentation:
	make html -C docs/

test: install
	$(VENV_BIN)/python -m pytest

upload: test documentation
	$(VENV_BIN)/python -m pip install --upgrade twine
	$(VENV_BIN)/python -m twine upload --verbose dist/*

download: uninstall
	$(VENV_BIN)/python -m pip install $(NAME)


