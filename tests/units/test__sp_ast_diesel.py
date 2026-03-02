"""Tests for SP_AST_Diesel_1p1 dataset loader."""

from __future__ import annotations

import numpy as np
import pandas as pd

from pycfast.datasets import load_sp_ast_diesel_1p1

EXPECTED_COLUMNS = [
    "heat_of_combustion",
    "radiative_fraction",
    "soot_yield",
    "target_location_z",
    "max_trgsurt",
]


class TestLoadSpAstDiesel1p1:
    """Test suite for load_sp_ast_diesel_1p1 function."""

    def test_default_returns_full_dataframe(self) -> None:
        """Default call returns a DataFrame with correct shape, columns, and DESCR."""
        df = load_sp_ast_diesel_1p1()

        assert isinstance(df, pd.DataFrame)
        assert df.shape == (5000, 5)
        assert list(df.columns) == EXPECTED_COLUMNS
        assert "DESCR" in df.attrs

    def test_return_x_y_as_frame(self) -> None:
        """return_X_y=True returns (DataFrame, Series) with correct dimensions."""
        X, y = load_sp_ast_diesel_1p1(return_X_y=True)

        assert isinstance(X, pd.DataFrame)
        assert isinstance(y, pd.Series)
        assert X.shape == (5000, 4)
        assert list(X.columns) == EXPECTED_COLUMNS[:4]
        assert y.name == "max_trgsurt"

    def test_return_x_y_as_numpy(self) -> None:
        """return_X_y=True, as_frame=False returns numpy arrays."""
        X, y = load_sp_ast_diesel_1p1(return_X_y=True, as_frame=False)

        assert isinstance(X, np.ndarray)
        assert isinstance(y, np.ndarray)
        assert X.shape == (5000, 4)
        assert y.shape == (5000,)

    def test_no_missing_values(self) -> None:
        """Dataset contains no NaN values."""
        df = load_sp_ast_diesel_1p1()
        assert not df.isnull().any().any()

    def test_parameter_ranges(self) -> None:
        """Input parameters fall within expected bounds."""
        df = load_sp_ast_diesel_1p1()

        assert df["heat_of_combustion"].between(5.0, 50.0).all()
        assert df["radiative_fraction"].between(0.1, 0.5).all()
        assert df["soot_yield"].between(0.01, 0.15).all()
        assert df["target_location_z"].between(1.45, 5.45).all()
