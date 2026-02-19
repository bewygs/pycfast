"""
=======================
04 Sensitivity Analysis
=======================

This example demonstrates how to perform sensitivity analysis on CFAST fire simulation
models using the SALib library. We'll use Sobol indices to quantify parameter importance
and visualize the results.
"""

# %%
# Step 1: Import Required Libraries
# ----------------------------------

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.ticker import FormatStrFormatter
from SALib.analyze import sobol as sobol_analyze
from SALib.sample import sobol as sobol_sample

from pycfast.parsers import parse_cfast_file

# %%
# Step 2: Load Base Model
# -----------------------
# For this example, we'll use a predefined CFAST input file as our base model.
# You can replace this with your own model file. We'll use
# :func:`~pycfast.parsers.parse_cfast_file` to load the
# `USN_Hawaii_Test_03.in <data/USN_Hawaii_Test_03.in>`_ input file.

model = parse_cfast_file("data/USN_Hawaii_Test_03.in")

# %%
# The parsed model is displayed below.

model

# %%
# Step 3: Define the Problem for Sensitivity Analysis
# ----------------------------------------------------
# We specify which parameters to analyze and their realistic ranges.
# For this example, we focus on four key parameters:
#
# 1. **Heat of combustion**: Energy released per unit mass of fuel (affects fire intensity)
# 2. **Radiative fraction**: Fraction of fire energy released as radiation (affects heat transfer)
# 3. **Target thickness**: Material thickness of temperature measurement targets
# 4. **Target emissivity**: Surface radiation properties of targets
#
# Each parameter gets a range of realistic values to explore during the analysis.

problem = {
    "num_vars": 4,
    "names": [
        "heat_of_combustion",  # Heat of combustion (MJ/kg)
        "radiative_fraction",  # Fire radiative fraction (adimensional)
        "target_thickness",  # Target material thickness (m)
        "target_emissivity",  # Target material emissivity (adimensional)
    ],
    "bounds": [
        [100, 50000],  # Heat of combustion: 100-50000 MJ/kg
        [0.1, 1.0],  # Radiative fraction: 0.1-1.0
        [0.15, 0.60],  # Target thickness: 0.15-0.60 m
        [0.8, 0.95],  # Target emissivity: 0.8-0.95
    ],
}

print("Sensitivity analysis problem defined:")
for i, name in enumerate(problem["names"]):
    bounds = problem["bounds"][i]
    print(f"  {name}: [{bounds[0]}, {bounds[1]}]")

# %%
# Step 4: Generate Parameter Samples
# ------------------------------------
# We use Sobol sequences to create well-distributed parameter combinations.
# Sobol sampling ensures:
#
# - Good coverage of the parameter space
# - Efficient sampling for sensitivity analysis
# - Proper computation of interaction effects
#
# The number of samples affects accuracy but also computational time.

N = 64  # Number of samples (will generate N*(2*num_vars+2) total samples)
param_values = sobol_sample.sample(problem, N)

print(f"Generated {len(param_values)} parameter combinations")
print(f"Sample shape: {param_values.shape}")

df_samples = pd.DataFrame(param_values, columns=problem["names"])
print("\nFirst 5 parameter combinations:")
print(df_samples.head())

# %%
# Step 5: Run Model Evaluations
# ------------------------------
# Now we run CFAST simulations for each parameter combination. This is the
# most time-consuming step as we need to:
#
# - Modify the model with each parameter set using :meth:`~pycfast.CFASTModel.update_fire_params` and :meth:`~pycfast.CFASTModel.update_material_params`
# - Run the CFAST simulation with :meth:`~pycfast.CFASTModel.run`
# - Extract and store the output values
#
# Progress indicators help track completion of all evaluations.

print("Running model evaluations...")
outputs = []

for i, params in enumerate(param_values):
    if i % 50 == 0:
        print(f"Processing sample {i}/{len(param_values)}")
        print(
            f"hoc={params[0]}, rf={params[1]}, thickness={params[2]}, emissivity={params[3]}"
        )

    temp_model = model.update_fire_params(
        fire="Hawaii_03_Fire",
        heat_of_combustion=params[0],  # heat of combustion in MJ/kg
        radiative_fraction=params[1],  # radiative fraction (0-1)
    )
    temp_model = temp_model.update_material_params(
        material="STEELSHT",
        thickness=params[2],  # thickness in meters
        emissivity=params[3],  # emissivity (0-1)
    )

    results = temp_model.run()
    max_target_temp = results["devices"]["TRGSURT_1"].max()

    outputs.append(max_target_temp)

Y = np.array(outputs)
print(f"Completed {len(outputs)} model evaluations")
print(f"Output shape: {Y.shape}")

# %%
# Step 6: Perform Sobol Sensitivity Analysis
# --------------------------------------------
# We calculate Sobol indices to quantify parameter importance:
#
# - **First-order indices (S1)**: Direct effect of each parameter alone
# - **Total-order indices (ST)**: Total effect including interactions with other parameters
# - **Interaction effects (ST - S1)**: How much parameters interact with each other
#
# Higher values indicate greater influence on the simulation output.

