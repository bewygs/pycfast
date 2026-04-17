"""
PyCFAST: Python interface for CFAST fire modeling software.

This package provides a Python interface for creating, configuring, and running
CFAST (Consolidated Fire and Smoke Transport) simulations. CFAST is a fire modeling
software developed by NIST for simulating fire growth and smoke transport in
compartmentalized structures.
"""

from __future__ import annotations

import logging
from importlib.metadata import version

from . import datasets
from .ceiling_floor_vent import CeilingFloorVent
from .compartment import Compartment
from .device import Device
from .fire import Fire
from .material import Material
from .mechanical_vent import MechanicalVent
from .model import CFASTModel
from .simulation_environment import SimulationEnvironment
from .surface_connection import SurfaceConnection
from .wall_vent import WallVent

logging.getLogger("pycfast").addHandler(logging.NullHandler())

__all__ = [
    "datasets",
    "CFAST_VERSION",
    "CeilingFloorVent",
    "Compartment",
    "Device",
    "Fire",
    "Material",
    "MechanicalVent",
    "CFASTModel",
    "SimulationEnvironment",
    "SurfaceConnection",
    "WallVent",
]

__version__ = version("pycfast")
__author__ = "WYGAS Benoît"

CFAST_VERSION = [
    "7.7.5",
    "7.7.4",
    "7.7.3",
    "7.7.2",
    "7.7.1",
    "7.7.0",
]  # CFAST versions that pycfast is compatible with
