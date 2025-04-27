.PHONY: lint format test

all: test lint

format:
	uv run ruff check --fix

lint:
	uv run ruff check
	uv run mypy ./pyfinity

test:
	uv run pytest

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
