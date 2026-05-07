"""Shared utilities for comparing PyCFAST model results against reference CSV data.

- get_reference_data_dir: Locate reference data directories
- compare_model_to_reference_data: Compare model outputs to reference CSVs
"""

from __future__ import annotations

import re
import warnings
from pathlib import Path

import pandas as pd
import pytest

from pycfast.utils import CSV_READ_CONFIGS


def get_reference_data_dir(base_path: Path, data_local_dir: str, subdir: str) -> Path:
    """
    Get the reference data directory.

    Parameters
    ----------
        base_path: Path to the test file (typically Path(__file__).parent)
        data_local_dir: Name of the local data directory (e.g. 'verification_data_local')
        subdir: Subdirectory path under data_local_dir.

    Returns
    -------
        Path: The reference data directory to use
    """
    return base_path / data_local_dir / Path(subdir)


def compare_model_to_reference_data(
    results: dict, reference_data_dir: Path, prefix: str, tmp_path: Path
) -> None:
    """Compare model results dict of DataFrames to reference CSVs for a given prefix.

    Raises
    ------
        pytest.fail on mismatch or missing files.
    """
    if not reference_data_dir.exists():
        pytest.fail(f"Reference data directory does not exist: {reference_data_dir}")

    pattern = rf"^{re.escape(prefix)}(_[a-zA-Z]+\.csv|\.csv)$"
    ref_csv_files = [
        f
        for f in reference_data_dir.iterdir()
        if f.name.endswith(".csv") and re.match(pattern, f.name)
    ]

    if not ref_csv_files:
        pytest.fail(
            f"No reference CSV files found for prefix '{prefix}' in "
            f"{reference_data_dir}. Expected files matching pattern: {pattern}"
        )

    successful_comparisons = 0
    skipped_comparisons = 0

    for ref_csv_file in ref_csv_files:
        suffix = ref_csv_file.name.replace(prefix, "")
        suffix_clean = suffix.replace(".csv", "").replace("_", "")
        model_csv = None
        for key in results.keys():
            if key.endswith(suffix_clean):
                model_csv = results[key]
                break
        assert model_csv is not None, f"Missing model output {suffix_clean}"
        model_df = model_csv

        ref_csv = reference_data_dir / ref_csv_file.name

        read_params = CSV_READ_CONFIGS.get(suffix_clean, {})
        read_args = {k: v for k, v in read_params.items() if v is not None}
        try:
            ref_df = pd.read_csv(ref_csv, **read_args)  # type: ignore[call-overload]
        except pd.errors.EmptyDataError:
            warnings.warn(f"Reference CSV is empty: {ref_csv}", stacklevel=2)
            skipped_comparisons += 1
            continue
        except Exception as e:
            pytest.fail(f"Failed to read reference file {ref_csv}: {e}")

        if model_df.empty and ref_df.empty:
            warnings.warn(
                f"Both model and reference data are empty for {suffix_clean}",
                stacklevel=2,
            )
            skipped_comparisons += 1
            continue
        elif model_df.empty and not ref_df.empty:
            pytest.fail(
                f"Model output is empty but reference CSV is not for {suffix_clean}"
            )
        elif not model_df.empty and ref_df.empty:
            pytest.fail(
                f"Reference CSV is empty but model output is not for {suffix_clean}"
            )

        try:
            pd.testing.assert_frame_equal(
                model_df, ref_df, check_dtype=False, check_exact=True
            )
            successful_comparisons += 1
        except AssertionError as e:
            pytest.fail(
                f"DataFrame mismatch for {suffix}: {e}\nTemporary path: {tmp_path}"
            )

    if successful_comparisons == 0:
        pytest.fail(
            f"No successful comparisons performed for prefix '{prefix}'."
            f"Found {len(ref_csv_files)} files but {skipped_comparisons} were skipped"
        )
