"""
PyCFAST: Python interface for CFAST fire modeling software.

This package provides a Python interface for creating, configuring, and running
CFAST (Consolidated Fire and Smoke Transport) simulations. CFAST is a fire modeling
software developed by NIST for simulating fire growth and smoke transport in
compartmentalized structures.
"""

from __future__ import annotations

from importlib.metadata import version

from .ceiling_floor_vents import CeilingFloorVents
from .compartments import Compartments
from .devices import Devices
from .fires import Fires
from .material_properties import MaterialProperties
from .mechanical_vents import MechanicalVents
from .model import CFASTModel
from .simulation_environment import SimulationEnvironment
from .surface_connections import SurfaceConnections
from .wall_vents import WallVents

__all__ = [
    "CeilingFloorVents",
    "Compartments",
    "Devices",
    "Fires",
    "MaterialProperties",
    "MechanicalVents",
    "CFASTModel",
    "SimulationEnvironment",
    "SurfaceConnections",
    "WallVents",
]

__version__ = version("pycfast")
__author__ = "WYGAS Benoît"
