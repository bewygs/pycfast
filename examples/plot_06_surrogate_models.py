"""
=========================================
06 Surrogate Models with machine learning
=========================================


Build surrogate model machine learning models to predict CFAST outputs instantly instead of running full simulations.
**Goal**: Predict Target Surface Temperature of the devices (:class:`~pycfast.Devices` TRGSURT) from fire parameters: heat of combustion, radiative fraction, soot yield and target z position
**Models**: Linear → Polynomial → Gradient Boosting → Random Forest → Neural Network (PyTorch)
"""

# %%
# Step 1: Import Libraries
# -------------------------

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import torch
import torch.nn as nn
import torch.optim as optim
from scipy.stats import qmc
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import PolynomialFeatures, StandardScaler
from torch.utils.data import DataLoader, TensorDataset

from pycfast.parsers import parse_cfast_file

plt.style.use("seaborn-v0_8-whitegrid")

# %%
# Step 2: Load Base Model and Run Baseline
# ------------------------------------------
# We use :func:`~pycfast.parsers.parse_cfast_file` to load the base model and :meth:`~pycfast.CFASTModel.run` to get baseline results.

model = parse_cfast_file("data/SP_AST_Diesel_1p1.in")
baseline_results = model.run()

print(f"Baseline TRGSURT max: {baseline_results['devices']['TRGSURT_1'].max():.2f} °C")
print("Current fire parameters:")
print(f"Heat of combustion: {model.fires[0].heat_of_combustion} MJ/kg")
print(f"Radiative fraction: {model.fires[0].radiative_fraction}")
print(f"Soot yield: {model.fires[0].data_table[0][5]}")

# %%
# The parsed model is displayed below.

model

# %%
model.summary()

# %%
# Step 3: Generate Training Data
# --------------------------------
# We define parameter ranges and use Sobol sampling to generate a well-distributed
# training dataset.

param_bounds = {
    "heat_of_combustion": [5.0, 50.0],
    "radiative_fraction": [0.1, 0.5],
    "soot_yield": [0.01, 0.15],
    "target_location_z": [1.45, 5.45],  # height of target above floor
}

print("Parameter ranges:")
for param, bounds in param_bounds.items():
    print(f"  {param}: {bounds}")

# %%
# We will use Sobol sampling to generate a training dataset.
# Sobol sequences provide low-discrepancy coverage of the parameter space.


def generate_samples(bounds_dict, n_samples, seed: int = 42):
    param_names = list(bounds_dict.keys())
    lower = np.array([bounds[0] for bounds in bounds_dict.values()], dtype=float)
    upper = np.array([bounds[1] for bounds in bounds_dict.values()], dtype=float)

    sampler = qmc.Sobol(d=len(param_names), scramble=True, seed=seed)
    unit_samples = sampler.random(n_samples)

    # Centered discrepancy (default)
    disc_centered = qmc.discrepancy(unit_samples)

    # L2-star discrepancy
    disc_l2 = qmc.discrepancy(unit_samples, method="L2-star")

    print(f"Centered discrepancy: {disc_centered:.5f}")
    print(f"L2-star discrepancy:  {disc_l2:.5f}")

    samples = qmc.scale(unit_samples, lower, upper)
    return pd.DataFrame(samples, columns=param_names)


# Generate 100 training samples
training_samples = generate_samples(param_bounds, 100)
print(f"Generated {len(training_samples)} training samples")

# %%
# Discrepancy score allows us to measure how well the samples cover the
# parameter space. Lower is better. Now we define the simulation function
# and run CFAST for each sample.


def run_cfast_simulation(row: pd.Series) -> float:
    data_table = model.fires[0].data_table

    temp_data_table = [
        r[:5] + [row["soot_yield"]] + r[6:] if len(r) > 6 else r for r in data_table
    ]

    # update fire parameters in the model using :meth:`~pycfast.CFASTModel.update_fire_params`
    temp_model = model.update_fire_params(
        fire="n-Decane Test 1_Fire",
        data_table=temp_data_table,
        heat_of_combustion=row["heat_of_combustion"],
        radiative_fraction=row["radiative_fraction"],
    )

    # Update the second target device location using :meth:`~pycfast.CFASTModel.update_device_params`
    temp_model = temp_model.update_device_params(
        device="Targ 1",
        location=[50.0, 50.0, row["target_location_z"]],  # x, y, z
    )

    sim_results = temp_model.run()
    max_trgsurt = sim_results["devices"]["TRGSURT_1"].max()

    return max_trgsurt


# %%
# Run simulations and collect training data
print("Running CFAST simulations...")
results = []

