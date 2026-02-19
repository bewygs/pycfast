"""
=================================
07 Parallel Computing on clusters
=================================

This notebook demonstrates how to use parallel computing on a cluster to accelerate CFAST fire simulations using PyCFAST and Dask.

Locally you would normally use multiprocessing or joblib library to run simulations in parallel on multiple CPU cores. However, for larger
parameter studies or optimization tasks, you may want to scale up to an HPC cluster or cloud environment.

We'll compare sequential (single-core) vs parallel execution using :func:`~pycfast.parsers.parse_cfast_file`, :meth:`~pycfast.CFASTModel.update_fire_params`, and :meth:`~pycfast.CFASTModel.run` and show how to set up distributed computing for CFAST simulations.
"""

# %%
# Import Libraries
# -----------------
# We'll need the following libraries:
#
# - **dask.distributed**: For parallel computing
# - **NumPy**: Numerical operations

import os
import shutil
import time
import uuid
from pathlib import Path

import numpy as np
from dask.distributed import Client, LocalCluster, get_worker

from pycfast.parsers import parse_cfast_file

# %%
# Step 1: Setting Up the Dask Client
# ------------------------------------
# Dask provides a flexible framework for parallel computing. It can be used
# with a variety of cluster managers, including local clusters, HPC schedulers
# (like SLURM), and cloud services.
#
# Here we create a local cluster that will use 4 CPU cores on your machine.
#
# **Cluster Configuration:**
#
# - **n_workers**: Number of worker processes (typically = number of CPU cores)
# - **threads_per_worker**: Threads per worker (1 for CPU-bound tasks like CFAST)
# - **memory_limit**: Memory limit per worker to prevent system overload

cluster = LocalCluster(
    n_workers=4,  # Use 4 workers (adjust based on your CPU cores)
    threads_per_worker=1,  # 1 thread per worker for CPU-bound CFAST simulations
    memory_limit="256MB",  # Memory limit per worker
)
client = Client(cluster)

print(f"Dask dashboard available at: {client.dashboard_link}")
print(f"Number of workers: {len(client.scheduler_info()['workers'])}")
client

# %%
# Step 2: Load Base Model
# -----------------------
# We start with an existing CFAST model as our template. We'll use
# :func:`~pycfast.parsers.parse_cfast_file` to load the
# `USN_Hawaii_Test_03.in <data/USN_Hawaii_Test_03.in>`_. This model serves
# as the foundation that we'll modify systematically to generate our dataset.

model = parse_cfast_file("data/USN_Hawaii_Test_03.in")

# %%
# The parsed model is displayed below.

model

# %%
# Step 3: Generate Parameter Combinations
# ----------------------------------------
# We use NumPy to create systematic parameter variations. For this study,
# we'll vary two key fire parameters:
#
# - **Heat of combustion**: Energy released per unit mass of fuel (affects fire intensity)
# - **Radiative fraction**: Portion of fire energy released as radiation (affects heat transfer)
#
# For demonstration, we'll use a smaller sample size. In practice, you might
# use hundreds or thousands of combinations.

n_samples = 100  # Number of parameter combinations

heat_of_combustion_values = np.linspace(15000, 25000, n_samples)  # kJ/kg
radiative_fraction_values = np.linspace(0.2, 0.4, n_samples)  # Fraction

parameter_combinations = list(
    zip(heat_of_combustion_values, radiative_fraction_values, strict=False)
)

print(f"Generated {len(parameter_combinations)} parameter combinations")
print(
    f"Heat of combustion range: {heat_of_combustion_values[0]:.0f} - {heat_of_combustion_values[-1]:.0f} kJ/kg"
)
print(
    f"Radiative fraction range: {radiative_fraction_values[0]:.2f} - {radiative_fraction_values[-1]:.2f}"
)

# %%
# Step 4: Sequential Execution (Single Core)
# --------------------------------------------
# First, let's run simulations sequentially using a traditional for loop.
# This will serve as our baseline for performance comparison.
#
# **Sequential approach characteristics:**
#
# - Uses only one CPU core
# - Simulations run one after another
# - Simple but slower for multiple runs


def run_sequential(heat_of_combustion, radiative_fraction, file_name=None):
    temp_model = model.update_fire_params(
        fire="Hawaii_03_Fire",
        heat_of_combustion=heat_of_combustion,
        radiative_fraction=radiative_fraction,
    )

    results = temp_model.run(file_name=file_name)

    return results


