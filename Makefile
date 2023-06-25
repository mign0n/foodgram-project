WORKDIR = backend
VENV = $(WORKDIR)/venv
MANAGE = python $(WORKDIR)/manage.py
DEVREQS = dev-requirements.txt
REQS = requirements.txt

deps:
	pip install --upgrade pip pip-tools
	pip-compile --output-file $(WORKDIR)/$(REQS) --resolver=backtracking $(WORKDIR)/pyproject.toml

dev-deps: deps
	pip-compile --extra=dev --output-file $(WORKDIR)/$(DEVREQS) --resolver=backtracking $(WORKDIR)/pyproject.toml

install-deps: deps
	pip-sync $(WORKDIR)/$(REQS)

install-dev-deps: install-deps dev-deps
	pip-sync $(WORKDIR)/$(DEVREQS)

run:
	VENV/bin/$(MANAGE) runserver

style:
	black $(WORKDIR)
	isort $(WORKDIR)
	flake8 --toml-config=$(WORKDIR)/pyproject.toml $(WORKDIR)
	mypy $(WORKDIR)
	pymarkdown scan .

test:
	pytest
