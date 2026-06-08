SHELL := /usr/bin/env bash
PYTHON ?= python3
VENV ?= venv
PIP := $(VENV)/bin/pip
PYTEST := $(VENV)/bin/pytest

.PHONY: help venv install install-mcp test test-mcp-live examples

help:
	@echo "nlp2env"
	@echo "  make install      pip install -e ."
	@echo "  make install-mcp  pip install -e \".[mcp]\""
	@echo "  make test         pytest"
	@echo "  make test-mcp-live  MCP stdio e2e (tmp .env)"
	@echo "  make examples     run examples/run-e2e.sh"

venv:
	@test -x "$(PIP)" || $(PYTHON) -m venv "$(VENV)"

install: venv
	$(PIP) install -e .

install-mcp: venv
	$(PIP) install -e ".[mcp]"

test: install-mcp
	$(PYTEST) tests/ -v

test-mcp-live: install-mcp
	./scripts/test-mcp-live.sh

examples: install-mcp
	./examples/run-e2e.sh
