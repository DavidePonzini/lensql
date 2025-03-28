NAME=lensql
VENV=./venv
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

install: $(VENV) uninstall build
	$(VENV_BIN)/python -m pip install ./dist/*.whl

build: $(VENV)
	rm -rf dist/
	$(VENV_BIN)/python -m build

uninstall: $(VENV)
	$(VENV_BIN)/python -m pip uninstall -y $(NAME)

documentation:
	make html -C docs/

test: $(VENV) install
	$(VENV_BIN)/python -m pytest

upload: $(VENV) test documentation
	$(VENV_BIN)/python -m pip install --upgrade twine
	$(VENV_BIN)/python -m twine upload --verbose dist/*

download: $(VENV) uninstall
	$(VENV_BIN)/python -m pip install $(NAME)


