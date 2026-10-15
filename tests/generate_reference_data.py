# Script to run periodically to stay synced with verification/validation input files
import argparse
import os
import platform
import shutil
import subprocess
from concurrent.futures import ThreadPoolExecutor
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


def run_case(in_file: Path, input_dir: Path, output_dir: Path) -> None:
    """
    Copy one input file to the output tree and run CFAST on it.

    Parameters
    ----------
    in_file : Path
        Input file to run.
    input_dir : Path
        Root of the suite input files.
    output_dir : Path
        Root of the suite reference outputs.

    Raises
    ------
    subprocess.CalledProcessError
        If CFAST execution fails with non-recoverable error.
    """
    print(f"  Processing {in_file.relative_to(input_dir)}")
    rel_path = in_file.relative_to(input_dir)
    ref_subdir = output_dir / rel_path.parent
    ref_subdir.mkdir(parents=True, exist_ok=True)

    ref_in_file = ref_subdir / in_file.name
    shutil.copy(in_file, ref_in_file)

    # the output is captured so that parallel runs do not mix their logs
    try:
        subprocess.run(
            ["cfast", f"{ref_in_file.stem}.in", "-f"],
            cwd=ref_subdir,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )
    except subprocess.CalledProcessError as e:
        print(
            f"  Warning: CFAST failed for {in_file.name} with exit code {e.returncode}\n"
            f"{e.output}"
        )
        if platform.system() == "Windows" and e.returncode == 3:
            print(f"  Skipping {in_file.name} (Windows floating-point exception)")
            if ref_in_file.exists():
                ref_in_file.unlink()
        else:
            raise


def generate_outputs(suite_name: str, jobs: int) -> None:
    """
    Generate reference outputs by running CFAST on all .in files for a suite.

    Parameters
    ----------
    suite_name : str
        Either 'verification' or 'validation'.
    jobs : int
        Number of CFAST runs in parallel.

    Raises
    ------
    subprocess.CalledProcessError
        If CFAST execution fails with non-recoverable error.
    """
    suite = SUITES[suite_name]
    input_dir: Path = suite["input_dir"]
    output_dir: Path = suite["output_dir"]

    print(f"Generating {suite_name} data: {input_dir} -> {output_dir}")

    with ThreadPoolExecutor(max_workers=jobs) as executor:
        futures = [
            executor.submit(run_case, in_file, input_dir, output_dir)
            for in_file in input_dir.rglob("*.in")
        ]
        for future in futures:
            future.result()

    # cleaned once all runs are done: several cases share a folder and a
    # running case still needs its own .out, .smv, .status... files
    allowed_extensions = {".csv", ".log", ".in"}
    for file_path in output_dir.rglob("*"):
        if file_path.is_file() and file_path.suffix.lower() not in allowed_extensions:
            file_path.unlink()

    print(f"Done ({suite_name}).")


def parse_jobs(value: str) -> int:
    """Read the --jobs argument: a positive number, or 'auto' for one per CPU."""
    if value == "auto":
        return os.cpu_count() or 1
    if not value.isdigit() or int(value) < 1:
        raise argparse.ArgumentTypeError(
            f"must be 'auto' or a positive number, got {value}"
        )
    return int(value)


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
    parser.add_argument(
        "--jobs",
        type=parse_jobs,
        default=1,
        help="Number of CFAST runs in parallel, or 'auto' for one per CPU (default: 1)",
    )

    args = parser.parse_args()

    suites = list(SUITES.keys()) if args.suite == "all" else [args.suite]
    for suite_name in suites:
        generate_outputs(suite_name, args.jobs)


if __name__ == "__main__":
    main()
