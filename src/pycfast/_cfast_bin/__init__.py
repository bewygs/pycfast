"""Internal module for the compiled CFAST binary path.

This module exposes the path to the CFAST binary/executable that was compiled
during the wheel build process. The binary is placed in ``src/pycfast/_cfast_bin/``
by the CI pipeline before building the platform-specific wheel.
"""

from __future__ import annotations

import platform
from pathlib import Path

_BIN_DIR = Path(__file__).parent


def get_cfast_executable() -> str | None:
    """Return the absolute path to the bundled CFAST binary, if available.

    Returns
    -------
    str or None
        Absolute path to the bundled CFAST binary/executable, or ``None`` if
        no binary was bundled for this platform.
    """
    name = "cfast.exe" if platform.system() == "Windows" else "cfast"
    exe = _BIN_DIR / name
    if exe.is_file():
        return str(exe)
    return None
