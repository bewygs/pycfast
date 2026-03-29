Getting Started
===============

PyCFAST allows you to create and manage CFAST fire simulation models entirely in Python. You can either build models from scratch or import existing CFAST input files.

Creating a New Model
~~~~~~~~~~~~~~~~~~~~

Minimal Example
^^^^^^^^^^^^^^^

This minimal model runs with just a title and one compartment with default values:

.. code-block:: python

    from pycfast import CFASTModel, Compartments, SimulationEnvironment

    model = CFASTModel(
        simulation_environment=SimulationEnvironment(title="My Simulation"),
        compartments=[Compartments()],
        # you can also add: fires, wall_vents, ceiling_floor_vents, mechanical_vents, material_properties
        file_name="my_simulation.in",
    )
    model.save()

You will have a ``my_simulation.in`` file saved in your working directory, which you can open to inspect the generated input file. This file can be run with CFAST or open with CEdit to produce results, you can also run it (preferably) from Python using the :meth:`~pycfast.CFASTModel.run` method and will return a dictionary of pandas DataFrames for each output CSV file: 

.. code-block:: python

    results = model.run()

Complete Example
^^^^^^^^^^^^^^^^

A more complete model with two :class:`~pycfast.Compartments` connected by a :class:`~pycfast.WallVents` and a :class:`~pycfast.Fires` in the first room. Components reference each other with an ID to be able to connect them together.

.. code-block:: python

    from pycfast import CFASTModel, Compartments, Fires, SimulationEnvironment, WallVents

    # Two compartments connected by a door
    room1 = Compartments(id="ROOM1", width=5.0, depth=4.0, height=2.7)
    room2 = Compartments(id="ROOM2", width=4.0, depth=4.0, height=2.7)

    # Door between the two rooms (references compartment IDs)
    wall_vent = WallVents(
        id="wallvent",
        comps_ids=["ROOM1", "ROOM2"],  # connects ROOM1 and ROOM2
        bottom=0.0,
        height=2.0,
        width=0.9,
        face="RIGHT",
    )

    # Fire data table: (n, 9) shape, can be a list of lists, a numpy.ndarray or a pandas DataFrame
    # Columns: time(s), HRR(kW), height(m), area, CO_yield, SOOT_yield, HCN_yield, HCL_yield, TRACE_yield
    fire_data = [
        [0, 0, 0.5, 0.1, 0.01, 0.01, 0, 0, 0],      # t=0s, no heat release
        [60, 100, 0.5, 0.5, 0.01, 0.01, 0, 0, 0],   # t=60s, 100 kW
        [300, 500, 1.0, 1.0, 0.01, 0.01, 0, 0, 0],  # t=300s, 500 kW steady state
        [600, 500, 1.0, 1.0, 0.01, 0.01, 0, 0, 0],  # t=600s, 500 kW start of decay
        [1000, 0, 1.0, 1.0, 0.01, 0.01, 0, 0, 0],   # t=1000s, end of fire
    ]

    # Fire in ROOM1 (references compartment ID)
    fire = Fires(
        id="FIRE1",
        comp_id="ROOM1",  # placed in ROOM1
        fire_id="POLYURETHANE",
        location=[2.0, 2.0],  # x, y position in the compartment (m)
        data_table=fire_data
    )

    model = CFASTModel(
        simulation_environment=SimulationEnvironment(title="Two-Room Fire"),
        compartments=[room1, room2],
        wall_vents=[wall_vent],
        fires=[fire],
        file_name="two_room_fire.in",
    )
    model.save()

Other components (:class:`~pycfast.CeilingFloorVents`, :class:`~pycfast.Devices`, :class:`~pycfast.MaterialProperties`, :class:`~pycfast.MechanicalVents`, :class:`~pycfast.SurfaceConnections`) follow the same pattern and are documented in the :doc:`API reference <api/index>`.

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
    print(model.summary())

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
