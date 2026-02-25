"""Download CFAST source code and compile the binary for the current platform.

This script is intended to be run in CI before building the wheel,
or locally for development. It clones the CFAST repository at a specific
version tag and compiles the executable using the official NIST build scripts.

Usage
-----
Run from the repository root::

    python scripts/build_cfast.py                           # defaults
    python scripts/build_cfast.py --version 7.7.5           # explicit version
    python scripts/build_cfast.py --compiler intel           # Intel compiler

The compiled binary is placed in ``src/pycfast/_cfast_bin/``.
"""

from __future__ import annotations

import argparse
import platform
import shutil
import stat
import subprocess
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DEST_DIR = REPO_ROOT / "src" / "pycfast" / "_cfast_bin"

# Platform-specific build configuration.
BUILD_CONFIGS: dict[tuple[str, str], dict[str, str]] = {
    ("Linux", "gcc"): {
        "build_dir": "gnu_linux_64",
        "build_script": "make_cfast.sh",
        "binary_name": "cfast7_linux_64",
        "dest_name": "cfast",
    },
    ("Windows", "gcc"): {
        "build_dir": "gnu_win_64",
        "build_script": "make_cfast.bat",
        "binary_name": "cfast7_win_64.exe",
        "dest_name": "cfast.exe",
    },
    ("Darwin", "gcc"): {
        "build_dir": "gnu_linux_64",
        "build_script": "make_cfast.sh",
        "binary_name": "cfast7_linux_64",
        "dest_name": "cfast",
    },
}


def _get_build_config(compiler: str) -> dict[str, str]:
    """Return the build configuration for the current platform and compiler.

    Parameters
    ----------
    compiler : str
        Fortran compiler family (``"gcc"`` or ``"intel"``).

    Returns
    -------
    dict[str, str]
        Build configuration with keys ``build_dir``, ``build_script``,
        ``binary_name``, and ``dest_name``.

    Raises
    ------
    RuntimeError
        If the current platform/compiler combination is not supported.
    """
    system = platform.system()
    key = (system, compiler)
    if key not in BUILD_CONFIGS:
        supported = [f"{s}/{c}" for s, c in BUILD_CONFIGS]
        msg = (
            f"Unsupported platform/compiler: {system}/{compiler}. "
            f"Supported: {', '.join(supported)}"
        )
        raise RuntimeError(msg)
    return BUILD_CONFIGS[key]


def _clone_cfast(version: str, dest: Path) -> Path:
    """Shallow-clone the CFAST repository at a specific version tag.

    Parameters
    ----------
    version : str
        CFAST version (e.g. ``"7.7.5"``).
    dest : Path
        Directory to clone into.

    Returns
    -------
    Path
        Path to the cloned repository root.
    """
    # CFAST tag is not consistent across versions, and only version 7.7.5 is running correctly on linux
    tag_mapping = {
        "7.7.5": "CFAST-7.7.5",
    }

    tag = tag_mapping.get(version, f"CFAST-{version}")
    print(f"Cloning CFAST {version} (tag: {tag}) ...")
    subprocess.run(
        [
            "git",
            "clone",
            "--depth",
            "1",
            "--branch",
            tag,
            "https://github.com/firemodels/cfast.git",
            str(dest),
        ],
        check=True,
    )
    return dest


def _compile_cfast(cfast_root: Path, config: dict[str, str]) -> Path:
    """Compile CFAST using the official NIST build script.

    Parameters
    ----------
    cfast_root : Path
        Root of the cloned CFAST repository.
    config : dict[str, str]
        Build configuration from :func:`_get_build_config`.

    Returns
    -------
    Path
        Path to the compiled CFAST executable.

    Raises
    ------
    FileNotFoundError
        If the build directory or compiled binary cannot be found.
    subprocess.CalledProcessError
        If compilation fails.
    """
    build_dir = cfast_root / "Build" / "CFAST" / config["build_dir"]
    script = config["build_script"]
    binary_name = config["binary_name"]

    if not build_dir.is_dir():
        msg = f"Build directory not found: {build_dir}"
        raise FileNotFoundError(msg)

    print(f"Compiling CFAST in {build_dir} ...")

    system = platform.system()
    if system in ("Linux", "Darwin"):
        script_path = build_dir / script
        script_path.chmod(script_path.stat().st_mode | stat.S_IEXEC)
        subprocess.run(
            ["bash", str(script_path)],
            cwd=str(build_dir),
            check=True,
        )
    elif system == "Windows":
        subprocess.run(
            ["cmd", "/c", "call", script],
            cwd=str(build_dir),
            check=True,
        )

    binary = build_dir / binary_name
    if not binary.is_file():
        msg = f"Compiled binary '{binary_name}' not found in {build_dir}"
        raise FileNotFoundError(msg)

    print(f"Compilation successful: {binary}")
    return binary


def build_cfast(version: str = "7.7.5", compiler: str = "gcc") -> Path:
    """Download, compile, and install the CFAST binary.

    The binary is placed in ``src/pycfast/_cfast_bin/``.

    Parameters
    ----------
    version : str
        CFAST version to build (e.g. ``"7.7.5"``).
    compiler : str
        Fortran compiler family (``"gcc"`` or ``"intel"``).

    Returns
    -------
    Path
        Path to the installed binary.
    """
    config = _get_build_config(compiler)
    DEST_DIR.mkdir(parents=True, exist_ok=True)

    dest = DEST_DIR / config["dest_name"]

    with tempfile.TemporaryDirectory() as tmpdir:
        cfast_root = _clone_cfast(version, Path(tmpdir) / f"cfast-{version}")
        binary = _compile_cfast(cfast_root, config)

        shutil.copy2(binary, dest)

        if platform.system() != "Windows":
            dest.chmod(dest.stat().st_mode | stat.S_IEXEC)

    size_mb = dest.stat().st_size / (1024 * 1024)
    print(f"CFAST {version} installed to {dest} ({size_mb:.1f} MB)")
    return dest


def main() -> None:
    """CLI entry point for building the CFAST binary."""
    parser = argparse.ArgumentParser(
        description="Build CFAST binary for the current platform.",
    )
    parser.add_argument(
        "--version",
        default="7.7.5",
        help="CFAST version tag to build (default: %(default)s)",
    )
    parser.add_argument(
        "--compiler",
        default="gcc",
        choices=["gcc", "intel"],
        help="Fortran compiler family (default: %(default)s)",
    )
    args = parser.parse_args()

    build_cfast(version=args.version, compiler=args.compiler)


if __name__ == "__main__":
    main()
