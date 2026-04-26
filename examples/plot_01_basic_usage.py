"""
==============
01 Basic usage
==============

This example shows how to create a basic CFAST fire simulation model using PyCFAST.
We'll build a complete simulation with two compartments, ventilation, fire sources, and
target devices.
"""

# %%
# Step 1: Import Required PyCFAST Components
# ------------------------------------------
# First, let's import all the necessary PyCFAST components.
from pycfast import (
    CeilingFloorVent,
    CFASTModel,
    Compartment,
    Device,
    Fire,
    Material,
    MechanicalVent,
    SimulationEnvironment,
    SurfaceConnection,
    WallVent,
)

# %%
# Step 2: Configure Simulation Environment
# ----------------------------------------
# The simulation environment defines the global parameters for our CFAST simulation. The
# :class:`~pycfast.SimulationEnvironment` class is the equivalent of the CEdit
# simulation settings tab but programmatically defined.
#
# .. figure:: /_static/images/cedit-simulation-tab.png
#    :width: 800px

simulation_env = SimulationEnvironment(
    title="Simple example",
    time_simulation=7200,
    print=40,
    smokeview=10,
    spreadsheet=10,
    init_pressure=101325,
    relative_humidity=50,
    interior_temperature=20,
    exterior_temperature=20,
    adiabatic=False,
    lower_oxygen_limit=0.1,
    max_time_step=10,
)
# %%
# Step 3: Define Material Properties
# ----------------------------------
# Material properties define the thermal characteristics of surfaces in our compartments. The
# :class:`~pycfast.Material` class is the equivalent of the CEdit simulation settings tab but
# programmatically defined.
#
# .. figure:: /_static/images/cedit-material-properties-tab.png
#    :alt: CEdit Material Properties Tab
#    :width: 800px
#
#
# Here we define gypsum board, which is commonly used for walls and ceilings.

gypsum_board = Material(
    id="Gypboard",
    material="Gypsum Board",
    conductivity=0.16,
    density=480,
    specific_heat=1,
    thickness=0.015,
    emissivity=0.9,
)

# %%
# Step 4: Create Compartment
# --------------------------
# Compartment represent the physical spaces in our building. The
# :class:`~pycfast.Compartment` class is the equivalent of the CEdit compartment tab
# but programmatically defined.
#
# .. figure:: /_static/images/cedit-compartments-tab.png
#    :alt: CEdit Compartment Tab
#    :width: 800px
#
#
# We'll create two 10×10×10 meter rooms stacked vertically.

ground_level = Compartment(
    id="Comp 1",
    depth=10.0,
    height=10.0,
    width=10.0,
    ceiling_mat_id="Gypboard",
    ceiling_thickness=0.01,
    wall_mat_id="Gypboard",
    wall_thickness=0.01,
    floor_mat_id="Gypboard",
    floor_thickness=0.01,
    origin_x=0,
    origin_y=0,
    origin_z=0,
)

upper_level = Compartment(
    id="Comp 2",
    depth=10.0,
    height=10.0,
    width=10.0,
    ceiling_mat_id="Gypboard",
    ceiling_thickness=0.01,
    wall_mat_id="Gypboard",
    wall_thickness=0.01,
    floor_mat_id="Gypboard",
    floor_thickness=0.01,
    origin_x=0,
    origin_y=0,
    origin_z=10,
)

# %%
# Step 5: Define Ventilation Systems
# ----------------------------------
# As before, we'll create three types of ventilation:
#
# .. list-table::
#    :widths: 33 33 34
#    :header-rows: 1
#
#    * - **Wall vents**
#      - **Ceiling/floor vents**
#      - **Mechanical vents**
#    * - Natural ventilation through openings in walls
#      - Natural ventilation between compartments
#      - Forced ventilation systems
#    * - .. figure:: /_static/images/cedit-wall-vents-tab.png
#           :alt: CEdit Wall Vents Tab
#           :width: 200px
#      - .. figure:: /_static/images/cedit-ceiling-floor-vents-tab.png
#           :alt: CEdit Ceiling/Floor Vents Tab
#           :width: 200px
#      - .. figure:: /_static/images/cedit-mechanical-ventilation-tab.png
#           :alt: CEdit Mechanical Ventilation Tab
#           :width: 200px
#
# We'll use the :class:`~pycfast.MechanicalVent`, :class:`~pycfast.CeilingFloorVent`,
# and :class:`~pycfast.WallVent` classes to define our vents.

# Wall vent connecting first compartment to outside

wall_vent = WallVent(
    id="WallVent_1",
    comps_ids=["Comp 1", "OUTSIDE"],
    bottom=0.02,
    height=0.3,
    width=0.2,
    face="FRONT",
    offset=0.47,
)
ceiling_floor_vents = CeilingFloorVent(
    id="CeilFloorVent_1",
    comps_ids=["Comp 2", "Comp 1"],
    area=0.01,
    shape="SQUARE",
    offsets=[0.84, 0.86],
)

