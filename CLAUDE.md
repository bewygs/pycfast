# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

All commands use `uv` as the package manager. Prefer Makefile targets over raw commands.

```bash
make install-dev    # Install package + dev dependencies (first-time setup)
make check          # Lint with ruff
make format         # Format with ruff
make type           # Type-check with mypy
make test           # Run all tests (units + verification)
make test-units     # Run unit tests only
make test-verif     # Run verification tests only
make cov            # Run tests with HTML coverage report
make allci          # Full CI pipeline (check, format, type, coverage)
```

Run a single test file:
```bash
uv run pytest tests/units/test_model.py -v --tb=short
```

Run a single test:
```bash
uv run pytest tests/units/test_model.py::test_function_name -v
```

## Architecture

PyCFAST is a Python interface for building, running, and parsing [CFAST](https://pages.nist.gov/cfast/) fire simulation models. CFAST uses Fortran namelist (`.in`) files as input and produces CSV result files.

### Core Flow

```
Python component objects
        ↓
CFASTModel.run() / CFASTModel.save()
        ↓
to_input_string() on each component → Fortran namelist .in file
        ↓
CFAST binary execution (subprocess)
        ↓
CSV result files → dict of pandas DataFrames
```

Reverse: `CFASTParser` reads an existing `.in` file via `f90nml` and reconstructs component objects into a `CFASTModel`.

### Component Model

All simulation elements are standalone classes (no shared base class):
- `SimulationEnvironment` — title, duration, time step, initial conditions
- `Compartment` — room geometry, materials, leakage
- `Material` — thermal properties referenced by ID from Compartment/Device
- `Fire` — heat release rate, chemistry, compartment placement
- `WallVent` / `CeilingFloorVent` / `MechanicalVent` — connections between compartments by ID
- `Device` — targets (heat transfer probes) and detectors (heat/smoke/sprinkler)
- `SurfaceConnection` — adjacent surface heat transfer

Each component implements:
- `to_input_string()` → Fortran namelist fragment via `NamelistRecord`
- `_validate()` → raises on invalid config
- `__getitem__` / `__setitem__` → dict-like parameter access
- `__repr_html__()` → Jupyter card rendering

### CFASTModel (`model.py`)

The main orchestrator. Key responsibilities:
- Holds lists of all component instances
- `_validate_dependencies()` — checks all cross-referenced IDs (compartments, materials) exist before running
- `run()` — serializes to `.in`, calls CFAST binary, parses CSV output into DataFrames
- `save()` — writes `.in` file only
- `update_*_params()` / `add_*()` — bulk/individual component management

Results dict keys match CFAST CSV output suffixes: `compartments`, `devices`, `masses`, `vents`, `walls`, `zone`, `diagnostics` (optional).

### NamelistRecord (`utils/namelist.py`)

Low-level builder for Fortran namelist format. Converts Python types to CFAST-compatible strings (`.TRUE.`/`.FALSE.` for bools, quoted strings, arrays). `None` values are silently skipped. All `to_input_string()` methods use this.

### CFASTParser (`parsers/cfast_parser.py`)

Parses existing `.in` files (via `f90nml`) into a full `CFASTModel`. Has dedicated `_parse_*_block()` methods for each namelist section (`HEAD`, `COMP`, `VENT`, `FIRE`, `DEVC`, `CONN`, etc.). Entry point: `parse_cfast_file(path)`.

### Tests

- `tests/units/` — test each component class in isolation
- `tests/verification_tests/` — run real CFAST verification models against NIST reference data

Pytest markers: `slow` (long-running), `local` (requires local CFAST + verification data).

## Standards

- **Ruff**: line-length 88, rules E, W, F, I, B, C4, UP, D (numpy docstrings)
- **MyPy**: strict mode, Python 3.14 target
- All public API is exported from `src/pycfast/__init__.py`