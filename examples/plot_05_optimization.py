"""
====================================================
05 Operational research with optimization algorithms
====================================================

This notebook demonstrates how to use optimization algorithms to find the best parameter values for CFAST fire simulations.

We'll use SciPy's optimization algorithms to efficiently explore the parameter space and find optimal fire model configurations.
"""

# %%
# Step 1: Import Required Libraries
# -----------------------------------
# We'll import:
#
# - **SciPy optimize**: For optimization algorithms (minimize, bounds handling)
# - **Scikit-learn**: For parameter scaling and preprocessing
# - **PyCFAST**: For parsing and running CFAST models (see :func:`~pycfast.parsers.parse_cfast_file` and :meth:`~pycfast.CFASTModel.run`)
# - **Standard libraries**: For data manipulation and visualization

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import optimize
from sklearn.preprocessing import MinMaxScaler

from pycfast.parsers import parse_cfast_file

# %%
# Step 2: Load Base Model
# -----------------------
# We start with an existing CFAST model that will serve as our optimization
# baseline. This model contains all simulation settings and components.
#
# For this example, we use :func:`~pycfast.parsers.parse_cfast_file` to load the
# `SP_AST_Diesel_1p1.in <https://github.com/firemodels/cfast/blob/master/Validation/SP_AST/SP_AST_Diesel_1p1.in>`_
# model which is fast to compute, making it suitable for optimization studies.

model = parse_cfast_file("data/SP_AST_Diesel_1p1.in")

# %%
# The parsed model is displayed below.

model

# %%
model.summary()

# %%
# Step 3: Define the Optimization Problem
# ----------------------------------------
# We specify:
#
# 1. **Parameters to optimize**: Which model inputs to vary
# 2. **Parameter bounds**: Realistic ranges for each parameter
# 3. **Starting point**: Initial guess for the optimization
# 4. **Objective**: What to maximize/minimize (here: maximize TRGSURT_2 temperature)
#
# **Parameters chosen:**
#
# - **Soot yield**: Amount of soot produced by combustion (affects visibility and radiation)
# - **Radiative fraction**: Portion of fire energy released as radiation (affects heat transfer)
#
# We keep the problem simple with 2 parameters for demonstration, but you can
# optimize many parameters simultaneously.

bounds = {
    "soot_yield": [0.01, 0.12],  # soot yield: 0.01-0.12
    "radiative_fraction": [0.20, 0.45],  # radiative fraction: 0.20-0.45
}
x0 = {"soot_yield": 0.05, "radiative_fraction": 0.35}

param_names = list(bounds.keys())

print("Optimization problem defined:")
for name, bound in bounds.items():
    print(f"{name}: [{bound[0]}, {bound[1]}]")

# %%
# Step 4: Format Bounds for SciPy
# --------------------------------
# We scale and prepare bounds in the format required by SciPy optimization functions.

bounds_array = np.array(list(bounds.values()))  # Shape: (n_params, 2)
print(f"Original bounds shape: {bounds_array.shape}")
print(f"Bounds array:\n{bounds_array}")

# Create scaler that will map from original bounds to [0,1] for each parameter
scaler = MinMaxScaler(feature_range=(0, 1))

scaler.fit(bounds_array.T)  # Transpose so each parameter is a column

scaled_bounds = [(0.0, 1.0) for _ in range(len(bounds))]
print(f"Scaled bounds: {scaled_bounds}")

x0_array = np.array(list(x0.values())).reshape(1, -1)  # Shape: (1, n_params)
scaled_x0 = scaler.transform(x0_array).flatten()
print(f"Original x0: {list(x0.values())}")
print(f"Scaled x0: {scaled_x0}")

test_min = scaler.transform(bounds_array[:, 0].reshape(1, -1)).flatten()
test_max = scaler.transform(bounds_array[:, 1].reshape(1, -1)).flatten()
print(f"Scaled min bounds: {test_min}")
print(f"Scaled max bounds: {test_max}")

# %%
# Step 5: Define Objective Function
# -----------------------------------
# The objective function is the heart of optimization. It:
#
# - **Receives scaled parameters** from the optimizer
# - **Converts back to physical units** using the scaler
# - **Runs the simulation** with :meth:`~pycfast.CFASTModel.run`
# - **Returns the negative temperature** (since SciPy minimizes, but we want to maximize temperature)
#
# The function also uses a cache to avoid re-computing identical parameter combinations.