mechanical_vents = MechanicalVent(
    id="mech",
    comps_ids=["OUTSIDE", "Comp 1"],
    area=[1.2, 10],
    heights=[1, 1],
    orientations=["HORIZONTAL", "HORIZONTAL"],
    flow=1,
    cutoffs=[250, 300],
    offsets=[0, 0.6],
    filter_time=1.2,
    filter_efficiency=5,
)

# %%
# Step 6: Define Fire Sources
# ---------------------------
# Fire sources represent the combustion processes in our simulation. The
# :class:`~pycfast.Fire` class is the equivalent of the CEdit fires tab
# but programmatically defined.
#
# .. figure:: /_static/images/cedit-fires-tab.png
#    :alt: CEdit Fire Tab
#    :width: 800px
#
#
# Here we define a propane fire with specific chemical composition and heat release characteristics.

propane_fire = Fire(
    id="Propane",
    comp_id="Comp 1",
    fire_id="Propane_Fire",
    location=[0.3, 0.3],
    carbon=5,
    chlorine=2,
    hydrogen=8,
    nitrogen=1,
    oxygen=0,
    heat_of_combustion=100,
    radiative_fraction=0.3,
    data_table=[
        [0, 0, 0, 0.3, 0.008021683, 0.02, 0, 0, 0],  # t=0s
        [30, 10, 0, 0.3, 0.008021683, 0.02, 0, 0, 0],  # t=30s
        [60, 40, 0, 0.3, 0.008021683, 0.02, 0, 0, 0],  # t=60s
        [90, 90, 0, 0.3, 0.008021683, 0.02, 0, 0, 0],  # t=90s
        [120, 160, 0, 0.3, 0.008021683, 0.02, 0, 0, 0],  # t=120s
        [150, 250, 0, 0.3, 0.008021683, 0.02, 0, 0, 0],  # t=150s
        [180, 360, 0, 0.3, 0.008021683, 0.02, 0, 0, 0],  # t=180s
        [210, 490, 0, 0.3, 0.008021683, 0.02, 0, 0, 0],  # ...
        [240, 640, 0, 0.3, 0.008021683, 0.02, 0, 0, 0],
        [270, 810, 0, 0.3, 0.008021683, 0.02, 0, 0, 0],
        [300, 999.9999, 0, 0.3, 0.008021683, 0.02, 0, 0, 0],
        [600, 1000, 0, 0.3, 0.008021683, 0.02, 0, 0, 0],
        [601, 810, 0, 0.3, 0.008021683, 0.02, 0, 0, 0],
        [602, 640, 0, 0.3, 0.008021683, 0.02, 0, 0, 0],
        [603, 490, 0, 0.3, 0.008021683, 0.02, 0, 0, 0],
        [604, 360, 0, 0.3, 0.008021683, 0.02, 0, 0, 0],
        [605, 250, 0, 0.3, 0.008021683, 0.02, 0, 0, 0],
        [606, 160, 0, 0.3, 0.008021683, 0.02, 0, 0, 0],
        [607, 90, 0, 0.3, 0.008021683, 0.02, 0, 0, 0],
        [608, 40, 0, 0.3, 0.008021683, 0.02, 0, 0, 0],
        [609, 10, 0, 0.3, 0.008021683, 0.02, 0, 0, 0],
        [610, 0, 0, 0.3, 0.008021683, 0.02, 0, 0, 0],
        [620, 0, 0, 0.3, 0.008021683, 0.02, 0, 0, 0],
    ],
)

# %%
# Step 7: Add Device
# ------------------
# Device allow us to monitor conditions at specific locations. The
# :class:`~pycfast.Device` class is the equivalent of the CEdit devices tab but
# programmatically defined.
#
# .. figure:: /_static/images/cedit-targets-tab.png
#    :alt: CEdit Target Tab
#    :width: 800px
#
#
# The :class:`~pycfast.Device` class has classmethods to help create common device types:
#
# * :meth:`~pycfast.Device.create_target`: equivalent of target device
# * :meth:`~pycfast.Device.create_heat_detector`: equivalent of heat detector device
# * :meth:`~pycfast.Device.create_smoke_detector`: equivalent of smoke detector device
# * :meth:`~pycfast.Device.create_sprinkler`: equivalent of sprinkler device
#
# Here we add a target device to measure thermal conditions.
target = Device.create_target(
    id="Target_1",
    comp_id="Comp 1",
    location=[0.5, 0.5, 0],
    type="CYLINDER",
    material_id="Gypboard",
    surface_orientation="CEILING",
    thickness=0.01,
    temperature_depth=0.01,
    depth_units="M",
)

# %%
# Step 8: Configure Surface Connections
# -------------------------------------
# Surface connections define thermal connections between compartments through shared
# surfaces. The :class:`~pycfast.SurfaceConnection` class is the equivalent of the
# CEdit surface connections tab but programmatically defined.
#
# .. figure:: /_static/images/cedit-surface-connections-tab.png
#    :alt: CEdit Surface Connections
#    :width: 800px
#
#
# The :class:`~pycfast.SurfaceConnection` class has 2 classmethods to help create
# common connection types :meth:`~pycfast.SurfaceConnection.ceiling_floor_connection`,
# and :meth:`~pycfast.SurfaceConnection.wall_connection`. Here we create a
# ceiling/floor connection between the two compartments to allow heat transfer and air
# flow between them.

