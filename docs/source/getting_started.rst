Getting Started
===============

PyCFAST allows you to create and manage CFAST fire simulation models entirely in Python. You can either build models from scratch or import existing CFAST input files.

Creating a New Model
~~~~~~~~~~~~~~~~~~~~

Minimal Example
^^^^^^^^^^^^^^^

This minimal model runs with just a title and one compartment with default values:

.. code-block:: python

    from pycfast import CFASTModel, Compartment, SimulationEnvironment

    model = CFASTModel(
        simulation_environment=SimulationEnvironment(title="My Simulation"),
        compartments=[Compartment()],
        # you can also add: fires, wall_vents, ceiling_floor_vents, mechanical_vents, material_properties
        file_name="my_simulation.in",
    )
    model.save()

You will obtain a ``my_simulation.in`` file saved in your working directory, which you can open to inspect the generated input file. This file can be run with CFAST or opened with CEdit to produce results. You can also run it (preferably) using the :meth:`~pycfast.CFASTModel.run` method, which returns a dictionary of pandas :class:`~pandas.DataFrame` for each output CSV file:

.. code-block:: python

    results = model.run()

Complete Example
^^^^^^^^^^^^^^^^

A more complete model with two :class:`~pycfast.Compartment` connected by a :class:`~pycfast.WallVent` and a :class:`~pycfast.Fire` in the first room. Components reference each other with an ID to be able to connect them together.

First import the necessary classes to define the components of the model:

.. code-block:: python

    from pycfast import CFASTModel, Compartment, Fire, SimulationEnvironment, WallVent


Connect two :class:`~pycfast.Compartment` together:

.. code-block:: python

    room1 = Compartment(id="ROOM1", width=5.0, depth=4.0, height=2.7)
    room2 = Compartment(id="ROOM2", width=4.0, depth=4.0, height=2.7)


Door between the two rooms with a :class:`~pycfast.WallVent`:

.. code-block:: python

    wall_vent = WallVent(
        id="wallvent",
        comps_ids=["ROOM1", "ROOM2"],
        bottom=0.0,
        height=2.0,
        width=0.9,
        face="RIGHT",
    )

A :class:`~pycfast.Fire` requires a data table with shape ``(n, 9)`` where ``n`` is the number
of time steps and the 9 columns are:

.. list-table::
   :header-rows: 1
   :widths: 10 25 15 50

   * - Index
     - Name
     - Unit
     - Description
   * - 0
     - ``TIME``
     - s
     - Simulation time
   * - 1
     - ``HRR``
     - kW
     - Heat release rate
   * - 2
     - ``HEIGHT``
     - m
     - Flame height
   * - 3
     - ``AREA``
     - m²
     - Fire base area
   * - 4
     - ``CO_YIELD``
     - kg/kg
     - Carbon monoxide yield
   * - 5
     - ``SOOT_YIELD``
     - kg/kg
     - Soot yield
   * - 6
     - ``HCN_YIELD``
     - kg/kg
     - Hydrogen cyanide yield
   * - 7
     - ``HCL_YIELD``
     - kg/kg
     - Hydrogen chloride yield
   * - 8
     - ``TRACE_YIELD``
     - kg/kg
     - Trace species yield

The data table can be a list of lists, a :class:`~numpy.ndarray`, a :class:`~pandas.DataFrame` or a dictionary with the column names as keys:

.. code-block:: python

    fire_data = [
        [0, 0, 0.5, 0.1, 0.01, 0.01, 0, 0, 0],      # t=0s, no heat release
        [60, 100, 0.5, 0.5, 0.01, 0.01, 0, 0, 0],   # t=60s, 100 kW
        [300, 500, 1.0, 1.0, 0.01, 0.01, 0, 0, 0],  # t=300s, 500 kW steady state
        [600, 500, 1.0, 1.0, 0.01, 0.01, 0, 0, 0],  # t=600s, 500 kW start of decay
        [1000, 0, 1.0, 1.0, 0.01, 0.01, 0, 0, 0],   # t=1000s, end of fire
    ]

