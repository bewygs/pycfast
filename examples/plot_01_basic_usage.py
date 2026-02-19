"""
==============
01 Basic usage
==============

This example shows how to create a basic CFAST fire simulation model using PyCFAST.
We'll build a complete simulation with two compartments, ventilation, fire sources, and target devices.
"""

# %%
# Step 1: Import Required PyCFAST Components
# ------------------------------------------
# First, let's import all the necessary PyCFAST components.
from pycfast import (
    CeilingFloorVents,
    CFASTModel,
    Compartments,
    Devices,
    Fires,
    MaterialProperties,
    MechanicalVents,
    SimulationEnvironment,
    SurfaceConnections,
    WallVents,
)

# %%
# Step 2: Configure Simulation Environment
# ----------------------------------------
# The simulation environment defines the global parameters for our CFAST simulation. The :class:`~pycfast.SimulationEnvironment` class is the equivalent of the CEdit simulation settings tab but programmatically defined.
#
# .. figure:: /_static/images/cedit-simulation-tab.png
#    :width: 800px

simulation_env = SimulationEnvironment(
    title="Simple example",
    time_simulation=7200,  # Total simulation time in seconds (2 hours)
    print=40,  # Print output every 40 seconds
    smokeview=10,  # Smokeview output every 10 seconds
    spreadsheet=10,  # Spreadsheet output every 10 seconds
    init_pressure=101325,  # Initial pressure in Pa (1 atm)
    relative_humidity=50,  # Relative humidity as percentage
    interior_temperature=20,  # Interior temperature in °C
    exterior_temperature=20,  # Exterior temperature in °C
    adiabatic=False,  # Allow heat transfer through surfaces
    lower_oxygen_limit=0.1,  # Lower oxygen limit for combustion
    max_time_step=10,  # Maximum time step in seconds
)
# %%
# You can expand the simulation environment diagram below to see all the available parameters and their descriptions.

simulation_env

# %%
# Step 3: Define Material Properties
# ----------------------------------
# Material properties define the thermal characteristics of surfaces in our compartments. The :class:`~pycfast.MaterialProperties` class is the equivalent of the CEdit simulation settings tab but programmatically defined.
#
# .. figure:: /_static/images/cedit-material-properties-tab.png
#    :alt: CEdit Material Properties Tab
#    :width: 800px
#
#
# Here we define gypsum board, which is commonly used for walls and ceilings.

gypsum_board = MaterialProperties(
    id="Gypboard",  # Unique identifier for the material
    material="Gypsum Board",  # Descriptive name
    conductivity=0.16,  # Thermal conductivity in W/m·K (not in kW as CEdit shows)
    density=480,  # Density in kg/m³
    specific_heat=1,  # Specific heat in kJ/kg·K
    thickness=0.015,  # Default thickness in meters
    emissivity=0.9,  # Surface emissivity for radiation
)

# %%
# You can see the properties of the gypsum board on the material card below.

gypsum_board

# %%
# Step 4: Create Compartments
# ---------------------------
# Compartments represent the physical spaces in our building. The :class:`~pycfast.Compartments` class is the equivalent of the CEdit compartment tab but programmatically defined.
#
# .. figure:: /_static/images/cedit-compartments-tab.png
#    :alt: CEdit Compartments Tab
#    :width: 800px
#
#
# We'll create two 10×10×10 meter rooms stacked vertically.

ground_level = Compartments(
    id="Comp 1",
    depth=10.0,  # Depth in meters (Y-direction)
    height=10.0,  # Height in meters (Z-direction)
    width=10.0,  # Width in meters (X-direction)
    ceiling_mat_id="Gypboard",  # Material for ceiling
    ceiling_thickness=0.01,  # Ceiling thickness in meters
    wall_mat_id="Gypboard",  # Material for walls
    wall_thickness=0.01,  # Wall thickness in meters
    floor_mat_id="Gypboard",  # Material for floor
    floor_thickness=0.01,  # Floor thickness in meters
    origin_x=0,  # X-coordinate of origin
    origin_y=0,  # Y-coordinate of origin
    origin_z=0,  # Z-coordinate of origin
)

upper_level = Compartments(
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
    origin_z=10,  # Positioned above first compartment
)

# %%
# You can see the properties of the compartments on the compartment cards below (we display only the first compartment as an example).

ground_level

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
# We'll use the :class:`~pycfast.MechanicalVents`, :class:`~pycfast.CeilingFloorVents`, and :class:`~pycfast.WallVents` classes to define our vents.

# Wall vent connecting first compartment to outside

