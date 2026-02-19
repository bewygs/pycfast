.PHONY: help

help:
	@echo "Usage:"
	@echo "  make install            Install the package for personnal use"
	@echo "  make install-dev        Install the package in development mode with dev dependencies"
	@echo "  make install-docs       Install the package with documentation dependencies"
	@echo "  make install-examples   Install the package with examples dependencies"
	@echo "  make install-all        Install all dependencies (dev, docs, examples)"
	@echo "  make test               Run all tests"
	@echo "  make test-units         Run unit tests only"
	@echo "  make test-verif         Run verification tests only"
	@echo "  make cov                Run tests with coverage report"
	@echo "  make check              Lint the code with ruff"
	@echo "  make format             Format the code with ruff"
	@echo "  make type               Type check the code with mypy"
	@echo "  make clean              Clean build artifacts and cache"
	@echo "  make doc                Build and serve documentation"
	@echo "  make build              Build the package wheel"
	@echo "  make publish            Publish package to PyPI"
	@echo "  make pre-commit         Run pre-commit hooks"
	@echo "  make allci              Run all CI steps (check, format, type, test, coverage)"

install:
	uv sync --no-dev

install-dev:
	uv sync --extra dev

install-docs:
	uv sync --extra docs

install-examples:
	uv sync --extra examples

install-all:
	uv sync --extra dev --extra docs --extra examples

test:
	uv run pytest tests/

test-units:
	uv run pytest tests/units/

test-verif:
	uv run pytest tests/verification_tests/

cov:
	uv run pytest --cov=src/pycfast tests/ --cov-report=term-missing --cov-report=html

check:
	uv run ruff check .

format:
	uv run ruff format .

type:
	uv run mypy src/

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf .pytest_cache/
	rm -rf docs/build/
	rm -rf docs/source/auto_examples/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

doc:
	cd docs && uv run sphinx-build -b html source build/html
	@echo "Documentation built! Open $(PWD)/docs/build/html/index.html in your browser"

build:
	uv build

publish:
	uv publish

pre-commit:
	uv run pre-commit run --all-files

allci: check format type cov
	@echo "All CI steps completed!"
