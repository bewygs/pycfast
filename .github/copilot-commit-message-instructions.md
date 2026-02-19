# Commit Message Instructions for PyCFAST

Follow conventional commit format: `<type>: <description>`

## Types
- **DEV**: development tool or utility
- **FIX**: Bug fix  
- **DOC**: Documentation changes
- **BLD**: Dependencies/build system (Makefile, pyproject.toml, ...)
- **STY**: Code formatting
- **TST**: addition or modification of tests
- **MAINT**: maintenance commit (refactoring, typos, etc.)
- **ENH**: enhancement
- **CI**: CI/CD workflows
- **REL**: release commit (version bump, changelog update, etc.)
- **chore**: Other maintenance

## Rules
- Use imperative mood ("Add" not "Added")
- Start with capital letter
- No period at end
- Keep under 50 characters
- Reference issues when relevant

## Examples
```
ENH: add CFAST 7.8 ventilation support
FIX: handle missing executable gracefully
DOC: update installation guide for uv  
TST: add compartment validation tests
CI: migrate workflows to use uv
BLD: bump pandas minimum to 2.1.0
DEV: add mypy type checking to Makefile
MAINT: refactor simulation environment module
STY: apply ruff formatting rules
```

## Breaking Changes
Add `!` and footer:
```
ENH!: redesign Model class interface

BREAKING CHANGE: Model.run() returns SimulationResult object
```