ceiling_floor_connection = SurfaceConnection.ceiling_floor_connection(
    comp_id="Comp 1",
    comp_ids="Comp 2",
)

# %%
# Step 9: Create and Run the CFAST Model
# --------------------------------------
# Now we'll create a complete :class:`~pycfast.CFASTModel` with all our components and
# run the simulation. After running, we'll explore how to access and analyze the
# results.

model = CFASTModel(
    simulation_environment=simulation_env,
    material_properties=[gypsum_board],
    compartments=[ground_level, upper_level],
    wall_vents=[wall_vent],
    ceiling_floor_vents=[ceiling_floor_vents],
    mechanical_vents=[mechanical_vents],
    fires=[propane_fire],
    devices=[target],
    surface_connections=[ceiling_floor_connection],
    file_name="example_simulation.in",
    cfast_exe="cfast",
    extra_arguments=["-f"],
)

# %%
# Use the :meth:`~pycfast.CFASTModel.summary` method to print a summary of the model
# configuration.

print(model.summary())

# %%
# You can also save to the disk the CFAST model input file with the
# :meth:`~pycfast.CFASTModel.save` method and view its contents with
# :meth:`~pycfast.CFASTModel.view_cfast_input_file` (not necessary to run the
# simulation, as the model will be saved automatically when you run it, but useful if
# you want to inspect the generated input file or run it manually with CFAST).

model.save()

input_file_contents = model.view_cfast_input_file(pretty_print=True)
print(input_file_contents)

# %%
# The :meth:`~pycfast.CFASTModel.run` method returns a dictionary containing
# :class:`~pandas.DataFrame` for each CFAST output file. This makes it easy to analyze
# and visualize the simulation results using familiar pandas methods and matplotlib.

results = model.run(
    verbose=True,
    timeout=None,
)

# %%
# Available Output Files
# ^^^^^^^^^^^^^^^^^^^^^^
#
# Each simulation generates several CSV files with different types of data:
#
# .. list-table::
#    :header-rows: 1
#    :widths: 20 80
#
#    * - Key
#      - Description
#    * - ``'zone'``
#      - Complete zone data including temperatures, pressures, and fire parameters
#    * - ``'devices'``
#      - Target device responses (temperatures, heat fluxes)
#    * - ``'vents'``
#      - Ventilation mass flows through each vent
#    * - ``'compartments'``
#      - Detailed compartment conditions for all species
#    * - ``'walls'``
#      - Wall surface temperatures
#    * - ``'masses'``
#      - Species mass tracking over time

# %%
# Step 10: Analyzing Simulation Results
# -------------------------------------
#
# Below is a small example of comparing the Expected HRR and the Actual HRR using
# matplotlib and pandas, though you're free to use any Python data analysis tools in
# the ecosystem!

# %%
import matplotlib.pyplot as plt

df = results["compartments"]

plt.figure(figsize=(10, 6))
plt.plot(df["Time"], df["HRR_1"], label="HRR Actual", color="tab:red", linewidth=2)
plt.plot(
    df["Time"],
    df["HRR_E1"],
    label="HRR Expected",
    color="tab:blue",
    linestyle="--",
    linewidth=2,
)
plt.title("Heat Release Rate in Compartment 1")
plt.xlabel("Time (s)")
plt.ylabel("Heat Release Rate (kW)")
plt.legend()
plt.xlim(0, 1500)
plt.grid(True, linestyle="--", alpha=0.7)
plt.tight_layout()
plt.show()

# %%
# Step 11: Updating the model
# ---------------------------
# You can update any part of the model after its creation with the ``update_*`` methods
# (e.g., :meth:`~pycfast.CFASTModel.update_fire_params`). For example, to change the
# fire's radiative fraction, you can do:

# %%
# Original model
model.fires

# %%
# Updated model
new_model = model.update_fire_params(fire="Propane", radiative_fraction=0.4)
new_model.fires

# %%
# You can also add additional components to an existing model with
# :meth:`~pycfast.CFASTModel.add`. For example, to add another
# target device:

# %%
# Original model devices
for device in model.devices:
    print(device)

# %%
# Adding a new device
new_device = Device.create_target(
    id="Target_2",
    comp_id="Comp 2",
    location=[0.5, 0.5, 0.5],
    type="CYLINDER",
    material_id="Gypboard",
    surface_orientation="CEILING",
    thickness=0.01,
    temperature_depth=0.01,
    depth_units="M",
)

updated_model = model.add(new_device)

# %%
# And now the updated model has both devices
for device in updated_model.devices:
    print(device)

# %%
# Cleanup
# -------
# Finally, we clean up the temporary files generated during the simulation.

import glob
import os

files_to_remove = glob.glob("example_simulation*")

for file in files_to_remove:
    if os.path.exists(file):
        os.remove(file)
        print(f"Removed {file}")

if files_to_remove:
    print("Cleanup completed!")
else:
    print("No files to clean up.")