optimization_path = []  # Track the actual optimization path


def objective_function(x):
    x = np.array([x])
    x = scaler.inverse_transform(x.reshape(1, -1))
    x = x.transpose()
    x = [x[0][0], x[1][0]]  # Convert from 2D array to 1D list
    soot_yield = x[0]
    radiative_fraction = x[1]

    # recreate data_table with soot_yield value updated
    data_table = [
        row[:5] + [soot_yield] + row[6:] if len(row) > 6 else row
        for row in model.fires[0].data_table
    ]

    # Update model with new fire parameters using :meth:`~pycfast.CFASTModel.update_fire_params`
    temp_model = model.update_fire_params(
        fire="n-Decane Test 1_Fire",
        data_table=data_table,
        radiative_fraction=radiative_fraction,
    )

    results = temp_model.run()

    max_trgsurt_2 = results["devices"]["TRGSURT_2"].max()
    print(
        f"Computing point: SY={soot_yield:.4f}, RF={radiative_fraction:.4f}, Temp={max_trgsurt_2:.2f}"
    )

    optimization_path.append((soot_yield, radiative_fraction, max_trgsurt_2))

    return -max_trgsurt_2  # Negate to convert maximization to minimization


# %%
# Step 6: Generate Complete Function Map
# ----------------------------------------
# Before optimization, we evaluate the objective function on a grid to visualize
# the landscape, validate optimizer results, and identify optimal regions.
# This helps us understand if the function is smooth or has local minima.

default_max_temp = model.run()["devices"]["TRGSURT_2"].max()
print(f"Default model max TRGSURT_2: {default_max_temp:.2f} °C")

# %%
grid_resolution = 15  # 15x15 = 225 function evaluations

soot_yield_grid = np.linspace(
    bounds["soot_yield"][0], bounds["soot_yield"][1], grid_resolution
)
radiative_fraction_grid = np.linspace(
    bounds["radiative_fraction"][0], bounds["radiative_fraction"][1], grid_resolution
)

function_map = {}
temperature_grid = np.zeros((grid_resolution, grid_resolution))

total_evaluations = grid_resolution * grid_resolution
evaluation_count = 0

for i, soot_yield in enumerate(soot_yield_grid):
    for j, radiative_fraction in enumerate(radiative_fraction_grid):
        evaluation_count += 1

        if evaluation_count % 25 == 0 or evaluation_count == total_evaluations:
            print(
                f"Progress: {evaluation_count}/{total_evaluations} ({100 * evaluation_count / total_evaluations:.1f}%)"
            )

        # recreate data_table with soot_yield value updated
        data_table = [
            row[:5] + [soot_yield] + row[6:] if len(row) > 6 else row
            for row in model.fires[0].data_table
        ]

        # Update model with new fire parameters using :meth:`~pycfast.CFASTModel.update_fire_params`
        temp_model = model.update_fire_params(
            fire="n-Decane Test 1_Fire",
            data_table=data_table,
            radiative_fraction=radiative_fraction,
        )

        results = temp_model.run()

        # Extract max TRGSURT_2
        max_trgsurt_2 = results["devices"]["TRGSURT_2"].max()

        function_map[(soot_yield, radiative_fraction)] = max_trgsurt_2
        temperature_grid[i, j] = max_trgsurt_2

SY_grid, RF_grid = np.meshgrid(soot_yield_grid, radiative_fraction_grid)

grid_df = pd.DataFrame(
    [(k[0], k[1], v) for k, v in function_map.items()],
    columns=["soot_yield", "radiative_fraction", "max_trgsurt_2"],
)

print("Function statistics:")
print(f"Minimum temperature: {grid_df['max_trgsurt_2'].min():.2f} °C")
print(f"Maximum temperature: {grid_df['max_trgsurt_2'].max():.2f} °C")
print(f"Mean temperature: {grid_df['max_trgsurt_2'].mean():.2f} °C")
print(f"Default model temperature: {default_max_temp:.2f} °C")

# %%
# Step 7: Run Optimization Algorithm
# ------------------------------------
# Now we execute the Nelder-Mead optimization algorithm. This method requires
# no gradients, uses a simplex to converge toward the optimum, and respects
# parameter constraints during the search.

