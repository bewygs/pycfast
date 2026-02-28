Getting Started
===============

PyCFAST allows you to create and manage CFAST fire simulation models entirely in Python. You can either build models from scratch or import existing CFAST input files.

Creating a New Model
~~~~~~~~~~~~~~~~~~~~

To create a new model, import the required classes and define each component:

.. code-block:: python

    from pycfast import (
        CeilingFloorVents,
        CFASTModel,
        Compartments,
        Fires,
        MaterialProperties,
        MechanicalVents,
        SimulationEnvironment,
        WallVents,
    )

Each class represents a section from the CFAST input file (corresponding to tabs in CEdit). Here's how to build a complete model:

.. code-block:: python

    # Define simulation parameters
    simulation_environment = SimulationEnvironment(...)
    material_properties = [MaterialProperties(...)]
    compartments = [Compartments(...)]
    wall_vents = [WallVents(...)]
    ceiling_floor_vents = [CeilingFloorVents(...)]
    mechanical_vents = [MechanicalVents(...)]
    fires = [Fires(...)]

    # Create the model
    model = CFASTModel(
        simulation_environment=simulation_environment,
        material_properties=material_properties,
        compartments=compartments,
        wall_vents=wall_vents,
        ceiling_floor_vents=ceiling_floor_vents,
        mechanical_vents=mechanical_vents,
        fires=fires,
        file_name="test_simulation.in",
        cfast_exe="/path/to/cfast_executable",
        extra_arguments=["-f"],
    )

Importing Existing Models
~~~~~~~~~~~~~~~~~~~~~~~~~

You can easily import and work with existing CFAST input files:

.. code-block:: python

    from pycfast.parsers import parse_cfast_file

    model = parse_cfast_file("existing_model.in")

.. note::
   When importing existing models, ensure component names (TITLE, MATERIAL, ID, etc.) contain only alphanumeric characters. Special characters like quotes and slashes may cause parsing issues and will be automatically sanitized when possible.

Running Simulations
~~~~~~~~~~~~~~~~~~~

Once your model is ready, you can inspect it and run the simulation:

.. code-block:: python

    # Review your model configuration
    model.summary()

    # Run the simulation
    results = model.run()

The :meth:`~pycfast.CFASTModel.run` method returns a dictionary containing pandas DataFrames for each output CSV file, making it easy to analyze results directly in Python.

Modifying Models
~~~~~~~~~~~~~~~~

PyCFAST provides flexible methods to modify your models dynamically:

.. code-block:: python

    from pycfast import Compartments

    # Add new components
    new_compartment = Compartments(...)
    model = model.add_compartments(new_compartment)

    # Update existing components (by index or ID)
    model = model.update_fires(0, new_fire_parameters)

These modification methods enable parametric studies and provide smooth integration with the broader Python ecosystem.

Next Steps
~~~~~~~~~~

This quick guide covers the fundamental concepts of PyCFAST to help you start building and running fire simulations effectively.

For comprehensive documentation of all available classes, methods, and their parameters, explore the :doc:`API reference <api/index>`.

To see PyCFAST in different contexts, check out the practical :doc:`examples` that demonstrate real-world applications you can adapt for your specific needs.
