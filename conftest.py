"""Fixtures for testing the pycfast package."""

import numpy as np
import pandas as pd
import pytest

from pycfast.ceiling_floor_vent import CeilingFloorVent
from pycfast.compartment import Compartment
from pycfast.device import Device
from pycfast.fire import Fire
from pycfast.material import Material
from pycfast.mechanical_vent import MechanicalVent
from pycfast.model import CFASTModel
from pycfast.simulation_environment import SimulationEnvironment
from pycfast.surface_connection import SurfaceConnection
from pycfast.wall_vent import WallVent


@pytest.fixture(autouse=True, scope="session")
def add_doctest_namespace(doctest_namespace: dict) -> dict:
    """Populate the doctest namespace."""
    simulation_env = SimulationEnvironment(
        title="Office Fire Simulation", time_simulation=1800
    )
    room1 = Compartment(id="ROOM1", width=5.0, depth=4.0, height=3.0)
    room2 = Compartment(id="ROOM2", width=4.0, depth=3.0, height=2.5)
    concrete = Material(
        id="CONCRETE",
        material="Concrete",
        conductivity=1.0,
        density=2300,
        specific_heat=0.88,
        thickness=0.2,
    )
    gypsum = Material(
        id="GYPSUM",
        material="Gypsum Board",
        conductivity=0.17,
        density=790,
        specific_heat=0.9,
        thickness=0.016,
    )
    door = WallVent(
        id="DOOR1",
        comps_ids=["ROOM1", "ROOM2"],
        bottom=0.0,
        height=2.0,
        width=0.9,
        face="RIGHT",
    )
    ceiling_vent = CeilingFloorVent(
        id="CEILING1",
        comps_ids=["ROOM1", "ROOM2"],
        area=1.0,
    )
    mech_vent = MechanicalVent(
        id="FAN1",
        comps_ids=["OUTSIDE", "ROOM1"],
        offsets=[0.0, 1.0],
    )
    fire1 = Fire(
        id="FIRE1",
        comp_id="ROOM1",
        fire_id="POLYURETHANE",
        location=[2.0, 2.0],
    )
    temp_sensor = Device(
        id="TEMP1",
        comp_id="ROOM1",
        location=[1.0, 2.0, 1.5],
        type="HEAT_DETECTOR",
        material_id="",
        setpoint=70.0,
        rti=50.0,
    )
    surface_conn = SurfaceConnection.wall_connection(
        comp_id="ROOM1",
        comp_ids="ROOM2",
        fraction=0.5,
    )
    model = CFASTModel(
        simulation_environment=simulation_env,
        compartments=[room1, room2],
        material_properties=[concrete, gypsum],
        wall_vents=[door],
        ceiling_floor_vents=[ceiling_vent],
        mechanical_vents=[mech_vent],
        fires=[fire1],
        devices=[temp_sensor],
        surface_connections=[surface_conn],
    )

    doctest_namespace["model"] = model
    doctest_namespace["CFASTModel"] = CFASTModel
    doctest_namespace["SimulationEnvironment"] = SimulationEnvironment
    doctest_namespace["Compartment"] = Compartment
    doctest_namespace["Material"] = Material
    doctest_namespace["WallVent"] = WallVent
    doctest_namespace["CeilingFloorVent"] = CeilingFloorVent
    doctest_namespace["MechanicalVent"] = MechanicalVent
    doctest_namespace["Fire"] = Fire
    doctest_namespace["Device"] = Device
    doctest_namespace["SurfaceConnection"] = SurfaceConnection
    doctest_namespace["np"] = np
    doctest_namespace["pd"] = pd
    doctest_namespace["simulation_env"] = simulation_env
    doctest_namespace["room1"] = room1
    doctest_namespace["room2"] = room2
    doctest_namespace["concrete"] = concrete
    doctest_namespace["gypsum"] = gypsum
    doctest_namespace["door"] = door
    doctest_namespace["fire1"] = fire1
    doctest_namespace["temp_sensor"] = temp_sensor

    return doctest_namespace
