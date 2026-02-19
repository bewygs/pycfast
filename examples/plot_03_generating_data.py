"""
===============================
03 Generating Data with PyCFAST
===============================

This example demonstrates how to use PyCFAST with NumPy to generate simulation data by running multiple CFAST fire simulations with varying parameters.

We'll create a simple parametric study by varying fire characteristics and analyze the trends in the results.
"""

# %%
# Step 1: Import Libraries
# -------------------------
# We'll import:
#
# - **NumPy**: For generating parameter ranges and arrays
# - **Pandas**: For organizing and analyzing simulation results
# - **Matplotlib**: For visualizing the generated data
# - **PyCFAST**: For parsing and running CFAST models (see :func:`~pycfast.parsers.parse_cfast_file` and :meth:`~pycfast.CFASTModel.run`)

import os

import matplotlib.pyplot as plt
import numpy as np

from pycfast.parsers import parse_cfast_file

# %%
# Step 2: Load Base Model
# -----------------------
# We start with an existing CFAST model as our template. We'll use
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

n_samples = 10

heat_of_combustion_values = np.linspace(15, 5000, n_samples)  # MJ/kg
radiative_fraction_values = np.linspace(0.1, 0.9, n_samples)  # Fraction

parameter_combinations = list(
    zip(heat_of_combustion_values, radiative_fraction_values, strict=False)
)

print(f"Generated {len(parameter_combinations)} parameter combinations")
print(
    f"Heat of combustion range: {heat_of_combustion_values[0]:.2f} - {heat_of_combustion_values[-1]:.2f} MJ/kg"
)
print(
    f"Radiative fraction range: {radiative_fraction_values[0]:.2f} - {radiative_fraction_values[-1]:.2f}"
)

# %%
# Step 4: Run Parametric Study
# ----------------------------
# Now we'll systematically modify the model parameters and run simulations
# to generate our dataset.
#
# This creates a structured dataset linking input parameters to simulation outputs.

all_runs = []

for i, (hoc, rf) in enumerate(parameter_combinations):
    print(
        f"Running simulation {i + 1}/{len(parameter_combinations)}: hoc={hoc}, rf={rf}"
    )

    # Update fire parameters using :meth:`~pycfast.CFASTModel.update_fire_params`
    temp_model = model.update_fire_params(
        fire="Hawaii_03_Fire", heat_of_combustion=hoc, radiative_fraction=rf
    )

    # Run the simulation with :meth:`~pycfast.CFASTModel.run` and save the output
    outputs = temp_model.run(file_name=f"data_gen_sim_{i:03d}.in")
    all_runs.append(
        {
            "simulation_id": i,
            "hoc": hoc,  # heat of combustion
            "rf": rf,  # radiative fraction
            "outputs": outputs,
        }
    )

# %%
# Step 5: Analyze Generated Data
# -------------------------------
# Now we visualize our generated dataset to understand how the parameter
# variations affect fire behavior.
#
# Each line represents a different combination of heat of combustion and
# radiative fraction values.

plt.figure(figsize=(12, 7))
colors = plt.get_cmap("viridis")(np.linspace(0, 1, len(all_runs)))

for idx, run in enumerate(all_runs):
    upper_layer = run["outputs"]["compartments"]["ULT_1"]
    time = run["outputs"]["compartments"]["Time"]
    plt.plot(
        time,
        upper_layer,
        label=(f"$H_c$={run['hoc']:.0f} MJ/kg, $f_{{rad}}$={run['rf']:.2f}"),
        linewidth=2,
        alpha=0.85,
        color=colors[idx],
    )

plt.xlabel("Time (s)", fontsize=16, fontweight="bold")
plt.ylabel("Upper Layer Temperature (°C)", fontsize=16, fontweight="bold")
plt.title(
    "Upper Layer Temperature for Different Fire Parameters",
    fontsize=18,
    fontweight="bold",
)
plt.legend(
    loc="upper left",
    fontsize=12,
    frameon=False,
    ncol=2,
    title="Simulations",
    title_fontsize=14,
)
plt.grid(True, which="both", linestyle="--", linewidth=0.7, alpha=0.5)
plt.minorticks_on()
plt.tick_params(axis="both", which="major", labelsize=14, length=7, width=2)
plt.tick_params(axis="both", which="minor", labelsize=12, length=4, width=1)
plt.tight_layout()
plt.show()

# %%
# Cleanup
# -------
# CFAST generates multiple output files during each simulation run.

files_removed = 0
for fname in os.listdir("."):
    if fname.startswith("data_gen_sim_"):
        try:
            os.remove(fname)
            files_removed += 1
        except Exception as e:
            print(f"Could not remove {fname}: {e}")

print(f"Cleanup complete. Removed {files_removed} simulation files.")
