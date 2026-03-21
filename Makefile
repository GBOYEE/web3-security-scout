.PHONY: install test format lint run clean

install:
	pip install -r requirements.txt
	pip install -e .

install-dev:
	pip install -r requirements-dev.txt

test:
	export PYTHONPATH=src && pytest -v tests/

format:
	black src tests
	isort src tests

lint:
	flake8 src tests

clean:
	rm -rf __pycache__ .pytest_cache .coverage dist build *.egg-info