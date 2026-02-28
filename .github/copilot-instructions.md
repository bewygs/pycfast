# PyCFAST Overview

PyCFAST is a Python interface for building, running, and analyzing CFAST fire simulation models. It allows you to programmatically create CFAST input files, execute simulations, and process results directly in Python. It's a pure Python library that does not require any CFAST-specific dependencies.

CFAST is a computer program that fire investigators, safety officials, researchers, and engineers can use to simulate the impact of past or potential fires and smoke in a specific building environment. CFAST is a two-zone fire model used to calculate the evolving distribution of smoke, fire gases and temperature throughout compartments of a building during a fire.

 ## Folder Structure

- `/src/pycfast`: Contains the source code for the library.
- `/examples`: Contains examples scripts showing how to use the library.
- `/docs`: Contains documentation for the project, a user guides and some script to keep the documentation up to date with CFAST official documentation.
- `/tests`: Contains tests that validate the functionality of the library.

## Libraries and Frameworks
 - python
 - pandas
 - f90nml

## Coding Standards

- Use ruff coding standard including formatting, linting, and best practices.
- Follow mypy for type checking.
- Use numpy docstring style for documentation.
- Stay Pythonic
- Follow SOLID and DRY principles where applicable.

## Environment Setup

When running command you can use the makefile commands to have the right environment with the right dependencies installed.