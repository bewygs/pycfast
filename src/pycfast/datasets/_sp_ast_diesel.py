"""SP_AST_Diesel_1p1 dataset loader."""

from __future__ import annotations

from importlib import resources
from typing import TYPE_CHECKING

import numpy as np
import pandas as pd

if TYPE_CHECKING:
    from numpy.typing import NDArray

_INPUT_PARAMS = [
    "heat_of_combustion",
    "radiative_fraction",
    "soot_yield",
    "target_location_z",
]

_TARGET_NAME = "max_trgsurt"

_DESCR = """\
SP_AST_Diesel_1p1 Dataset
=========================

This dataset contains 5000 pre-computed CFAST simulation results
based on the ``SP_AST_Diesel_1p1.in`` validation model. Each sample
maps fire parameters to the maximum target surface temperature (TRGSURT).

**Base model**: SP_AST_Diesel_1p1.in

**Input features** (4):
  - ``heat_of_combustion`` (MJ/kg): Heat of combustion [5.0, 50.0]
  - ``radiative_fraction`` : Radiative fraction [0.1, 0.5]
  - ``soot_yield`` : Soot yield [0.01, 0.15]
  - ``target_location_z`` (m): Target device height above floor [1.45, 5.45]

**Target** (1):
  - ``max_trgsurt`` (°C): Maximum target surface temperature

**Sampling method**: Sobol quasi-random sequence (scrambled, seed=42)

**Number of samples**: 5000
"""

_DATA_FILE = "sp_ast_diesel_1p1.csv.gz"


def load_sp_ast_diesel_1p1(
    *,
    return_X_y: bool = False,
    as_frame: bool = True,
) -> (
    pd.DataFrame
    | tuple[pd.DataFrame, pd.Series]
    | tuple[NDArray[np.floating], NDArray[np.floating]]
):
    """Load the SP_AST_Diesel_1p1 pre-computed dataset.

    Returns 5000 CFAST simulation results based on the
    ``SP_AST_Diesel_1p1.in`` validation model, mapping fire parameters
    (heat of combustion, radiative fraction, soot yield, target height)
    to maximum target surface temperature (TRGSURT).

    Parameters
    ----------
    return_X_y : bool, default=False
        If ``True``, return ``(X, y)`` instead of a single DataFrame.
        ``X`` contains the 4 input features and ``y`` the target.
    as_frame : bool, default=True
        If ``True`` (default), return pandas objects.
        If ``False``, return numpy arrays (only effective when
        ``return_X_y=True``).

    Returns
    -------
    data : pd.DataFrame or tuple
        - If ``return_X_y=False``: a DataFrame with all columns.
          Access ``data.attrs["DESCR"]`` for a human-readable description.
        - If ``return_X_y=True`` and ``as_frame=True``:
          ``(X, y)`` as ``(pd.DataFrame, pd.Series)``.
        - If ``return_X_y=True`` and ``as_frame=False``:
          ``(X, y)`` as ``(np.ndarray, np.ndarray)``.

    Examples
    --------
    >>> from pycfast.datasets import load_sp_ast_diesel_1p1
    >>> df = load_sp_ast_diesel_1p1()
    >>> df.shape
    (5000, 5)

    >>> X, y = load_sp_ast_diesel_1p1(return_X_y=True)
    >>> X.shape
    (5000, 4)
    """
    data_dir = resources.files("pycfast.datasets") / "data"
    csv_path = data_dir / _DATA_FILE

    with resources.as_file(csv_path) as path:
        df = pd.read_csv(path)

    df.attrs["DESCR"] = _DESCR

    if not return_X_y:
        return df

    x_frame = df[_INPUT_PARAMS]
    y_series = df[_TARGET_NAME]

    if as_frame:
        return x_frame, y_series

    return x_frame.to_numpy(), y_series.to_numpy()