for i, row in training_samples.iterrows():
    print(f"Running simulation {i + 1}/{len(training_samples)}", end="\r")
    max_trgsurt = run_cfast_simulation(row)

    results.append(
        {
            "heat_of_combustion": row["heat_of_combustion"],
            "radiative_fraction": row["radiative_fraction"],
            "soot_yield": row["soot_yield"],
            "target_location_z": row["target_location_z"],
            "max_trgsurt": max_trgsurt,
        }
    )

training_data = pd.DataFrame(results)
print(f"Collected {len(training_data)} successful simulations")
print(
    f"TRGSURT range: {training_data['max_trgsurt'].min():.1f} - {training_data['max_trgsurt'].max():.1f} °C"
)

# %%
# Step 4: Quick Data Exploration
# -------------------------------

# Show parameter correlations with output
input_params = [
    "heat_of_combustion",
    "radiative_fraction",
    "soot_yield",
    "target_location_z",
]
correlations = training_data[input_params].corrwith(training_data["max_trgsurt"])

print("Parameter correlations with TRGSURT:")
for param, corr in correlations.abs().sort_values(ascending=False).items():
    direction = "+" if correlations[param] > 0 else "-"
    print(f"  {param}: {direction}{corr:.3f}")

# Quick visualization
fig, ax = plt.subplots(1, 1, figsize=(8, 6))
sns.heatmap(training_data.corr(), annot=True, cmap="coolwarm", center=0, ax=ax)
plt.title("Parameter Correlation Matrix")
plt.tight_layout()
plt.show()

# %%
# The correlation analysis shows that **target height (z-axis position)** has the strongest negative correlation with TRGSURT, making it the most influential parameter for temperature prediction. This makes physical sense since the farther the target device is from the fire source, the lower the surface temperature it experiences.
#
# **Radiative fraction** shows the second strongest correlation, showing the importance of radiative heat transfer in determining target surface temperatures in fire scenarios.

# %%
# Step 5: Train Surrogate Models
# --------------------------------

# Prepare data for machine learning models
X = training_data[input_params].values
y = training_data["max_trgsurt"].values
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

models = {}
metrics = {}


# Prepare models and evaluate their performance
# 1. Linear Regression
models["Linear"] = Pipeline(
    [("scaler", StandardScaler()), ("regressor", LinearRegression())]
)
models["Linear"].fit(X_train, y_train)
y_pred = models["Linear"].predict(X_test)
metrics["Linear"] = {
    "R²": r2_score(y_test, y_pred),
    "RMSE": np.sqrt(mean_squared_error(y_test, y_pred)),
}

# 2. Polynomial Regression
models["Polynomial"] = Pipeline(
    [
        ("scaler", StandardScaler()),
        ("poly", PolynomialFeatures(degree=2, include_bias=False)),
        ("regressor", LinearRegression()),
    ]
)
models["Polynomial"].fit(X_train, y_train)
y_pred = models["Polynomial"].predict(X_test)
metrics["Polynomial"] = {
    "R²": r2_score(y_test, y_pred),
    "RMSE": np.sqrt(mean_squared_error(y_test, y_pred)),
}

# 3. Gradient Boosting
models["Gradient Boosting"] = Pipeline(
    [
        ("scaler", StandardScaler()),
        ("regressor", GradientBoostingRegressor(n_estimators=100, random_state=42)),
    ]
)
models["Gradient Boosting"].fit(X_train, y_train)
y_pred = models["Gradient Boosting"].predict(X_test)
metrics["Gradient Boosting"] = {
    "R²": r2_score(y_test, y_pred),
    "RMSE": np.sqrt(mean_squared_error(y_test, y_pred)),
}

# 4. Random Forest
models["Random Forest"] = Pipeline(
    [
        ("scaler", StandardScaler()),
        ("regressor", RandomForestRegressor(n_estimators=100, random_state=42)),
    ]
)
models["Random Forest"].fit(X_train, y_train)
y_pred = models["Random Forest"].predict(X_test)
metrics["Random Forest"] = {
    "R²": r2_score(y_test, y_pred),
    "RMSE": np.sqrt(mean_squared_error(y_test, y_pred)),
}

print("Model Performance:")
for name, metric in metrics.items():
    print(f"  {name}: R² = {metric['R²']:.4f}, RMSE = {metric['RMSE']:.2f} °C")

# %%
# Neural net model in a separate cell below as this requires more setup.


class SimpleNN(nn.Module):
    def __init__(self, input_size):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(input_size, 16),
            nn.ReLU(),
            nn.Linear(16, 16),
            nn.ReLU(),
            nn.Linear(16, 1),
        )

    def forward(self, x):
        return self.net(x)


scaler_nn = StandardScaler()
X_train_scaled = scaler_nn.fit_transform(X_train)
X_test_scaled = scaler_nn.transform(X_test)

