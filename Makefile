.PHONY: lint format all

all: format lint

format:
	poetry run ruff check --fix

lint:
	poetry run ruff check
	poetry run mypy

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
