.PHONY: lint format test

all: test lint

format:
	uv run ruff check --fix

lint:
	uv run ruff check
	uv run mypy ./thingsmith

test:
	uv run -m pytest

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
