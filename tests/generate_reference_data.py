# Script to run periodically to stay synced with verification/validation input files
import argparse
import platform
import shutil
import subprocess
from pathlib import Path

TESTS_DIR = Path(__file__).parent

SUITES = {
    "verification": {
        "input_dir": TESTS_DIR / "verification_tests" / "Verification",
        "output_dir": TESTS_DIR / "verification_tests" / "verification_data_local",
    },
    "validation": {
        "input_dir": TESTS_DIR / "validation_tests" / "Validation",
        "output_dir": TESTS_DIR / "validation_tests" / "validation_data_local",
    },
}


def generate_outputs(suite_name: str) -> None:
    """
    Generate reference outputs by running CFAST on all .in files for a suite.

    Parameters
    ----------
    suite_name : str
        Either 'verification' or 'validation'.

    Raises
    ------
    subprocess.CalledProcessError
        If CFAST execution fails with non-recoverable error.
    """
    suite = SUITES[suite_name]
    input_dir: Path = suite["input_dir"]
    output_dir: Path = suite["output_dir"]

    print(f"Generating {suite_name} data: {input_dir} -> {output_dir}")

    for in_file in input_dir.rglob("*.in"):
        print(f"  Processing {in_file.relative_to(input_dir)}")
        rel_path = in_file.relative_to(input_dir)
        ref_subdir = output_dir / rel_path.parent
        ref_subdir.mkdir(parents=True, exist_ok=True)

        ref_in_file = ref_subdir / in_file.name
        shutil.copy(in_file, ref_in_file)

        try:
            subprocess.run(
                ["cfast", f"{ref_in_file.stem}.in", "-f"], cwd=ref_subdir, check=True
            )
        except subprocess.CalledProcessError as e:
            print(
                f"  Warning: CFAST failed for {in_file.name} with exit code {e.returncode}"
            )
            if platform.system() == "Windows" and e.returncode == 3:
                print(f"  Skipping {in_file.name} (Windows floating-point exception)")
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
                file_path.unlink()

    print(f"Done ({suite_name}).")


def main():
    """Run the data generation script with command line arguments."""
    parser = argparse.ArgumentParser(
        description="Generate reference CSV data for CFAST tests"
    )
    parser.add_argument(
        "--suite",
        choices=["verification", "validation", "all"],
        default="all",
        help="Which suite to generate data for (default: all)",
    )

    args = parser.parse_args()

    suites = list(SUITES.keys()) if args.suite == "all" else [args.suite]
    for suite_name in suites:
        generate_outputs(suite_name)


if __name__ == "__main__":
    main()
