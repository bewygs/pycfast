"""Verification utilities for CFAST model testing.

This module provides utilities for comparing PyCFAST model results against
reference verification data:

- get_cfast_version: Extract CFAST version from command line output
- get_verification_data_dir: Locate verification data directories
- compare_model_to_verification_data: Compare model outputs to reference CSVs
"""

from __future__ import annotations

import re
import subprocess
import warnings
from pathlib import Path

import pandas as pd
import pytest

from pycfast.utils import CSV_READ_CONFIGS


def get_cfast_version() -> str | None:
    """
    Get CFAST version from environment variable or by running cfast command.

    Returns
    -------
    str | None
        CFAST version string (e.g., "7.7.5") or None if not available
    """
    try:
        result = subprocess.run(["cfast"], capture_output=True, text=True, timeout=10)

        output = result.stdout + result.stderr
        version_patterns = [
            r"Test CFAST (\d+\.\d+\.\d+)",
            r"Release Version\s*:\s*CFAST (\d+\.\d+\.\d+)",
            r"CFAST (\d+\.\d+\.\d+)",
        ]

        for pattern in version_patterns:
            match = re.search(pattern, output)
            if match:
                print(match.group(1))
                return match.group(1)

    except (
        subprocess.TimeoutExpired,
        subprocess.CalledProcessError,
        FileNotFoundError,
    ):
        pass
    except Exception:
        pass

    return None


def get_verification_data_dir(base_path: Path, subdir: str) -> Path:
    """
    Get the verification data directory from 'verification_data_local' only.

    Parameters
    ----------
        base_path: Path to the test file (typically Path(__file__).parent)
        subdir: Subdirectory path under verification_data_local.

    Returns
    -------
        Path: The verification data directory to use

    Examples
    --------
    >>> get_verification_data_dir(
    ...     Path("tests"), "DOE_Guidance_Report"
    ... )
    PosixPath('tests/verification_data_local/DOE_Guidance_Report')
    """
    subdir_path = Path(subdir)
    local_verif_dir = base_path / "verification_data_local" / subdir_path
    return local_verif_dir


def compare_model_to_verification_data(
    results: dict, verification_data_dir: Path, prefix: str, tmp_path: Path
) -> None:
    """Compare model results dict of DataFrames to verification CSVs for a given prefix.

    Raises
    ------
        pytest.fail on mismatch or missing files.
    """
    if not verification_data_dir.exists():
        pytest.fail(
            f"Verification data directory does not exist: {verification_data_dir}"
        )

    # Match files: prefix_word.csv or prefix.csv (no additional underscores)
    pattern = rf"^{re.escape(prefix)}(_[a-zA-Z]+\.csv|\.csv)$"
    verif_csv_files = [
        f
        for f in verification_data_dir.iterdir()
        if f.name.endswith(".csv") and re.match(pattern, f.name)
    ]

    if not verif_csv_files:
        pytest.fail(
            f"No verification CSV files found for prefix '{prefix}' in "
            f"{verification_data_dir}. Expected files matching pattern: {pattern}"
        )

    successful_comparisons = 0
    skipped_comparisons = 0

    for verif_csv_file in verif_csv_files:
        suffix = verif_csv_file.name.replace(prefix, "")
        suffix_clean = suffix.replace(".csv", "").replace("_", "")
        model_csv = None
        for key in results.keys():
            if key.endswith(suffix_clean):
                model_csv = results[key]
                break
        assert model_csv is not None, f"Missing model output {suffix_clean}"
        model_df = model_csv

        verif_csv = verification_data_dir / verif_csv_file.name

        read_params = CSV_READ_CONFIGS.get(suffix_clean, {})
        read_args = {k: v for k, v in read_params.items() if v is not None}
        try:
            ref_df = pd.read_csv(verif_csv, **read_args)  # type: ignore[call-overload]
        except pd.errors.EmptyDataError:
            warnings.warn(f"Verification CSV is empty: {verif_csv}", stacklevel=2)
            skipped_comparisons += 1
            continue
        except Exception as e:
            pytest.fail(f"Failed to read verification file {verif_csv}: {e}")

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
            f"No successful verifications performed for prefix '{prefix}'."
            f"Found {len(verif_csv_files)} files but {skipped_comparisons} were skipped"
        )
