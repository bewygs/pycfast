"""
Datasets module for PyCFAST.

This module provides pre-computed datasets for examples. The datasets are bundled with
the package to avoid re-running expensive CFAST simulations.

"""

from ._sp_ast_diesel import load_sp_ast_diesel_1p1

__all__ = [
    "load_sp_ast_diesel_1p1",
]
