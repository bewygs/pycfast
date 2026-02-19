from __future__ import annotations

import glob
import os
from pathlib import Path

import pytest

from pycfast.parsers import parse_cfast_file

from .verification import (
    compare_model_to_verification_data,
    get_verification_data_dir,
)


def get_all_verification_input_files():
    """Get all .in files from the verification test directories."""
    verification_dir = Path(__file__).parent / "Verification"
    return glob.glob(str(verification_dir / "**" / "*.in"), recursive=True)


def get_test_parameters():
    """Generate test parameters for all verification input files."""
    input_files = get_all_verification_input_files()
    test_params = []

    for input_file in input_files:
        file_path = Path(input_file)
        parent_dir = file_path.parent.name
        file_prefix = file_path.stem

        # Handle NRC_Users_Guide subdirectories
        if "NRC_Users_Guide" in file_path.parts:
            # Find the NRC_Users_Guide index and build the subdirectory path
            nrc_idx = file_path.parts.index("NRC_Users_Guide")
            # parent_dir should be NRC_Users_Guide/<subdir>
            parent_dir = os.path.join("NRC_Users_Guide", file_path.parts[nrc_idx + 1])

        test_params.append((input_file, parent_dir, file_prefix))

    return test_params


@pytest.mark.parametrize("input_file,parent_dir,file_prefix", get_test_parameters())
def test_parser_verification(input_file, parent_dir, file_prefix, tmp_path):
    """
    Test parser on verification input files.

    This test:
    1. Parses the input file using parse_cfast_file()
    2. Runs the parsed model
    3. Compares results to verification data

    Args:
        input_file: Path to the .in file to test
        parent_dir: Parent directory name (e.g., 'Radiation', 'DOE_Guidance_Report')
        file_prefix: File name without extension (e.g., 'radiation_1', 'DOE201')
        tmp_path: Pytest temporary directory fixture
    """
    # Get verification data directory
    verification_data_dir = get_verification_data_dir(Path(__file__).parent, parent_dir)

    skip_files = {
        "DOE202",
        "DOE203",
        "DOE204",
        "DOE205",
        "DOE206",
    }  # under ventilated cases that takes too much time to run

    if file_prefix in skip_files:
        pytest.skip(f"Skipping slow test for {input_file}")

    # Parse the input file
    try:
        model = parse_cfast_file(input_file)
    except Exception as e:
        pytest.fail(f"Failed to parse {input_file}: {e}")

    # Set up model for execution
    model.file_name = str(tmp_path / f"{file_prefix}.in")
    model.cfast_exe = "cfast"
    model.extra_arguments = ["-f"]

    # Run the model
    try:
        results = model.run()
        assert isinstance(results, dict), f"Expected dict results, got {type(results)}"
    except Exception as e:
        pytest.fail(f"Failed to run model for {input_file}: {e}")

    # Compare to verification data
    try:
        compare_model_to_verification_data(
            results, verification_data_dir, prefix=file_prefix, tmp_path=tmp_path
        )
    except Exception as e:
        pytest.fail(f"Verification comparison failed for {input_file}: {e}")


def test_parser_verification_file_discovery():
    """Test that we can discover verification input files."""
    input_files = get_all_verification_input_files()
    assert len(input_files) > 0, "No verification input files found"

    # Verify we found files from expected directories
    expected_dirs = {
        "DOE_Guidance_Report",
        "Energy_Balance",
        "Fires",
        "Mass_Balance",
        "NRC_Users_Guide" + os.sep + "A_Cabinet_Fire_in_MCR",
        "NRC_Users_Guide" + os.sep + "B_Cabinet_Fire_in_Switchgear",
        "NRC_Users_Guide" + os.sep + "D_MCC_Fire_in_Switchgear",
        "NRC_Users_Guide" + os.sep + "E_Trash_Fire_in_Cable_Spreading_Room",
        "NRC_Users_Guide" + os.sep + "G_Transient_Fire_in_Corridor",
        "Radiation",
        "Species",
        "Sprinkler",
        "Target",
        "Thermal_Equilibrium",
        "Ventilation",
    }

    verification_dir = Path(__file__).parent / "Verification"
    found_dirs = set()
    for file_path in input_files:
        parent_path = Path(file_path).parent
        rel_path = os.path.relpath(parent_path, verification_dir)
        found_dirs.add(rel_path)

    missing_dirs = expected_dirs - found_dirs
    if missing_dirs:
        pytest.fail(f"Missing verification directories: {missing_dirs}")


def test_parser_verification_sample():
    """Test parser on a sample verification file to ensure basic functionality."""
    # Use a simple radiation test as a sample
    verification_dir = Path(__file__).parent / "Verification" / "Radiation"
    sample_file = verification_dir / "radiation_1.in"

    if not sample_file.exists():
        pytest.skip("Sample verification file not found")

    # Test parsing without running the full verification
    try:
        model = parse_cfast_file(str(sample_file))
        assert model is not None, "Parser returned None"
        assert hasattr(model, "simulation_environment"), (
            "Missing simulation_environment"
        )
        assert hasattr(model, "compartments"), "Missing compartments"
    except Exception as e:
        pytest.fail(f"Failed to parse sample file {sample_file}: {e}")