y_scaler = StandardScaler()
y_train_scaled = y_scaler.fit_transform(y_train.reshape(-1, 1)).flatten()

X_train_tensor = torch.FloatTensor(X_train_scaled)
y_train_tensor = torch.FloatTensor(y_train_scaled).reshape(-1, 1)
X_test_tensor = torch.FloatTensor(X_test_scaled)

val_fraction = 0.2
n_val = int(len(X_train_tensor) * val_fraction)
X_val_tensor = X_train_tensor[:n_val]
y_val_tensor = y_train_tensor[:n_val]
X_tr_tensor = X_train_tensor[n_val:]
y_tr_tensor = y_train_tensor[n_val:]

train_dataset = TensorDataset(X_tr_tensor, y_tr_tensor)
val_dataset = TensorDataset(X_val_tensor, y_val_tensor)

train_loader = DataLoader(train_dataset, batch_size=16, shuffle=True)
val_loader = DataLoader(val_dataset, batch_size=256, shuffle=False)

model_nn = SimpleNN(X_train.shape[1])
criterion = nn.MSELoss()
optimizer = optim.Adam(model_nn.parameters(), lr=0.001, weight_decay=1e-5)
scheduler = optim.lr_scheduler.ReduceLROnPlateau(
    optimizer, mode="min", factor=0.5, patience=10
)

best_val_loss = float("inf")
patience = 20
patience_counter = 0
best_state = None

history = {"train": [], "val": []}

for epoch in range(1000):
    model_nn.train()
    train_loss = 0.0
    for batch_X, batch_y in train_loader:
        optimizer.zero_grad()
        outputs = model_nn(batch_X)
        loss = criterion(outputs, batch_y)
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model_nn.parameters(), max_norm=1.0)
        optimizer.step()
        train_loss += loss.item()
    train_loss /= len(train_loader)

    model_nn.eval()
    with torch.no_grad():
        val_loss = 0.0
        for batch_X, batch_y in val_loader:
            outputs = model_nn(batch_X)
            val_loss += criterion(outputs, batch_y).item()
        val_loss /= len(val_loader)

    scheduler.step(val_loss)

    history["train"].append(train_loss)
    history["val"].append(val_loss)

    if epoch % 40 == 0:
        print(
            f"Epoch {epoch}, Train Loss: {train_loss:.6f}, Val Loss: {val_loss:.6f}, LR: {optimizer.param_groups[0]['lr']:.6f}"
        )

    if val_loss < best_val_loss:
        best_val_loss = val_loss
        best_state = {k: v.clone() for k, v in model_nn.state_dict().items()}
        patience_counter = 0
    else:
        patience_counter += 1
        if patience_counter >= patience:
            print(f"Early stopping at epoch {epoch + 1}")
            break

if best_state:
    model_nn.load_state_dict(best_state)

model_nn.eval()
with torch.no_grad():
    y_pred_nn_scaled = model_nn(X_test_tensor).cpu().numpy()
    y_pred_nn = y_scaler.inverse_transform(y_pred_nn_scaled).flatten()

models["Neural Network"] = {
    "model": model_nn,
    "scaler": scaler_nn,
    "y_scaler": y_scaler,
}

metrics["Neural Network"] = {
    "R²": r2_score(y_test, y_pred_nn),
    "RMSE": np.sqrt(mean_squared_error(y_test, y_pred_nn)),
}
print(
    f"Neural Network: R² = {metrics['Neural Network']['R²']:.4f}, RMSE = {metrics['Neural Network']['RMSE']:.2f} °C"
)

best_model = max(metrics.keys(), key=lambda k: metrics[k]["R²"])
print(f"\nBest model: {best_model} (R² = {metrics[best_model]['R²']:.4f})")

# %%
# Plotting the training history shows that the model is learning well without overfitting.

plt.figure(figsize=(7, 4))
plt.plot(history["train"], label="Training Loss", color="#0072B2", linewidth=2)
plt.plot(history["val"], label="Validation Loss", color="#D55E00", linewidth=2)
plt.xlabel("Epoch", fontsize=12)
plt.ylabel("MSE Loss (scaled)", fontsize=12)
plt.title("Neural Network Training and Validation Loss", fontsize=14)
plt.yscale("log")
plt.legend(fontsize=11)
plt.grid(True, alpha=0.4)

min_val_epoch = np.argmin(history["val"])
min_val_loss = history["val"][min_val_epoch]

plt.tight_layout()
plt.show()

# %%
# Step 6: Evaluate and Compare Models
# ------------------------------------

model_names = list(metrics.keys())
n_models = len(model_names)

fig = plt.figure(figsize=(20, 12))

