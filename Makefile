.PHONY: help install test lint lint-check format format-check pre-commit clean check

.DEFAULT_GOAL := help

help:
	@echo "DaVinci Resolve MCP - Development Makefile"
	@echo ""
	@echo "Usage: make <target>"
	@echo ""
	@echo "Available targets:"
	@echo "  install      Install dependencies and pre-commit hooks"
	@echo "  test         Run tests with pytest"
	@echo "  lint         Run ruff check and auto-fix"
	@echo "  lint-check   Run ruff check without fixing"
	@echo "  format       Run ruff formatter"
	@echo "  format-check Run ruff format check"
	@echo "  check        Run lint-check, format-check, and test"
	@echo "  pre-commit   Run all pre-commit hooks"
	@echo "  clean        Remove temporary files and virtual environment"

install:
	uv sync --all-extras --dev
	uv run pre-commit install
	uv run pre-commit install --hook-type commit-msg

test:
	uv run python -m pytest --cov=src/davinci_resolve_mcp

lint:
	uv run ruff check --fix .

lint-check:
	uv run ruff check .

format:
	uv run ruff format .

format-check:
	uv run ruff format --check .

check: lint-check format-check test

pre-commit:
	uv run pre-commit run --all-files

clean:
	rm -rf .venv .pytest_cache .ruff_cache build dist *.egg-info .coverage htmlcov
	find . -type d -name "__pycache__" -exec rm -rf {} +

