"""
=====================================
02 Parsing Existing CFAST Input Files
=====================================

This example explains how to use PyCFAST's parser to read and analyze existing CFAST input files (.in) to a :class:`~pycfast.CFASTModel` object. This allows users to use their existing models, modify them, and re-run simulations with minimal effort.
"""

# %%
# Step 1: Import Necessary Components
# ------------------------------------
# We'll import the parser components and other utilities we need.

import os

from pycfast import MaterialProperties
from pycfast.parsers import parse_cfast_file

# %%
# Step 2: Parse CFAST File
# ------------------------
# The :func:`~pycfast.parsers.parse_cfast_file` is a convenience function to parse input CFAST files.
# Here we will parse the PRISME `PRS_D1.in <https://github.com/firemodels/cfast/blob/master/Validation/PRISME/PRS_D1.in>`_ input file for demonstration purposes.

model = parse_cfast_file(r"data/PRS_D1.in", r"parsed_PRS_D1.in")

# Saving locally the parsed model
model.save()

print(f"\nView of the input file parsed: \n{model.view_cfast_input_file()}")

# %%
# .. note::
#
#    When importing an existing model, ensure that all component names
#    (such as TITLE, MATERIAL, ID, etc.) use only alphanumeric characters.
#    Avoid special characters like quotes and slashes, as these may cause
#    parsing issues and will be automatically sanitized where possible.
#
#    For example, avoid including special characters (e.g., ``Material_1``
#    will be parsed, but ``Material/1 '1/4' in`` is not).

# %%
# You can inspect the parsed model with the card below.

model

# %%
# Step 3: Explore Parsed Components
# ----------------------------------
# Once parsed, you can easily inspect all model components using their
# built-in string representations or the :meth:`~pycfast.CFASTModel.summary` method.

print(f"Model: {model}")

model.summary()

# %%
# Step 4: Modify Parsed Model
# ----------------------------
# Once you have a parsed model, you can modify it using the ``update_*`` methods
# (e.g., :meth:`~pycfast.CFASTModel.update_simulation_params`) and run new simulations
# or save it as a new input file.

updated_model = model.update_simulation_params(
    time_simulation=7200, title="Extended Simulation"
)

# Add a new material with :meth:`~pycfast.CFASTModel.add_material`
new_material = MaterialProperties(
    id="Steel",
    material="Steel Plate",
    conductivity=45.0,
    density=7850,
    specific_heat=0.46,
    thickness=0.005,
    emissivity=0.7,
)
updated_model = updated_model.add_material(new_material)

# %%
# The new material properties can be inspected below.

new_material

# %%
# And the updated model with the new material and modified simulation parameters:

updated_model

# %%
# Step 5: Save Modified Model
# ----------------------------
# You can save the modified model as a new CFAST input file using :meth:`~pycfast.CFASTModel.save`.

updated_model.save(file_name="modified_PRS_D1.in")

print(f"Saved modified model to: {updated_model.file_name}")

# View the contents of the modified file
print(updated_model.view_cfast_input_file())

# %%
# Cleanup
# -------
# Clean up the temporary files we created during this demonstration.

files_to_remove = ["parsed_PRS_D1.in", "modified_PRS_D1.in"]

for file_path in files_to_remove:
    if os.path.exists(file_path):
        os.remove(file_path)
        print(f"Removed {file_path}")

print("\nCleanup completed!")
