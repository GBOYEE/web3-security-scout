.PHONY: install test coverage lint format type-check security clean

install:
	pip install -r requirements.txt -r requirements-dev.txt

test:
	PYTHONPATH=src pytest tests/

coverage:
	PYTHONPATH=src pytest --cov=src --cov-report=html --cov-report=xml tests/

lint:
	flake8 src tests

format:
	black src tests
	isort src tests

type-check:
	mypy src tests --ignore-missing-imports

security:
	bandit -r src tests
	safety check

clean:
	rm -rf .coverage coverage.xml htmlcov/ .pytest_cache/ .mypy_cache/ build/ dist/ *.egg-info