Si = sobol_analyze.analyze(problem, np.array(Y))

# %%
print("Sobol Sensitivity Analysis Results:")

print("\nFirst-order indices (S1):")
for i, param_name in enumerate(problem["names"]):
    print(f"  {param_name}: {Si['S1'][i]:.4f}")

print("\nTotal-order indices (ST):")
for i, param_name in enumerate(problem["names"]):
    print(f"  {param_name}: {Si['ST'][i]:.4f}")

# %%
# Step 7: Visualize Sensitivity Results
# ---------------------------------------
# The bar charts show:
#
# - **Left panel**: First-order effects (direct parameter influence)
# - **Right panel**: Total effects (including parameter interactions)
# - **Error bars**: Confidence intervals for the estimates
#
# Parameters with higher bars have greater influence on the simulation output.
# Large differences between S1 and ST indicate significant parameter interactions.

plt.style.use("seaborn-v0_8-whitegrid")

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6), constrained_layout=True)

names = problem["names"]
x = np.arange(len(names))

S1 = np.asarray(Si["S1"])
S1_conf = np.asarray(Si["S1_conf"])
ST = np.asarray(Si["ST"])
ST_conf = np.asarray(Si["ST_conf"])

cmap = plt.get_cmap("tab10")
bar_width = 0.6

ymax_candidate = np.nanmax([S1 + S1_conf, ST + ST_conf])
ymax = (
    float(np.clip(ymax_candidate + 0.06, 0, 1.0))
    if not np.isnan(ymax_candidate)
    else 1.0
)
ymin = 0.0

ax1.bar(x, S1, width=bar_width, color=cmap(0), edgecolor="black", alpha=0.9)
ax1.errorbar(
    x, S1, yerr=S1_conf, fmt="none", ecolor="black", capsize=5, elinewidth=1.25
)
ax1.set_title("First-order Sensitivity Indices (S1)", fontsize=14)
ax1.set_ylabel("Sensitivity Index", fontsize=12)
ax1.set_xlabel("Parameter", fontsize=12)
ax1.set_xticks(x)
ax1.set_xticklabels(names, rotation=45, ha="right", fontsize=10)
ax1.set_ylim(ymin, ymax)
ax1.grid(which="major", axis="y", linestyle="--", alpha=0.4)

for i, v in enumerate(S1):
    if np.isnan(v):
        txt = "nan"
    else:
        txt = f"{v:.2f} ± {S1_conf[i]:.2f}"
    ax1.text(
        i,
        (v if not np.isnan(v) else 0) + (0.02 if not np.isnan(v) else 0.01),
        txt,
        ha="center",
        fontsize=9,
    )

ax2.bar(x, ST, width=bar_width, color=cmap(1), edgecolor="black", alpha=0.9)
ax2.errorbar(
    x, ST, yerr=ST_conf, fmt="none", ecolor="black", capsize=5, elinewidth=1.25
)
ax2.set_title("Total-order Sensitivity Indices (ST)", fontsize=14)
ax2.set_ylabel("Sensitivity Index", fontsize=12)
ax2.set_xlabel("Parameter", fontsize=12)
ax2.set_xticks(x)
ax2.set_xticklabels(names, rotation=45, ha="right", fontsize=10)
ax2.set_ylim(ymin, ymax)
ax2.grid(which="major", axis="y", linestyle="--", alpha=0.4)

for i, v in enumerate(ST):
    if np.isnan(v):
        txt = "nan"
    else:
        txt = f"{v:.2f} ± {ST_conf[i]:.2f}"
    ax2.text(
        i,
        (v if not np.isnan(v) else 0) + (0.02 if not np.isnan(v) else 0.01),
        txt,
        ha="center",
        fontsize=9,
    )

ax1.yaxis.set_major_formatter(FormatStrFormatter("%.2f"))
ax2.yaxis.set_major_formatter(FormatStrFormatter("%.2f"))

for ax in (ax1, ax2):
    ax.axhline(0, color="gray", linewidth=0.8)
    ax.set_ylim(bottom=ymin)

plt.suptitle("Sobol Sensitivity Indices with 95% Confidence Intervals", fontsize=16)
plt.show()

interaction_effects = ST - S1
print("Interaction Effects (ST - S1):")
for i, param_name in enumerate(names):
    val = interaction_effects[i]
    if np.isnan(val):
        print(f"  {param_name}: nan")
    else:
        tag = "(interactions dominant)" if val > 0.05 else ""
        print(f"{param_name}: {val:.3f}{tag}")

# %%
# Cleanup
# -------
# CFAST generates temporary output files during simulation runs. We clean
# these up to keep the workspace tidy and avoid confusion with future runs.

import glob
import os

files_to_remove = glob.glob("USN_Hawaii_Test_03*")

for file in files_to_remove:
    if os.path.exists(file):
        os.remove(file)
        print(f"Removed {file}")

if files_to_remove:
    print("Cleanup completed!")
else:
    print("No files to clean up.")