Fire in the first room (references compartment ID and fire data table):

.. code-block:: python

    fire = Fire(
        id="FIRE1",
        comp_id="ROOM1",
        fire_id="POLYURETHANE",
        location=[2.0, 2.0],
        data_table=fire_data
    )

Then we can create the model with all the components and save it to a file:

.. code-block:: python

    model = CFASTModel(
        simulation_environment=SimulationEnvironment(title="Two-Room Fire"),
        compartments=[room1, room2],
        wall_vents=[wall_vent],
        fires=[fire],
        file_name="two_room_fire.in",
    )
    model.save()

Other components (:class:`~pycfast.CeilingFloorVent`, :class:`~pycfast.Device`, :class:`~pycfast.Material`, :class:`~pycfast.MechanicalVent`, :class:`~pycfast.SurfaceConnection`) follow the same pattern and are documented in the :doc:`API reference <api/index>`.

Importing Existing Models
~~~~~~~~~~~~~~~~~~~~~~~~~

You can easily import and work with existing CFAST input files with the :func:`~pycfast.parsers.parse_cfast_file`
function. This will parse the input file and create a :class:`~pycfast.CFASTModel` object that you can modify and
run directly from Python:

.. code-block:: python

    from pycfast.parsers import parse_cfast_file

    model = parse_cfast_file("existing_model.in")

.. note::
   When importing existing models, ensure component names (TITLE, MATERIAL, ID, etc.) contain only alphanumeric characters. Special characters like quotes and slashes may cause parsing issues and will be automatically sanitized when possible.

Running Simulations
~~~~~~~~~~~~~~~~~~~

Once your model is ready, you can inspect the model with the :meth:`~pycfast.CFASTModel.summary` method to get an overview of the components and their parameters:

.. code-block:: python

    print(model.summary())


Then you can run the simulation with the :meth:`~pycfast.CFASTModel.run` method, which will launch the CFAST input file and return a dictionary of :class:`~pandas.DataFrame`
for each output CSV file:

.. code-block:: python

    results = model.run()

Each key corresponds to an output CSV file generated by CFAST:

.. list-table::
   :header-rows: 1
   :widths: 20 80

   * - Key
     - Description
   * - ``'compartments'``
     - Conditions in each compartment over time.
   * - ``'devices'``
     - Measurements from devices/targets over time.
   * - ``'masses'``
     - Mass flow data for each compartment.
   * - ``'vents'``
     - Flow data for each vent over time.
   * - ``'walls'``
     - Heat transfer data for each wall over time.
   * - ``'zone'``
     - Zone-specific data.
   * - ``'diagnostics'``
     - Diagnostic information (only present if the input file contains ``&DIAG``).

Results can then be analyzed directly as :class:`~pandas.DataFrame` objects:

.. code-block:: python

    df_compartments = results['compartments']
    df_devices = results['devices']

Modifying Models
~~~~~~~~~~~~~~~~

PyCFAST provides flexible methods to modify your models dynamically.

You can add new components with the :meth:`~pycfast.CFASTModel.add` method:

.. code-block:: python

    new_compartment = Compartment(...)
    model = model.add(new_compartment)

Or you can update existing components (by index or ID) with the
``update_*_params`` methods:

.. code-block:: python

    model = model.update_fire_params(fire="FIRE1", heat_of_combustion=20000)

These methods allow you to perform parametric studies and provide smooth integration with the broader Python ecosystem.

Next Steps
~~~~~~~~~~

This quick guide covers the fundamental concepts of PyCFAST to help you start building and running fire simulations effectively.

For comprehensive documentation of all available classes, methods, and their parameters, explore the :doc:`API reference <api/index>`.

To see PyCFAST in different contexts, check out the practical :doc:`examples` that demonstrate real-world applications you can adapt for your specific needs.
