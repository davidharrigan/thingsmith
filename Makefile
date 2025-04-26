.PHONY: lint format all

all: format lint

format:
	uv run ruff check --fix

lint:
	uv run ruff check
	uv run mypy ./pyfinity

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
