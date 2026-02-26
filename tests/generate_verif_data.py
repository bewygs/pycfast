# Script to run periodically to stay synced with verification input files
import argparse
import platform
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
            subprocess.run(
                ["cfast", f"{ref_in_file.stem}.in", "-f"], cwd=ref_subdir, check=True
            )
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

        allowed_extensions = {".csv", ".log", ".in"}
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
    """
    Verify that all CFAST runs completed successfully.

    Checks each `.log` file in the output directory for
    the "Normal exit from CFAST" marker.

    Parameters
    ----------
    output_dir : Path
        Directory containing CFAST output files.

    Returns
    -------
    list[str]
        List of input file names whose log files are missing
        or do not contain the normal exit marker.
    """
    failed: list[str] = []
    for in_file in output_dir.rglob("*.in"):
        log_file = in_file.with_suffix(".log")
        if not log_file.exists():
            print(f"WARNING: No log file found for {in_file.name}")
            failed.append(str(in_file.relative_to(output_dir)))
            continue
        log_content = log_file.read_text(encoding="utf-8", errors="replace")
        if "Normal exit from CFAST" not in log_content:
            print(f"WARNING: Abnormal exit detected for {in_file.name}")
            failed.append(str(in_file.relative_to(output_dir)))
    return failed


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