wall_vent = WallVents(
    id="WallVent_1",
    comps_ids=["Comp 1", "OUTSIDE"],  # Connect compartment 1 to outside
    bottom=0.02,  # Height of bottom of vent in meters
    height=0.3,  # Height of vent opening in meters
    width=0.2,  # Width of vent opening in meters
    face="FRONT",  # Wall face (FRONT, BACK, LEFT, RIGHT)
    offset=0.47,
)
ceiling_floor_vents = CeilingFloorVents(
    id="CeilFloorVent_1",
    comps_ids=["Comp 2", "Comp 1"],  # Connect compartment 2 to compartment 1
    area=0.01,  # Vent area in m²
    shape="SQUARE",  # Shape of the vent
    width=None,  # Width (calculated from area for square)
    offsets=[0.84, 0.86],
)

mechanical_vents = MechanicalVents(
    id="mech",
    comps_ids=["OUTSIDE", "Comp 1"],  # Connect outside to compartment 1
    area=[1.2, 10],  # Areas at each end in m²
    heights=[1, 1],  # Heights at each end in meters
    orientations=["HORIZONTAL", "HORIZONTAL"],  # Duct orientations
    flow=1,  # Flow rate in m³/s
    cutoffs=[250, 300],  # Begin Drop Off and Zero Flow Pressure in Pa
    offsets=[0, 0.6],
    filter_time=1.2,  # Filter time constant
    filter_efficiency=5,  # Filter efficiency percentage
)

# %%
# You can see the properties of the wall vent on the wall vent card below (we display only the wall vent as an example).

wall_vent

# %%
# Step 6: Define Fire Sources
# ---------------------------
# Fire sources represent the combustion processes in our simulation. The :class:`~pycfast.Fires` class is the equivalent of the CEdit fires tab but programmatically defined.
#
# .. figure:: /_static/images/cedit-fires-tab.png
#    :alt: CEdit Fires Tab
#    :width: 800px
#
#
# Here we define a propane fire with specific chemical composition and heat release characteristics.

propane_fire = Fires(
    id="Propane",
    comp_id="Comp 1",  # Location: first compartment
    fire_id="Propane_Fire",
    location=[0.3, 0.3],  # X,Y coordinates within compartment
    # Chemical composition (atoms per molecule)
    carbon=5,  # Carbon atoms
    chlorine=2,  # Chlorine atoms
    hydrogen=8,  # Hydrogen atoms
    nitrogen=1,  # Nitrogen atoms
    oxygen=0,  # Oxygen atoms
    heat_of_combustion=100,  # Heat of combustion in kJ/kg
    radiative_fraction=0.3,  # Fraction of energy released as radiation
    # Fire time-line data
    # [time, mdot, hight, area, CO_yield, soot_yield, HCN_yield, HCl_yield, trace_yield]
    # you can also use an numpy array or pandas DataFrame
    # as long as the shape of the table is (n row , 9 columns)
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
# Step 7: Add Devices
# -------------------
# Devices allow us to monitor conditions at specific locations. The :class:`~pycfast.Devices` class is the equivalent of the CEdit devices tab but programmatically defined.
#
# .. figure:: /_static/images/cedit-targets-tab.png
#    :alt: CEdit Target Tab
#    :width: 800px
#
#
# The :class:`~pycfast.Devices` class has classmethods to help create common device types:
# * :meth:`~pycfast.Devices.create_target`: equivalent of target device
# * :meth:`~pycfast.Devices.create_heat_detector`: equivalent of heat detector device
# * :meth:`~pycfast.Devices.create_smoke_detector`: equivalent of smoke detector device
# * :meth:`~pycfast.Devices.create_sprinkler`: equivalent of sprinkler device
#
# Here we add a target device to measure thermal conditions.
target = Devices.create_target(
    id="Target_1",
    comp_id="Comp 1",  # Location: first compartment
    location=[0.5, 0.5, 0],  # X,Y,Z coordinates
    type="CYLINDER",  # Target geometry
    material_id="Gypboard",  # Target material
    surface_orientation="HORIZONTAL",  # Surface orientation
    thickness=0.01,  # Target thickness in meters
    temperature_depth=0.01,  # Depth for temperature measurement
    depth_units="M",  # Units for depth
)

# %%
# You can see the properties of the target device on the device card below.

target

# %%
# Step 8: Configure Surface Connections
# -------------------------------------
# Surface connections define thermal connections between compartments through shared surfaces. The :class:`~pycfast.SurfaceConnections` class is the equivalent of the CEdit surface connections tab but programmatically defined.
#
# .. figure:: /_static/images/cedit-surface-connections-tab.png
#    :alt: CEdit Surface Connections
#    :width: 800px
#
#
# The :class:`~pycfast.SurfaceConnections` class has 2 classmethods to help create common connection types :meth:`~pycfast.SurfaceConnections.ceiling_floor_connection`, and :meth:`~pycfast.SurfaceConnections.wall_connection`.
# Here we create a ceiling/floor connection between the two compartments to allow heat transfer and air flow between them.

ceiling_floor_connection = SurfaceConnections.ceiling_floor_connection(
    comp_id="Comp 1",  # Source compartment
    comp_ids="Comp 2",  # Target compartment
)

# %%
# You can see the properties of the surface connection on the surface connection card below.

ceiling_floor_connection

# %%
# Step 9: Create and Run the CFAST Model
# --------------------------------------
# Now we'll create a complete :class:`~pycfast.CFASTModel` with all our components and run the simulation. After running, we'll explore how to access and analyze the results.

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
    file_name="example_simulation.in",  # Output file name
    cfast_exe="cfast",  # Path to CFAST executable (adjust if needed)
    extra_arguments=["-f"],  # Optionnal command-line arguments
)