result = optimize.minimize(
    objective_function, x0=scaled_x0, method="Nelder-Mead", bounds=scaled_bounds
)

# %%
max_temp_found = -result.fun
print(f"Found max temp: {max_temp_found}")
optimized_params = dict(zip(param_names, result.x, strict=False))
print("Optimized parameters:")
for pname, pval in optimized_params.items():
    idx = list(param_names).index(pname)
    arr = np.zeros((1, len(param_names)))
    arr[0, idx] = pval
    unscaled_val = scaler.inverse_transform(arr)[0][idx]
    print(f"  {pname}: {unscaled_val}")

# %%
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

contour = ax1.contourf(
    SY_grid, RF_grid, temperature_grid.T, levels=20, cmap="viridis", alpha=0.8
)
contour_lines = ax1.contour(
    SY_grid,
    RF_grid,
    temperature_grid.T,
    levels=10,
    colors="white",
    alpha=0.6,
    linewidths=0.5,
)
ax1.clabel(contour_lines, inline=True, fontsize=8, fmt="%.1f")

if optimization_path:
    path_soot = [point[0] for point in optimization_path]
    path_rf = [point[1] for point in optimization_path]

    ax1.plot(
        path_soot, path_rf, "r-", linewidth=3, alpha=0.9, label="Optimization Path"
    )
    ax1.plot(path_soot, path_rf, "ro", markersize=5, alpha=0.9)

    ax1.plot(path_soot[0], path_rf[0], "go", markersize=12, label="Start Point")
    ax1.plot(path_soot[-1], path_rf[-1], "rs", markersize=12, label="Final Point")

ax1.set_xlabel("Soot Yield")
ax1.set_ylabel("Radiative Fraction")
ax1.set_title("Complete Objective Function Map with Optimization Path")
ax1.legend()
ax1.grid(True, alpha=0.3)
plt.colorbar(contour, ax=ax1, label="Max TRGSURT_2 (°C)")

ax2 = fig.add_subplot(122, projection="3d")
surface = ax2.plot_surface(
    SY_grid, RF_grid, temperature_grid.T, cmap="viridis", alpha=0.7
)

if optimization_path:
    path_temps = [point[2] for point in optimization_path]
    ax2.plot(
        path_soot, path_rf, path_temps, "r-", linewidth=4, label="Optimization Path"
    )
    ax2.scatter(path_soot, path_rf, path_temps, c="red", s=50)
    ax2.scatter(
        [path_soot[0]], [path_rf[0]], [path_temps[0]], c="green", s=150, label="Start"
    )
    ax2.scatter(
        [path_soot[-1]],
        [path_rf[-1]],
        [path_temps[-1]],
        c="red",
        s=150,
        marker="s",
        label="Final",
    )

ax2.set_xlabel("Soot Yield")
ax2.set_ylabel("Radiative Fraction")
ax2.set_zlabel("Max TRGSURT_2 (°C)")
ax2.set_title("3D Objective Function Surface")

plt.tight_layout()
plt.show()

# Calculate statistics for later use
max_idx = np.unravel_index(np.argmax(temperature_grid), temperature_grid.shape)
global_opt_soot = soot_yield_grid[max_idx[0]]
global_opt_rf = radiative_fraction_grid[max_idx[1]]
global_opt_temp = temperature_grid[max_idx]

final_temp = optimization_path[-1][2]
path_temps = [point[2] for point in optimization_path]

print("Function Map Statistics:")
print(
    f"Grid resolution: {grid_resolution}x{grid_resolution} = {grid_resolution**2} points"
)
print(
    f"Temperature range: {grid_df['max_trgsurt_2'].min():.2f} - {grid_df['max_trgsurt_2'].max():.2f} °C"
)
print(f"Temperature std dev: {grid_df['max_trgsurt_2'].std():.2f} °C")
print("\nGlobal Optimum (from complete map):")
print(f"Soot Yield: {global_opt_soot:.4f}")
print(f"Radiative Fraction: {global_opt_rf:.4f}")
print(f"Max Temperature: {global_opt_temp:.2f} °C")
print("\nOptimization Results:")
print(
    f"Start point: SY={path_soot[0]:.4f}, RF={path_rf[0]:.4f}, Temp={path_temps[0]:.2f} °C"
)
print(
    f"Final point: SY={path_soot[-1]:.4f}, RF={path_rf[-1]:.4f}, Temp={path_temps[-1]:.2f} °C"
)
print(f"Function evaluations: {len(optimization_path)}")
print(f"Temperature improvement: {path_temps[-1] - path_temps[0]:.2f} °C")
print(
    f"Distance from global optimum: {np.sqrt((path_soot[-1] - global_opt_soot) ** 2 + (path_rf[-1] - global_opt_rf) ** 2):.4f}"
)

