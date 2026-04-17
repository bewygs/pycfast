# Changelog
All notable changes to PyCFAST are documented in this file.

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