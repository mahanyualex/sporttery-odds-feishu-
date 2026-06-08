PYTHON ?= python

.PHONY: help install test lint clean help-cli

help:
	@echo "Available targets:"
	@echo "  install   - create local env dependencies"
	@echo "  test      - run pytest"
	@echo "  help-cli  - show odds_tool CLI help"
	@echo "  clean     - remove caches and runtime artifacts"

install:
	$(PYTHON) -m pip install -r requirements.txt

test:
	$(PYTHON) -m pytest tests -q

help-cli:
	$(PYTHON) -m odds_tool.main --help

clean:
	find . -type d -name '__pycache__' -prune -exec rm -rf {} +
	rm -rf .pytest_cache tests/.tmp-cache cache logs
