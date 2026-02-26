# Script to run periodically to stay synced with verification input files
import argparse
import platform
import re
import shutil
import subprocess
from pathlib import Path


def generate_verification_outputs(local=False, cfast_version=None):
    """
    Generate verification outputs by running CFAST on verification input files.

    Parameters
    ----------
    local : bool, optional
        If True, generate verification data in local directory (verification_data_local).
        If False, generate in standard verification_data directory. Default is False.
    cfast_version : str, optional
        Generate verification data for specific CFAST version (e.g., '7.7.5').
        If provided, creates version-specific output directory. Default is None.

    Raises
    ------
    subprocess.CalledProcessError
        If CFAST execution fails with non-recoverable error.
    """
    verification_dir = Path(".") / "verification_tests" / "Verification"

    if cfast_version:
        verification_data_dir_output = Path(".") / f"verification_data_{cfast_version}"
        print(f"Generating verification data for CFAST version {cfast_version}")
    elif local:
        verification_data_dir_output = (
            Path(".") / "verification_tests" / "verification_data_local"
        )
        print("Generating local verification data")
    else:
        verification_data_dir_output = (
            Path(".") / "verification_tests" / "verification_data"
        )
        print("Generating standard verification data")

    skip_files = {
        "DOE202.in",
        "DOE203.in",
        "DOE204.in",
        "DOE205.in",
        "DOE206.in",
    }  # under ventilated cases that takes too much time to run
    for in_file in verification_dir.rglob("*.in"):
        if in_file.name in skip_files:
            print(f"Skipping {in_file}")
            continue
        print(f"Processing {in_file}")
        rel_path = in_file.relative_to(verification_dir)
        ref_subdir = verification_data_dir_output / rel_path.parent
        ref_subdir.mkdir(parents=True, exist_ok=True)

        ref_in_file = ref_subdir / in_file.name
        shutil.copy(in_file, ref_in_file)

        try:
            result = subprocess.run(
                ["cfast", f"{ref_in_file.stem}.in", "-f"],
                cwd=ref_subdir,
                check=True,
                capture_output=True,
                text=True,
            )
            stderr_output = result.stderr
        except subprocess.CalledProcessError as e:
            print(
                f"Warning: CFAST failed for {in_file.name} with exit code {e.returncode}"
            )
            print("This may be due to platform-specific numerical issues")
            if platform.system() == "Windows" and e.returncode == 3:
                print(
                    f"Skipping {in_file.name} due to known Windows floating-point exception"
                )
                if ref_in_file.exists():
                    ref_in_file.unlink()
                continue
            else:
                raise

        if stderr_output:
            stderr_file = ref_subdir / f"{ref_in_file.stem}.stderr"
            stderr_file.write_text(stderr_output, encoding="utf-8")

        allowed_extensions = {".csv", ".log", ".in", ".stderr"}
        for file_path in ref_subdir.iterdir():
            if (
                file_path.is_file()
                and file_path.suffix.lower() not in allowed_extensions
            ):
                print(f"Removing {file_path.name}")
                file_path.unlink()

    failed_cases = _verify_outputs(verification_data_dir_output)
    if failed_cases:
        print(f"\nERROR: {len(failed_cases)} verification case(s) failed:")
        for case in failed_cases:
            print(f"  - {case}")
        raise RuntimeError(
            f"{len(failed_cases)} verification case(s) did not complete successfully. "
            "Check log files for details."
        )
    else:
        print("\nAll verification cases completed successfully.")


def _verify_outputs(output_dir: Path) -> list[str]:
    """Verify that all CFAST runs completed successfully.

    Performs three checks per input file:

    1. **Stderr check** - detects runtime signals (e.g. SIGFPE) that CFAST
       may survive but that corrupt the results.
    2. **Zone CSV existence** - ensures the ``_zone.csv`` file was produced
       and contains data rows (not just headers).
    3. **Simulation completeness** - reads the expected simulation duration
       from the ``.in`` file and compares it to the last time value in the
       ``_zone.csv``.  A tolerance of 10 % is applied.

    Parameters
    ----------
    output_dir : Path
        Directory containing CFAST output files.

    Returns
    -------
    list[str]
        List of input file relative paths whose outputs failed validation.
    """
    failed: list[str] = []
    for in_file in sorted(output_dir.rglob("*.in")):
        rel = str(in_file.relative_to(output_dir))
        reasons: list[str] = []

        # --- 1. Check stderr for runtime signals ---
        stderr_file = in_file.with_suffix(".stderr")
        if stderr_file.exists():
            stderr_content = stderr_file.read_text(encoding="utf-8", errors="replace")
            if re.search(
                r"SIGFPE|SIGSEGV|SIGABRT|Backtrace for this error",
                stderr_content,
            ):
                reasons.append(
                    f"runtime signal detected in stderr: "
                    f"{stderr_content.splitlines()[0]}"
                )

        # --- 2. Check _zone.csv exists and has data ---
        zone_csv = in_file.with_name(f"{in_file.stem}_zone.csv")
        if not zone_csv.exists():
            reasons.append("missing _zone.csv output file")
        else:
            zone_lines = zone_csv.read_text(
                encoding="utf-8", errors="replace"
            ).splitlines()
            # First two lines are units and header, data starts at line 3
            if len(zone_lines) <= 2:
                reasons.append("_zone.csv has no data rows")
            else:
                # --- 3. Check simulation reached expected end time ---
                expected_time = _parse_simulation_time(in_file)
                if expected_time is not None:
                    last_line = zone_lines[-1].strip()
                    try:
                        last_time = float(last_line.split(",")[0])
                        if last_time < expected_time * 0.9:
                            reasons.append(
                                f"simulation ended early: last time "
                                f"{last_time:.1f}s vs expected "
                                f"{expected_time:.1f}s"
                            )
                    except (ValueError, IndexError):
                        reasons.append("could not parse last time value from _zone.csv")

        if reasons:
            for reason in reasons:
                print(f"WARNING [{in_file.name}]: {reason}")
            failed.append(rel)

    return failed


def _parse_simulation_time(in_file: Path) -> float | None:
    """Extract the SIMULATION time from a CFAST input file.

    Looks for the ``&TIME SIMULATION = <value>`` pattern in the
    Fortran namelist-style input.

    Parameters
    ----------
    in_file : Path
        Path to a CFAST ``.in`` file.

    Returns
    -------
    float or None
        The simulation end time in seconds, or ``None`` if it
        could not be parsed.
    """
    content = in_file.read_text(encoding="utf-8", errors="replace")
    match = re.search(r"SIMULATION\s*=\s*([\d.]+)", content)
    if match:
        return float(match.group(1))
    return None


def main():
    """Run the verification data generation script with command line arguments."""
    parser = argparse.ArgumentParser(
        description="Generate verification data for CFAST tests"
    )
    parser.add_argument(
        "--local",
        action="store_true",
        help="Generate verification data in local directory (verification_data_local)",
    )
    parser.add_argument(
        "--version",
        help="Generate verification data for specific CFAST version (e.g., 7.7.5)",
    )

    args = parser.parse_args()

    cfast_version = args.version
    generate_verification_outputs(local=args.local, cfast_version=cfast_version)

    if cfast_version:
        data_type = f"version-specific ({cfast_version})"
    else:
        data_type = "local" if args.local else "standard"
    print(f"Verification data generation complete ({data_type}).")


if __name__ == "__main__":
    main()
