SHELL := /usr/bin/env bash
PYTHON ?= python3
VENV ?= venv
PIP := $(VENV)/bin/pip
PYTEST := $(VENV)/bin/pytest

.PHONY: help venv install install-mcp test test-mcp-live examples examples-multilang examples-all

help:
	@echo "nlp2env"
	@echo "  make install            pip install -e ."
	@echo "  make install-mcp        pip install -e \".[mcp]\""
	@echo "  make test               pytest"
	@echo "  make test-mcp-live      MCP stdio e2e (tmp .env)"
	@echo "  make examples           szybkie e2e (~30s)"
	@echo "  make examples-multilang 26 promptów LLM/Ollama, 16 języków (~3 min)"
	@echo "  make examples-all       examples + examples-multilang"

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

examples-multilang: install-mcp
	export SMTP_PASSWORD="$${SMTP_PASSWORD:-e2e-test-secret-42}"; \
	bash examples/write/smtp-email/e2e-multilang.sh

examples-all: examples examples-multilang
	@echo "ALL EXAMPLES + MULTILANG OK"
