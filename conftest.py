"""Root pytest configuration.

Enables doctest validation for all modules under ``src/pycfast/`` via
``--doctest-modules``. The fixtures defined here inject common imports and
pre-built example objects into the doctest namespace so that docstring
examples remain concise without having to repeat boilerplate setup.

Placed at the repository root so fixtures reach both the ``tests/`` tree and
the ``src/pycfast/`` modules collected by ``--doctest-modules``. A conftest
inside ``tests/`` would not cover doctests collected from source files.
"""

from __future__ import annotations

import shutil
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

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
from pycfast.parsers.cfast_parser import CFASTParser
from pycfast.utils.namelist import NamelistRecord

DOCTEST_FIXTURES_DIR = Path(__file__).parent / "tests" / "fixtures" / "doctest"


def _build_runnable_model(tmp_path: Path) -> CFASTModel:
    """Build a CFAST model that covers every component type used in doctests."""
    simulation_env = SimulationEnvironment(
        title="Doctest Simulation",
        time_simulation=60,
        print=30,
        smokeview=30,
        spreadsheet=30,
    )
    gypsum = Material(
        id="GYPSUM",
        material="Gypsum Board",
        conductivity=0.16,
        density=790,
        specific_heat=0.9,
        thickness=0.016,
        emissivity=0.9,
    )
    room1 = Compartment(
        id="ROOM1",
        width=3.0,
        depth=4.0,
        height=2.4,
        ceiling_mat_id="GYPSUM",
        ceiling_thickness=0.016,
        wall_mat_id="GYPSUM",
        wall_thickness=0.016,
    )
    room2 = Compartment(
        id="ROOM2",
        width=3.0,
        depth=4.0,
        height=2.4,
        ceiling_mat_id="GYPSUM",
        ceiling_thickness=0.016,
        wall_mat_id="GYPSUM",
        wall_thickness=0.016,
        origin_x=3.0,
    )
    wall_vent = WallVent(
        id="DOOR1",
        comps_ids=["ROOM1", "ROOM2"],
        bottom=0.0,
        height=2.0,
        width=0.9,
        face="RIGHT",
    )
    cf_vent = CeilingFloorVent(
        id="HATCH1",
        comps_ids=["ROOM1", "ROOM2"],
        area=0.5,
    )
    mech_vent = MechanicalVent(
        id="FAN1",
        comps_ids=["ROOM1", "OUTSIDE"],
        flow=0.1,
    )
    device = Device(
        id="TARGET1",
        comp_id="ROOM1",
        location=[1.5, 2.0, 1.0],
        type="PLATE",
        material_id="GYPSUM",
        normal=[0, 0, 1],
    )
    surface_conn = SurfaceConnection.wall_connection(
        comp_id="ROOM1",
        comp_ids="ROOM2",
        fraction=0.5,
    )
    fire = Fire(
        id="FIRE1",
        comp_id="ROOM1",
        fire_id="POLYURETHANE",
        location=[1.5, 2.0],
        carbon=1,
        hydrogen=4,
        heat_of_combustion=50000,
        radiative_fraction=0.35,
        data_table=[
            [0, 0, 0.0, 0.1, 0.01, 0.01, 0, 0, 0],
            [30, 50, 0.5, 0.5, 0.01, 0.01, 0, 0, 0],
            [60, 100, 0.5, 0.5, 0.01, 0.01, 0, 0, 0],
        ],
    )
    return CFASTModel(
        simulation_environment=simulation_env,
        compartments=[room1, room2],
        material_properties=[gypsum],
        wall_vents=[wall_vent],
        ceiling_floor_vents=[cf_vent],
        mechanical_vents=[mech_vent],
        devices=[device],
        surface_connections=[surface_conn],
        fires=[fire],
        file_name=str(tmp_path / "doctest.in"),
    )


@pytest.fixture(autouse=True)
def _doctest_namespace(doctest_namespace, tmp_path):
    """Inject common symbols into the doctest namespace.

    Adds the public PyCFAST API plus ``pd``, ``np`` so docstring examples
    can remain focused on the behaviour being illustrated. A pre-built
    runnable ``model`` and a path to a reference ``.in`` fixture are also
    exposed for the few examples that exercise ``CFASTModel.run()`` or
    parsing.
    """
    doctest_namespace["pd"] = pd
    doctest_namespace["np"] = np
    doctest_namespace["Path"] = Path
    doctest_namespace["tmp_path"] = tmp_path
    doctest_namespace["CFASTModel"] = CFASTModel
    doctest_namespace["SimulationEnvironment"] = SimulationEnvironment
    doctest_namespace["Compartment"] = Compartment
    doctest_namespace["Material"] = Material
    doctest_namespace["Fire"] = Fire
    doctest_namespace["Device"] = Device
    doctest_namespace["WallVent"] = WallVent
    doctest_namespace["CeilingFloorVent"] = CeilingFloorVent
    doctest_namespace["MechanicalVent"] = MechanicalVent
    doctest_namespace["SurfaceConnection"] = SurfaceConnection
    doctest_namespace["CFASTParser"] = CFASTParser
    doctest_namespace["NamelistRecord"] = NamelistRecord
    doctest_namespace["model"] = _build_runnable_model(tmp_path)
    doctest_namespace["example_in_path"] = str(DOCTEST_FIXTURES_DIR / "example.in")


def pytest_collection_modifyitems(config, items):
    """Skip doctests that need the CFAST binary when it is not installed."""
    if shutil.which("cfast") is not None:
        return
    skip_cfast = pytest.mark.skip(reason="CFAST binary not installed")
    for item in items:
        nodeid = item.nodeid
        if "CFASTModel.run" in nodeid or nodeid.endswith("model.CFASTModel"):
            item.add_marker(skip_cfast)
