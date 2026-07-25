# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

All commands use `uv` as the package manager. Prefer Makefile targets over raw commands (see `Makefile` or `make help` for the full list).

## Architecture

PyCFAST is a Python interface for building, running, and parsing [CFAST](https://pages.nist.gov/cfast/) fire simulation models. CFAST uses Fortran namelist (`.in`) files as input and produces CSV result files. `CFASTParser` reads an existing `.in` file via `f90nml` and reconstructs component objects into a `CFASTModel`.

### Gotchas and conventions

- `CFASTComponent.__setattr__` calls `_validate()` on every public attribute write once the component is `_initialized = True`. To apply several attribute changes atomically, toggle `_initialized` off, set the attributes, call `_validate()`, then turn it back on (this is what `CFASTModel._apply_kwargs` does).
- Component routing is driven by `_COMPONENT_SPECS` (a `kind -> (cls, model_attr, label, id_fields)` table) which is the single source of truth shared by `add()`, `_update_component()`, and `_resolve_identifier()`.
- `NamelistRecord` (`utils/namelist.py`) silently skips `None` values when serializing to Fortran namelist format.
- All public API is exported from `src/pycfast/__init__.py`.
