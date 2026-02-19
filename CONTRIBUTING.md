# Contributing guidelines

## Introduction

Thank you for your interest in contributing to PyCFAST! This comprehensive guide will
help you get started with development, testing, and understanding our workflow.

## Starting

Follow these steps to set up your development environment:

1. **Fork & Clone**
   - Fork [PyCFAST on GitHub](https://github.com/bewygs/pycfast)
   - Clone your fork:
     ```bash
     git clone https://github.com/YOUR_USERNAME/pycfast.git
     cd pycfast
     ```

2. **Set Up Development Environment**
   - **uv (Recommended):**

     Install [uv](https://docs.astral.sh/uv/) and run:

     ```bash
     make install-dev
     ```
   - **Or with pip:**
     ```bash
     python -m venv .venv
     source .venv/bin/activate
     pip install -e ".[dev]"
     ```

3. **Generate Local Verification Data**

   Before running tests, generate local reference data (required for verification tests):

   ```bash
   cd tests/
   python generate_verif_data.py --local
   ```

   > **Note:** Because CFAST uses a Fortran compiler, which can produce small numerical differences between systems and compilers, always generate verification data locally for your tests.
   You also need to have CFAST installed and accessible in your PATH. You can download it from the [NIST CFAST page](https://pages.nist.gov/cfast/index.html).

4. **Run Tests & Checks**

   Ensure everything is set up correctly by running:
   ```bash
   make allci  # Or: ruff check . && ruff format . && mypy src/ && pytest tests/
   ```

## Development Workflow

If you want to solve an issue or add a feature, follow these steps:

1. **Create a branch**
   ```bash
   git checkout -b feature/your-feature
   ```

2. **Write code and tests**
   - Add features or solve issues in `src/pycfast/`
   - Add/modify tests in `tests/units/`

3. **Check CI locally (check, format, type, test, coverage)**
   ```bash
   make allci
   ```

For commit messages, we follow this format:

```bash
DEV: development tool or utility
FIX: Bug fix
DOC: Documentation changes
BLD: Dependencies/build system (Makefile, pyproject.toml, ...)
STY: Code formatting
TST: addition or modification of tests
MAINT: maintenance commit (refactoring, typos, etc.)
ENH: enhancement
CI: CI/CD workflows
REL: release commit (version bump, changelog update, etc.)
chore: Other maintenance
```

4. **Commit and push**
   ```bash
   git add .
   git commit -m "ENH: short description"
   git push origin feature/your-feature
   ```

5. **Open a Pull Request** on [PyCFAST GitHub](https://github.com/bewygs/pycfast/pulls) page.

## Testing

We use [pytest](https://docs.pytest.org/en/stable/) for testing. Tests are located in the `tests/` directory and are categorized into:

- **Unit tests:**

  Fast checks for core modules run: 
  ```bash
  pytest tests/units/
  ```

- **Verification tests:**

  Compare PyCFAST with CFAST Verification cases. Ensure you have run `generate_verif_data.py --local`
  to create the necessary reference data. Run (can be slow depending on your system):
  ```bash
  pytest tests/verification_tests
  ```

- **Complete test suite:**

   Run all tests (units + verification) with:
   ```bash
   make test  # or pytest tests/
   ```

## Code Style

We use Python 3.10+ with type hints. Code formatting and linting is handled by
[ruff](https://docs.astral.sh/ruff/), and type checking uses [mypy](http://mypy-lang.org/).
You can run the following commands to check and format your code:

```bash
make format # or ruff format .
make check # or ruff check .
make type # or mypy src/
```

## Documentation

We use [Sphinx](https://www.sphinx-doc.org/) with [MyST](https://myst-parser.readthedocs.io/en/latest/)
for documentation. Use [Numpy-style docstrings](https://numpydoc.readthedocs.io/en/latest/format.html) and add or modify docs in `docs/source` or as docstrings. The documentation
for PyCFAST API reference is auto-generated from docstrings.

To build documentation locally:

- **With uv:**
```bash
make install-docs
make doc
```

- **Or with pip:**
```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[docs]"
cd docs && sphinx-build -b html source build/html
```