improvement_achieved = path_temps[-1] - default_max_temp
max_possible_improvement = global_opt_temp - default_max_temp
efficiency = (
    (improvement_achieved / max_possible_improvement) * 100
    if max_possible_improvement > 0
    else 0
)
print(f"Optimization efficiency: {efficiency:.1f}% of maximum possible improvement")

# %%
fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))

iterations = range(1, len(optimization_path) + 1)
path_soot = [point[0] for point in optimization_path]
path_rf = [point[1] for point in optimization_path]
path_temps = [point[2] for point in optimization_path]

ax1.plot(
    iterations, path_temps, "b-o", linewidth=2, markersize=4, label="Optimization Path"
)
ax1.axhline(
    y=default_max_temp,
    color="r",
    linestyle="--",
    alpha=0.7,
    label=f"Default Model ({default_max_temp:.2f} °C)",
)
ax1.axhline(
    y=global_opt_temp,
    color="g",
    linestyle="--",
    alpha=0.7,
    label=f"Global Optimum ({global_opt_temp:.2f} °C)",
)
ax1.set_xlabel("Iteration")
ax1.set_ylabel("Max TRGSURT_2 (°C)")
ax1.set_title("Convergence History")
ax1.grid(True, alpha=0.3)
ax1.legend()

ax2.plot(iterations, path_soot, "g-o", linewidth=2, markersize=4, label="Soot Yield")
ax2.plot(
    iterations, path_rf, "m-s", linewidth=2, markersize=4, label="Radiative Fraction"
)
ax2.axhline(
    y=global_opt_soot, color="g", linestyle=":", alpha=0.7, label="Global Opt SY"
)
ax2.axhline(y=global_opt_rf, color="m", linestyle=":", alpha=0.7, label="Global Opt RF")
ax2.set_xlabel("Iteration")
ax2.set_ylabel("Parameter Value")
ax2.set_title("Parameter Evolution")
ax2.grid(True, alpha=0.3)
ax2.legend()

distances = [
    np.sqrt((sy - global_opt_soot) ** 2 + (rf - global_opt_rf) ** 2)
    for sy, rf in zip(path_soot, path_rf, strict=False)
]
ax3.plot(iterations, distances, "r-o", linewidth=2, markersize=4)
ax3.set_xlabel("Iteration")
ax3.set_ylabel("Distance from Global Optimum")
ax3.set_title("Convergence to Global Optimum")
ax3.grid(True, alpha=0.3)
ax3.set_yscale("log")

improvements = [temp - default_max_temp for temp in path_temps]
max_improvement = global_opt_temp - default_max_temp
efficiency = [
    (imp / max_improvement) * 100 if max_improvement > 0 else 0 for imp in improvements
]

ax4.plot(iterations, efficiency, "purple", linewidth=2, marker="o", markersize=4)
ax4.axhline(
    y=100, color="g", linestyle="--", alpha=0.7, label="100% Efficiency (Global Opt)"
)
ax4.set_xlabel("Iteration")
ax4.set_ylabel("Optimization Efficiency (%)")
ax4.set_title("Optimization Efficiency Over Time")
ax4.grid(True, alpha=0.3)
ax4.legend()
ax4.set_ylim(0, max(105, max(efficiency) * 1.1))

plt.tight_layout()
plt.show()

print(f"Initial efficiency: {efficiency[0]:.1f}%")
print(f"Final efficiency: {efficiency[-1]:.1f}%")
print(f"Best efficiency achieved: {max(efficiency):.1f}%")
print(f"Final distance from global optimum: {distances[-1]:.4f}")

# %%
# Cleanup
# -------

import glob
import os

files_to_remove = glob.glob("SP_AST_Diesel_1p1*")

for file in files_to_remove:
    if os.path.exists(file):
        os.remove(file)
        print(f"Removed {file}")

if files_to_remove:
    print("Cleanup completed!")
else:
    print("No files to clean up.")