# %%
# Sequential execution with timing.

start_time = time.perf_counter()
all_runs_sequential = []

print("Running simulations sequentially")
for i, (hoc, rf) in enumerate(parameter_combinations):
    if i % 5 == 0:  # Progress indicator
        print(f"Running simulation {i + 1}/{len(parameter_combinations)}")

    outputs = run_sequential(heat_of_combustion=hoc, radiative_fraction=rf)
    all_runs_sequential.append(
        {
            "simulation_id": i,
            "hoc": hoc,  # heat of combustion
            "rf": rf,  # radiative fraction
            "outputs": outputs,
        }
    )

sequential_time = time.perf_counter() - start_time
print(f"\nSequential execution completed in {sequential_time:.2f} seconds")
print(
    f"Average time per simulation: {sequential_time / len(parameter_combinations):.2f} seconds"
)

# %%
# Clean up generated files from sequential run
files_removed = 0
for fname in os.listdir("."):
    if fname.startswith("USN_Hawaii_Test_03_"):
        try:
            os.remove(fname)
            files_removed += 1
        except Exception as e:
            print(f"Could not remove {fname}: {e}")

print(f"Cleanup complete. Removed {files_removed} sequential simulation files.")

# %%
# Step 5: Parallel Execution with Dask
# --------------------------------------
# Now let's implement the same simulations using parallel execution. This
# approach distributes work across multiple CPU cores.
#
# **Parallel approach characteristics:**
#
# - Uses multiple CPU cores simultaneously
# - Each worker runs in isolated temporary directories
# - Requires careful handling of file I/O to avoid conflicts


def _run_one(hoc, rf, sim_idx: int):
    w = get_worker()

    # Create a unique temporary directory assigned to this worker
    # This ensures no file conflicts between parallel tasks
    rundir = Path(w.local_directory) / f"cfast-{uuid.uuid4().hex}"
    rundir.mkdir(parents=True, exist_ok=True)

    try:
        in_name = rundir / f"parallel_sim_{sim_idx:03d}.in"

        # Run simulation in the temporary directory
        outputs = run_sequential(
            heat_of_combustion=hoc, radiative_fraction=rf, file_name=str(in_name)
        )

        return {
            "simulation_id": sim_idx,
            "hoc": hoc,
            "rf": rf,
            "outputs": outputs,
        }
    finally:
        shutil.rmtree(rundir, ignore_errors=True)


def run_all_parallel(parameter_combinations, client: Client):
    futures = [
        client.submit(_run_one, hoc, rf, i, pure=False)
        for i, (hoc, rf) in enumerate(parameter_combinations)
    ]

    results = client.gather(futures)
    return results


# %%
# While the simulation is running you can monitor the Dask dashboard at
# ``http://localhost:8787/status`` to see real-time progress and resource usage.

print("Running simulations in parallel...")
start_time = time.perf_counter()

all_runs_parallel = run_all_parallel(parameter_combinations, client)

parallel_time = time.perf_counter() - start_time
print(f"\nParallel execution completed in {parallel_time:.2f} seconds")
print(
    f"Average time per simulation: {parallel_time / len(parameter_combinations):.2f} seconds"
)

# %%
# Step 6: Speed Comparison
# -------------------------
# Note: For small workloads, parallel overhead may exceed benefits.

print(f"Number of simulations: {len(parameter_combinations)}")
print(f"Number of workers: {len(client.scheduler_info()['workers'])}")
print(f"Sequential execution time: {sequential_time:.2f} seconds")
print(f"Parallel execution time:   {parallel_time:.2f} seconds")
speedup = sequential_time / parallel_time
efficiency = speedup / len(client.scheduler_info()["workers"]) * 100
print(f"\nSpeedup factor: {speedup:.2f}x")
print(f"Parallel efficiency: {efficiency:.1f}%")

time_saved = sequential_time - parallel_time
print(
    f"Time saved: {time_saved:.2f} seconds ({time_saved / sequential_time * 100:.1f}%)"
)

print("Results verification:")
print(f"Sequential results: {len(all_runs_sequential)} simulations")
print(f"Parallel results: {len(all_runs_parallel)} simulations")
print(f"Results match: {len(all_runs_sequential) == len(all_runs_parallel)}")

# %%
# Cleanup
# -------

client.close()
cluster.close()
print("Dask cluster closed successfully")