# %%
# You can view the complete model with the card below

model

# %%
# Or use the :meth:`~pycfast.CFASTModel.summary` method to print a summary of the model configuration.

model.summary()

# %%
# You can also save to the disk the CFAST model input file with the :meth:`~pycfast.CFASTModel.save` method and view its contents with :meth:`~pycfast.CFASTModel.view_cfast_input_file` (not neccessary
# to run the simulation, as the model will be saved automatically when you run it, but useful if
# you want to inspect the generated input file or run it manually with CFAST).

model.save()

# View the saved input file (pretty printed)
input_file_contents = model.view_cfast_input_file(pretty_print=True)
print(input_file_contents)

# %%
# The :meth:`~pycfast.CFASTModel.run` method returns a **dictionary containing pandas DataFrames** for each CFAST output file. This makes it easy to analyze and visualize the simulation results using familiar pandas methods and matplotlib.

results = model.run(
    verbose=True,  # if True, print CFAST stdoutput and stderr
    timeout=None,  # You can set a timeout in seconds to stop the simulation but None means no timeout
)

# %%
# Step 10: Analyzing Simulation Results
# -------------------------------------
# The :meth:`~pycfast.CFASTModel.run` method returns a **dictionary containing pandas DataFrames** for each CFAST output file. This makes it easy to analyze and visualize the simulation results using familiar pandas methods and matplotlib.
#
# Available Output Files
# ^^^^^^^^^^^^^^^^^^^^^^
#
# Each simulation generates several CSV files with different types of data:
#
# - **`zone`**: Complete zone data including temperatures, pressures, and fire parameters
# - **`devices`**: Target device responses (temperatures, heat fluxes)
# - **`vents`**: Ventilation mass flows through each vent
# - **`compartments`**: Detailed compartment conditions for all species
# - **`walls`**: Wall surface temperatures
# - **`masses`**: Species mass tracking over time
#
# Below is a small example of comparing the Expected HRR and the Actual HRR using matplotlib and pandas, though you're free to use any Python data analysis tools in the ecosystem!

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
# You can update any part of the model after its creation with the ``update_*`` methods (e.g., :meth:`~pycfast.CFASTModel.update_fire_params`). For example, to change the fire's radiative fraction, you can do:
print(f"Original model: {model.fires}")

# After radiative fraction update
print(
    f"\nUpdated model: {model.update_fire_params(fire='Propane', radiative_fraction=0.4).fires}"
)
# You can also add additional components to an existing model using the ``add_*`` methods (e.g., :meth:`~pycfast.CFASTModel.add_device`). For example, you can add another target device:

# %%
print("Original model devices:")
for device in model.devices:
    print(device)

# After adding a new device
new_device = Devices.create_target(
    id="Target_2",
    comp_id="Comp 2",  # Location: second compartment
    location=[0.5, 0.5, 0.5],  # X,Y,Z coordinates
    type="CYLINDER",  # Target geometry
    material_id="Gypboard",  # Target material
    surface_orientation="HORIZONTAL",  # Surface orientation
    thickness=0.01,  # Target thickness in meters
    temperature_depth=0.01,  # Depth for temperature measurement
    depth_units="M",  # Units for depth
)

updated_model = model.add_device(new_device)

print("\nAfter adding new device, updated model devices:")
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