for i, model_name in enumerate(model_names):
    ax = plt.subplot(2, n_models, i + 1)

    if model_name == "Neural Network":
        model_obj = models[model_name]
        model_obj["model"].eval()
        with torch.no_grad():
            y_pred_scaled = model_obj["model"](X_test_tensor).numpy()
            y_pred = model_obj["y_scaler"].inverse_transform(y_pred_scaled).flatten()
    else:
        y_pred = models[model_name].predict(X_test)

    ax.scatter(y_test, y_pred, alpha=0.6, s=30)
    min_val, max_val = y_test.min(), y_test.max()
    ax.plot([min_val, max_val], [min_val, max_val], "r--", linewidth=2)
    ax.set_xlabel("Actual TRGSURT (°C)")
    ax.set_ylabel("Predicted TRGSURT (°C)")
    ax.set_title(f"{model_name}\nR² = {metrics[model_name]['R²']:.4f}")
    ax.grid(True, alpha=0.3)

    ax.text(
        0.05,
        0.95,
        f"RMSE = {metrics[model_name]['RMSE']:.1f}°C",
        transform=ax.transAxes,
        verticalalignment="top",
        bbox={"boxstyle": "round", "facecolor": "white", "alpha": 0.8},
    )

ax_r2 = plt.subplot(2, 2, 3)
r2_scores = [metrics[m]["R²"] for m in model_names]
colors = ["blue", "green", "orange", "red"][: len(model_names)]

bars = ax_r2.bar(model_names, r2_scores, color=colors)
ax_r2.set_ylabel("R² Score")
ax_r2.set_title("R² Score Comparison")
ax_r2.tick_params(axis="x", rotation=45)
ax_r2.grid(True, alpha=0.3)

for bar, score in zip(bars, r2_scores, strict=False):
    height = bar.get_height()
    ax_r2.text(
        bar.get_x() + bar.get_width() / 2.0,
        height + 0.01,
        f"{score:.3f}",
        ha="center",
        va="bottom",
        fontsize=9,
    )

ax_rmse = plt.subplot(2, 2, 4)
rmse_scores = [metrics[m]["RMSE"] for m in model_names]

bars = ax_rmse.bar(model_names, rmse_scores, color=colors)
ax_rmse.set_ylabel("RMSE (°C)")
ax_rmse.set_title("RMSE Comparison")
ax_rmse.tick_params(axis="x", rotation=45)
ax_rmse.grid(True, alpha=0.3)

for bar, score in zip(bars, rmse_scores, strict=False):
    height = bar.get_height()
    ax_rmse.text(
        bar.get_x() + bar.get_width() / 2.0,
        height + 1,
        f"{score:.1f}",
        ha="center",
        va="bottom",
        fontsize=9,
    )

plt.subplots_adjust(wspace=0.4, hspace=0.4)
plt.show()

print("Performance Summary:")
for name, metric in metrics.items():
    print(f"{name}: R² = {metric['R²']:.4f}, RMSE = {metric['RMSE']:.2f} °C")

best_model = max(metrics.keys(), key=lambda k: metrics[k]["R²"])
print(f"\nBest model: {best_model} (R² = {metrics[best_model]['R²']:.4f})")

# %%
# Step 7: Rough Speed Comparison
# --------------------------------

import time

test_params = training_samples.iloc[0]
start = time.time()
test_model_run = run_cfast_simulation(test_params)
cfast_time = time.time() - start

test_X = np.array(
    [
        [
            test_params["heat_of_combustion"],
            test_params["radiative_fraction"],
            test_params["soot_yield"],
            test_params["target_location_z"],
        ]
    ]
)

start = time.time()
if best_model == "Neural Network":
    X_scaled = models[best_model]["scaler"].transform(test_X)
    X_tensor = torch.FloatTensor(X_scaled)
    models[best_model]["model"].eval()
    with torch.no_grad():
        pred = models[best_model]["model"](X_tensor).numpy()
else:
    pred = models[best_model].predict(test_X)
surrogate_time = time.time() - start

speedup = cfast_time / surrogate_time
print("Rough Speed comparison:")
print(f"CFAST: {cfast_time:.3f} seconds")
print(f"{best_model}: {surrogate_time:.6f} seconds")
print(f"Speedup: {speedup:.0f}x faster")

# %%
# Surrogate models perform well on test data and is able to speed up predictions by several orders of magnitude. Of Course this is because the parameter space is small and the model is simple. More complex models will require more training data and more sophisticated surrogate models.

# %%
# Cleanup
# -------

import glob
import os

files_to_remove = glob.glob("SP_AST_Diesel_1p1*")
for file in files_to_remove:
    if os.path.exists(file):
        os.remove(file)

print("Cleanup completed!")
