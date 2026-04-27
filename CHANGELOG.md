# Changelog
All notable changes to PyCFAST are documented in this file.

## [0.2.0] - 2026-04-27

First Beta release.

### New features
- `Fire`: support dict format for `data_table` with named columns (#94)
- `CFASTModel.add()`: now accepts any component type, replacing specific `add_*()` methods (#112)

### API changes
- `Material`: `thickness`, `conductivity`, `density`, `specific_heat` are now required
- `Device`: `setpoint` and `rti` required for `HEAT_DETECTOR`/`SPRINKLER`; `spray_density` required for `SPRINKLER`
- `Fire`: `set_point` required when `ignition_criterion` is set
- `CFASTModel`: removed dict-like access (`model['compartments']`); use `model.compartments` directly

### Fixes
- `CFASTModel.run()`: CFAST executable resolution raises `FileNotFoundError` with a clear message for each failed path (explicit, `$CFAST` env var, PATH) (#111)
- Enhanced validation across all components with stricter rules and clearer error messages (#109)
- All components now validate on attribute assignment after initialization (#109)

### Internal refactoring
- Removed `__repr_html__` and `build_card` HTML methods from `CFASTModel` (#96)
- Doctests added for all public components; `make test` and `make test-doctest` now include them (#109)
- Documentation and dependency updates

## [0.1.4] - 2026-04-17
- Implement base component class for all CFAST components (#85)
- Add input validation for all components (#59)
- Rename component classes from plural to singular (#83)
- Replace logger with warnings for error handling (#88)
- Use Path for handling file paths and remove deprecated parameters (#87)
- Refactor CFASTModel methods to avoid repetition (#86)
- Add Windows CI for latest CFAST commit (#76)
- Update Python version to 3.14
- Fix missing `_validate()` in `__setitem__` for some components (#65)
- Documentation and dependency updates

## [0.1.3] - 2026-02-28
- Remove CFAST binary distribution due to complexity (#34)
- Add testing for multiple CFAST versions on Windows and Linux from version 7.7.0 to 7.7.5 (#33)
- Refactor Dockerfile
- Add CODE_OF_CONDUCT.md
- Improve documentation and installation instructions (#35, #36)

## [0.1.2] - 2026-02-25
- Add wheels with CFAST precompiled binaries for Linux (#21)
- Add bug report and feature request issue templates
- Add CITATION.cff file with Zenodo DOI
- Update documentation and example improvements
- Improve CI/CD workflows (Windows testing, workflow dispatch)

## [0.1.1] - 2026-02-19
- Release made for Zenodo archived (10.5281/zenodo.18703351)

## [0.1.0] - 2026-02-19
- Initial release, compatible with CFAST 7.7.5