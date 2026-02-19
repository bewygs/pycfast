"""
Configuration for reading CFAST CSV output files.

This module defines the standard parameters for reading different types of
CFAST CSV output files, ensuring consistency between model execution and
testing/verification.
"""

# Configuration for each CSV file type with their specific reading parameters
CSV_READ_CONFIGS: dict[str, dict[str, int | list | None]] = {
    "compartments": {"header": 0, "skiprows": [1, 2, 3]},
    "devices": {"header": 0, "skiprows": [1, 2, 3]},
    "masses": {"header": 0, "skiprows": [1, 2, 3]},
    "vents": {"header": 0, "skiprows": [1, 2, 3]},
    "walls": {"header": 0, "skiprows": [1, 2, 3]},
    "zone": {"header": 1, "skiprows": None},
    "diagnostics": {"header": 1, "skiprows": [1, 2, 3]},
}
