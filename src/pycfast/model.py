"""
CFAST model creation and execution module.

This module provides the main CFASTModel class for creating, configuring,
and executing CFAST fire simulations through a Python interface.
"""

from __future__ import annotations

import copy
import logging
import os
import shutil
import subprocess
import warnings
from collections.abc import Generator
from pathlib import Path
from typing import Any, cast

import numpy as np
import pandas as pd

from ._base_component import CFASTComponent
from .ceiling_floor_vent import CeilingFloorVent
from .compartment import Compartment
from .device import Device
from .fire import Fire
from .material import Material
from .mechanical_vent import MechanicalVent
from .simulation_environment import SimulationEnvironment
from .surface_connection import SurfaceConnection
from .utils import CSV_READ_CONFIGS
from .wall_vent import WallVent

logger = logging.getLogger("pycfast")

# Table used for mapping component types to their identifiers, useful for intenal method
# that update or add component to the model.
#
# Format: component_key: (model_attribute, display_label, identifier_fields)
#
# component_key is used internally to acces the table in private methods,
# model_attribute is the corresponding attribute of the CFASTModel class,
# display_label is used for error messages and logging
# identifier_fields are the fields used to identify components and update it
#
# fmt: off
_COMPONENT_SPECS = {
    "fire":         ("fires",               "Fire",               ("id", "fire_id")),
    "compartment":  ("compartments",        "Compartment",        ("id",)),
    "material":     ("material_properties", "Material",           ("id",)),
    "wall_vent":    ("wall_vents",          "Wall vent",          ("id",)),
    "cf_vent":      ("ceiling_floor_vents", "Ceiling/floor vent", ("id",)),
    "mech_vent":    ("mechanical_vents",    "Mechanical vent",    ("id",)),
    "device":       ("devices",             "Device",             ("id",)),
    "surface_conn": ("surface_connections", "Surface connection", ()),
}
# fmt: on


def _resolve_cfast_exe(cfast_exe: str | None = None) -> str:
    """Resolve the CFAST executable path with a fallback chain.

    Resolution order:

    1. Explicit ``cfast_exe`` argument
    2. ``CFAST`` environment variable
    3. ``cfast`` found on the system ``PATH``

    Parameters
    ----------
    cfast_exe : str or None
        Explicit path to the CFAST executable.

    Returns
    -------
    str
        Resolved path to the CFAST executable.

    Raises
    ------
    FileNotFoundError
        If no CFAST executable can be found.
    """
    if cfast_exe:
        return cfast_exe

    env_exe = os.getenv("CFAST")
    if env_exe:
        return env_exe

    system_exe = shutil.which("cfast")
    if system_exe:
        return system_exe

    msg = (
        "CFAST executable not found. Please either:\n"
        "  - Add 'cfast' to your system PATH\n"
        "  - Set the CFAST environment variable\n"
        "  - Pass cfast_exe='/path/to/cfast' to CFASTModel()\n\n"
        "CFAST can be downloaded from: https://pages.nist.gov/cfast/"
    )
    raise FileNotFoundError(msg)


class CFASTModel:
    """
    Main class for creating and running CFAST fire simulations.

    This class handles the creation of CFAST input files from Python objects
    and executes the CFAST simulation, returning results as pandas DataFrames.

    The CFASTModel combines all the necessary components of a fire simulation:
    scenario configuration, compartments, vents, fires, targets, and material
    properties into a single model that can be executed.

    Parameters
    ----------
    simulation_environment: SimulationEnvironment
        Basic simulation parameters and settings
    material_properties: List[Material]
        List of material property definitions
    compartments: List[Compartment]
        List of compartment/room definitions
    wall_vents: List[WallVent]
        List of wall vent connections between compartments
    ceiling_floor_vents: List[CeilingFloorVent]
        List of ceiling/floor vent connections
    mechanical_vents: List[MechanicalVent]
        List of mechanical ventilation systems
    fires: List[Fire]
        List of fire definitions
    targets: List[Device]
        List of target/sensor definitions
    file_name: str
        Name of the CFAST input file to generate
    cfast_exe: str
        Path to the CFAST executable
    extra_arguments: List[str]
        Additional command-line arguments for CFAST

    Examples
    --------
    Create and run a simple fire simulation:

    >>> model = CFASTModel(
    ...     simulation_environment=simulation_env,
    ...     compartments=[room1, room2],
    ...     material_properties=[concrete, gypsum],
    ...     wall_vents=[door],
    ...     fires=[fire1],
    ...     devices=[temp_sensor],
    ...     file_name="simulation.in"
    ... )
    >>> results = model.run()
    >>> print(results['simulation_compartments.csv'].head())

    Create a minimal simulation with just compartments:

    >>> minimal_model = CFASTModel(
    ...     scenario_configuration=scenario_config,
    ...     compartments=[room1]
    ... )
    >>> results = minimal_model.run()
    """

    def __init__(
        self,
        simulation_environment: SimulationEnvironment,
        compartments: list[Compartment],
        material_properties: list[Material] | None = None,
        wall_vents: list[WallVent] | None = None,
        ceiling_floor_vents: list[CeilingFloorVent] | None = None,
        mechanical_vents: list[MechanicalVent] | None = None,
        fires: list[Fire] | None = None,
        devices: list[Device] | None = None,
        surface_connections: list[SurfaceConnection] | None = None,
        file_name: str = "cfast_input.in",
        cfast_exe: str | None = None,
        extra_arguments: list[str] | None = None,
    ):
        self.simulation_environment = simulation_environment
        self.material_properties = material_properties or []
        self.compartments = compartments
        self.wall_vents = wall_vents or []
        self.ceiling_floor_vents = ceiling_floor_vents or []
        self.mechanical_vents = mechanical_vents or []
        self.fires = fires or []
        self.devices = devices or []
        self.surface_connections = surface_connections or []
        self.file_name = file_name
        self.cfast_exe = cfast_exe
        self.extra_arguments = extra_arguments or []
        self._input_written = False

        self._validate_dependencies()

    def __repr__(self) -> str:
        """Return a detailed string representation of the CFASTModel."""
        components = [
            f"compartments={len(self.compartments)}",
            f"fires={len(self.fires)}",
            f"wall_vents={len(self.wall_vents)}",
            f"ceiling_floor_vents={len(self.ceiling_floor_vents)}",
            f"mechanical_vents={len(self.mechanical_vents)}",
            f"devices={len(self.devices)}",
            f"material_properties={len(self.material_properties)}",
            f"surface_connections={len(self.surface_connections)}",
        ]

        return f"CFASTModel(file_name='{self.file_name}', {', '.join(components)})"

    def __str__(self) -> str:
        """Return a detailed string representation of the CFASTModel."""
        return self.summary()

    def __iter__(self) -> Generator[tuple[str, Any], None, None]:
        """Iterate over all components in the model."""
        component_types = [
            ("compartments", self.compartments),
            ("fires", self.fires),
            ("wall_vents", self.wall_vents),
            ("ceiling_floor_vents", self.ceiling_floor_vents),
            ("mechanical_vents", self.mechanical_vents),
            ("devices", self.devices),
            ("material_properties", self.material_properties),
            ("surface_connections", self.surface_connections),
        ]

        for component_type, components in component_types:
            if components:
                yield component_type, components

    def __getitem__(self, key: str) -> Any:
        """Get component list by name for dictionary-like access."""
        if not hasattr(self, key):
            raise KeyError(f"Property '{key}' not found in CFASTModel.")
        return getattr(self, key)

    def __setitem__(self, key: str, value: Any) -> None:
        """Set component list by name for dictionary-like assignment."""
        if not hasattr(self, key):
            raise KeyError(
                f"Cannot set '{key}'. Property does not exist in CFASTModel."
            )
        setattr(self, key, value)

    def run(
        self,
        file_name: str | None = None,
        timeout: int | float | None = None,
        verbose: bool = False,
    ) -> dict[str, pd.DataFrame]:
        """
        Execute the CFAST simulation and return results.

        This method writes the input file, runs CFAST, and reads the output
        CSV files into pandas DataFrames. The simulation creates several
        output files with different types of data.

        Parameters
        ----------
        file_name: str, optional
            Optional filename/path for this specific run. If provided,
            temporarily overrides the model's file_name for this execution only.
            The model's original file_name remains unchanged. Useful for batch
            processing, sensitivity analysis, or saving runs with descriptive names.
        timeout: int | float, optional
            Maximum time in seconds to allow for CFAST execution. If the
            execution exceeds this time, it will be terminated. If None,
            no timeout will be applied.
        verbose: bool, optional
            If True, logs CFAST stdout and stderr at DEBUG level.

        Returns
        -------
        dict[str, pd.DataFrame]
            Dictionary mapping CSV filenames to pandas DataFrames containing
            simulation results. Keys include:
            - 'compartments': Compartment conditions over time
            - 'devices': Device/target measurements
            - 'masses': Mass flow data
            - 'vents': Vent flow data
            - 'walls': Wall heat transfer data
            - 'zone': Zone-specific data
            - 'diagnostics': Diagnostic information (if generated with &DIAG)

            Returns None if simulation fails.

        Raises
        ------
        subprocess.CalledProcessError:
            If CFAST execution fails
        FileNotFoundError:
            If CFAST executable is not found
        pd.errors.ParserError:
            If output CSV files cannot be parsed

        Warns
        -----
        RuntimeWarning
            If CFAST execution exceeds the timeout, or if an expected output
            CSV file is missing, empty, or cannot be read.

        Examples
        --------
        >>> results = model.run()
        >>> if results:
        ...     temp_data = results['simulation_compartments.csv']
        ...     print(f"Max temperature: {temp_data['CEILT'].max()}")

        >>> # Run with custom filename for sensitivity analysis
        >>> results = model.run(file_name="sensitivity_case_1.in")
        """
        original_file_name = self.file_name
        if file_name is not None:
            self.file_name = file_name

        try:
            input_file_path = self._write_input()
            cfast_exe = _resolve_cfast_exe(self.cfast_exe)
            # cfast and its input files need to be in the same directory
            # otherwise there is a weird error where only "_zone.csv" is generated
            cwd = os.path.dirname(input_file_path)

            try:
                result = subprocess.run(
                    [
                        cfast_exe,
                        Path(input_file_path).stem,
                        *self.extra_arguments,
                    ],
                    check=True,
                    capture_output=True,
                    text=True,
                    cwd=str(cwd),
                    timeout=timeout,
                )
                if verbose:
                    logger.debug("CFAST stdout:\n%s", result.stdout)
                    logger.debug("CFAST stderr:\n%s", result.stderr)
            except subprocess.CalledProcessError as e:
                error_msg = f"CFAST execution failed with return code {e.returncode}"
                log_content = self._get_log()
                if log_content:
                    error_msg += f"\n\nCFAST log output:\n{log_content}"
                if e.stderr:
                    error_msg += f"\n\nCFAST stderr:\n{e.stderr}"
                raise subprocess.CalledProcessError(
                    e.returncode, e.cmd, output=e.stdout, stderr=error_msg
                ) from e

            except subprocess.TimeoutExpired:
                warnings.warn(
                    f"CFAST execution exceeded timeout of {timeout} seconds. Attempting to read available output files.",
                    RuntimeWarning,
                    stacklevel=2,
                )
            dataframes = {}
            base_name = str(Path(self.file_name).with_suffix(""))

            optional_csvs = {"diagnostics"}
            for suffix, read_params in CSV_READ_CONFIGS.items():
                csv_file = base_name + "_" + suffix + ".csv"
                if os.path.exists(csv_file):
                    try:
                        read_args = {
                            k: v for k, v in read_params.items() if v is not None
                        }
                        df = pd.read_csv(csv_file, **read_args)  # type: ignore[call-overload]
                        dataframes[suffix] = df
                    except pd.errors.EmptyDataError:
                        warnings.warn(
                            f"Output CSV is empty: {csv_file}",
                            RuntimeWarning,
                            stacklevel=2,
                        )
                        dataframes[suffix] = pd.DataFrame()
                        continue
                    except Exception as e:
                        warnings.warn(
                            f"Failed to read CSV file: {csv_file}. Error: {e}",
                            RuntimeWarning,
                            stacklevel=2,
                        )
                        dataframes[suffix] = None
                else:
                    if suffix not in optional_csvs:
                        warnings.warn(
                            f"Expected output CSV file not found: {csv_file}",
                            RuntimeWarning,
                            stacklevel=2,
                        )
                    dataframes[suffix] = None

            return dataframes
        finally:
            # Always restore the original file_name
            self.file_name = original_file_name

    def update_fire_params(
        self,
        fire: int | str | None = None,
        data_table: list[list[float]] | np.ndarray | pd.DataFrame | None = None,
        **kwargs: Any,
    ) -> CFASTModel:
        """
        Update fire parameters and return a new model instance.

        Parameters
        ----------
        fire : int | str | None, optional
            Fire identifier. Can be:
            - int: Fire index (0-based)
            - str: "fire_id" or "id" (yes it's different)
            - None: Updates first fire (index 0)
        data_table : list[list[float]], np.ndarray, or pd.DataFrame, optional
            New fire data table to replace existing one. Must have 9 columns:
            TIME, HRR, HEIGHT, AREA, CO_YIELD, SOOT_YIELD, HCN_YIELD, HCL_YIELD, TRACE_YIELD.
        **kwargs : Any
            Fire object attributes to update. See Fire class documentation
            for available parameters.

        Returns
        -------
        CFASTModel
            New model instance with updated fire parameters

        Examples
        --------
        >>> # Update scalar fire properties
        >>> new_model = model.update_fire_params(
        ...     heat_of_combustion=20000,
        ...     radiative_fraction=0.35
        ... )

        >>> # Update fire data table with pandas DataFrame
        >>> fire_data = pd.DataFrame({
        ...     'time': [0, 60, 120],
        ...     'heat_release_rate': [0, 1000, 2000],
        ...     'height': [0.5, 0.5, 0.5],
        ...     'area': [1.0, 1.0, 1.0],
        ...     'co_yield': [0.004, 0.004, 0.004],
        ...     'soot_yield': [0.01, 0.01, 0.01],
        ...     'hcn_yield': [0.0, 0.0, 0.0],
        ...     'hcl_yield': [0.0, 0.0, 0.0],
        ...     'trace_yield': [0.0, 0.0, 0.0]
        ... })
        >>> new_model = model.update_fire_params(data_table=fire_data)

        >>> # Update fire data table with numpy array
        >>> import numpy as np
        >>> fire_array = np.array([
        ...     [0, 0, 0.5, 1.0, 0.004, 0.01, 0.0, 0.0, 0.0],
        ...     [60, 1000, 0.5, 1.0, 0.004, 0.01, 0.0, 0.0, 0.0],
        ...     [120, 2000, 0.5, 1.0, 0.004, 0.01, 0.0, 0.0, 0.0]
        ... ])
        >>> new_model = model.update_fire_params(data_table=fire_array)

        >>> # Update fire data table with list of lists
        >>> fire_list = [
        ...     [0, 0, 0.5, 1.0, 0.004, 0.01, 0.0, 0.0, 0.0],
        ...     [60, 1000, 0.5, 1.0, 0.004, 0.01, 0.0, 0.0, 0.0],
        ...     [120, 2000, 0.5, 1.0, 0.004, 0.01, 0.0, 0.0, 0.0]
        ... ]
        >>> new_model = model.update_fire_params(data_table=fire_list)

        >>> # Update by fire name
        >>> new_model = model.update_fire_params(
        ...     fire="main_fire",
        ...     heat_of_combustion=18000
        ... )
        """
        identifier = fire
        new_model = self._update_component("fire", identifier, **kwargs)

        if data_table is not None:
            if isinstance(data_table, pd.DataFrame):
                coerced = data_table.values.tolist()
            elif isinstance(data_table, np.ndarray):
                coerced = data_table.tolist()
            elif isinstance(data_table, list):
                coerced = data_table
            else:
                raise TypeError(
                    "data_table must be a pandas DataFrame, numpy ndarray, or list of lists"
                )
            idx = (
                self._resolve_identifier("fire", identifier)
                if identifier is not None
                else 0
            )
            new_model.fires[idx].data_table = coerced

        return new_model

    def update_simulation_params(self, **kwargs: Any) -> CFASTModel:
        """
        Update simulation environment parameters and return a new model instance.

        Parameters
        ----------
        **kwargs : Any
            Simulation environment attributes to update. See SimulationEnvironment
            class documentation for available parameters.

        Returns
        -------
        CFASTModel
            New model instance with updated simulation parameters

        Examples
        --------
        >>> new_model = model.update_simulation_params(
        ...     time_simulation=1800,
        ...     print=10,
        ...     interior_temperature=25.0
        ... )
        """
        new_model = copy.deepcopy(self)
        if getattr(new_model, "simulation_environment", None) is None:
            raise ValueError("Model has no simulation_environment object")

        self._apply_kwargs(
            new_model.simulation_environment, "Simulation environment", kwargs
        )
        return new_model

    def update_compartment_params(
        self,
        compartment: int | str | None = None,
        **kwargs: Any,
    ) -> CFASTModel:
        """
        Update compartment parameters and return a new model instance.

        Parameters
        ----------
        compartment : int | str | None, optional
            Compartment identifier. Can be:
            - int: Compartment index (0-based)
            - str: Compartment id
            - None: Updates first compartment (index 0)
        **kwargs : Any
            Compartment attributes to update. See Compartment class documentation
            for available parameters.

        Returns
        -------
        CFASTModel
            New model instance with updated compartment parameters

        Examples
        --------
        >>> new_model = model.update_compartment_params(
        ...     width=5.0,
        ...     height=3.0,
        ...     compartment=1
        ... )

        >>> new_model = model.update_compartment_params(
        ...     compartment="living_room",
        ...     width=6.0
        ... )
        """
        identifier = compartment
        return self._update_component("compartment", identifier, **kwargs)

    def update_material_params(
        self,
        material: int | str | None = None,
        **kwargs: Any,
    ) -> CFASTModel:
        """
        Update material properties parameters and return a new model instance.

        Parameters
        ----------
        material : int | str | None, optional
            Material identifier. Can be:
            - int: Material index (0-based)
            - str: Material id
            - None: Updates first material (index 0)
        **kwargs : Any
            Material properties attributes to update. See Material class
            documentation for available parameters.

        Returns
        -------
        CFASTModel
            New model instance with updated material parameters

        Examples
        --------
        >>> new_model = model.update_material_params(
        ...     material="concrete",
        ...     conductivity=1.5,
        ...     density=2300
        ... )
        """
        identifier = material
        return self._update_component("material", identifier, **kwargs)

    def update_wall_vent_params(
        self,
        vent: int | str | None = None,
        **kwargs: Any,
    ) -> CFASTModel:
        """
        Update wall vent parameters and return a new model instance.

        Parameters
        ----------
        vent : int | str | None, optional
            Wall vent identifier. Can be:
            - int: Vent index (0-based)
            - str: Vent id
            - None: Updates first vent (index 0)
        **kwargs : Any
            Wall vent attributes to update. See WallVent class documentation
            for available parameters.

        Returns
        -------
        CFASTModel
            New model instance with updated wall vent parameters

        Examples
        --------
        >>> new_model = model.update_wall_vent_params(
        ...     vent=0,
        ...     width=1.2,
        ...     height=2.0
        ... )
        """
        return self._update_component("wall_vent", vent, **kwargs)

    def update_ceiling_floor_vent_params(
        self,
        vent: int | str | None = None,
        **kwargs: Any,
    ) -> CFASTModel:
        """
        Update ceiling/floor vent parameters and return a new model instance.

        Parameters
        ----------
        vent : int | str | None, optional
            Ceiling/floor vent identifier. Can be:
            - int: Vent index (0-based)
            - str: Vent id
            - None: Updates first vent (index 0)
        **kwargs : Any
            Ceiling/floor vent attributes to update. See CeilingFloorVent class
            documentation for available parameters.

        Returns
        -------
        CFASTModel
            New model instance with updated ceiling/floor vent parameters

        Examples
        --------
        >>> new_model = model.update_ceiling_floor_vent_params(
        ...     vent=0,
        ...     area=0.5
        ... )
        """
        return self._update_component("cf_vent", vent, **kwargs)

    def update_mechanical_vent_params(
        self,
        vent: int | str | None = None,
        **kwargs: Any,
    ) -> CFASTModel:
        """
        Update mechanical vent parameters and return a new model instance.

        Parameters
        ----------
        vent : int | str | None, optional
            Mechanical vent identifier. Can be:
            - int: Vent index (0-based)
            - str: Vent id
            - None: Updates first vent (index 0)
        **kwargs : Any
            Mechanical vent attributes to update. See MechanicalVent class
            documentation for available parameters.

        Returns
        -------
        CFASTModel
            New model instance with updated mechanical vent parameters

        Examples
        --------
        >>> new_model = model.update_mechanical_vent_params(
        ...     vent=0,
        ...     flow_rate=0.5
        ... )
        """
        return self._update_component("mech_vent", vent, **kwargs)

    def update_device_params(
        self,
        device: int | str | None = None,
        **kwargs: Any,
    ) -> CFASTModel:
        """
        Update device/target parameters and return a new model instance.

        Parameters
        ----------
        device : int | str | None, optional
            Device identifier. Can be:
            - int: Device index (0-based)
            - str: Device id
            - None: Updates first device (index 0)
        **kwargs : Any
            Device attributes to update. See Device class documentation
            for available parameters.

        Returns
        -------
        CFASTModel
            New model instance with updated device parameters

        Examples
        --------
        >>> new_model = model.update_device_params(
        ...     device=0,
        ...     location=[2.0, 2.0, 2.4]
        ... )
        """
        return self._update_component("device", device, **kwargs)

    def update_surface_connection_params(
        self,
        connection: int | None = None,
        **kwargs: Any,
    ) -> CFASTModel:
        """
        Update surface connection parameters and return a new model instance.

        Parameters
        ----------
        connection : int | None, optional
            Surface connection identifier. Can be:
            - int: Connection index (0-based)
            - None: Updates first connection (index 0)
        **kwargs : Any
            Surface connection attributes to update. See SurfaceConnection class
            documentation for available parameters.

        Returns
        -------
        CFASTModel
            New model instance with updated surface connection parameters

        Examples
        --------
        >>> new_model = model.update_surface_connection_params(
        ...     connection=0,
        ...     fraction=0.8
        ... )
        """
        return self._update_component("surface_conn", connection, **kwargs)

    def add_fire(self, fire: Fire) -> CFASTModel:
        """
        Add a fire to the model and return a new model instance.

        Parameters
        ----------
        fire : Fire
            Fire object to add to the model

        Returns
        -------
        CFASTModel
            New model instance with the added fire

        Examples
        --------
        >>> new_fire = Fire(id="FIRE2", comp_id="ROOM1", location=[2.0, 2.0])
        >>> updated_model = model.add_fire(new_fire)
        """
        return self._add_component("fire", fire)

    def add_compartment(self, compartment: Compartment) -> CFASTModel:
        """
        Add a compartment to the model and return a new model instance.

        Parameters
        ----------
        compartment : Compartment
            Compartment object to add to the model

        Returns
        -------
        CFASTModel
            New model instance with the added compartment

        Examples
        --------
        >>> new_room = Compartment(id="ROOM3", width=5.0, depth=4.0, height=3.0)
        >>> updated_model = model.add_compartment(new_room)
        """
        return self._add_component("compartment", compartment)

    def add_material(self, material: Material) -> CFASTModel:
        """
        Add a material property to the model and return a new model instance.

        Parameters
        ----------
        material : Material
            Material properties object to add to the model

        Returns
        -------
        CFASTModel
            New model instance with the added material

        Examples
        --------
        >>> steel = Material(id="STEEL", conductivity=45.0, density=7850)
        >>> updated_model = model.add_material(steel)
        """
        return self._add_component("material", material)

    def add_wall_vent(self, vent: WallVent) -> CFASTModel:
        """
        Add a wall vent to the model and return a new model instance.

        Parameters
        ----------
        vent : WallVent
            Wall vent object to add to the model

        Returns
        -------
        CFASTModel
            New model instance with the added wall vent

        Examples
        --------
        >>> door = WallVent(comp_ids=["ROOM1", "ROOM2"], width=1.0, height=2.0)
        >>> updated_model = model.add_wall_vent(door)
        """
        return self._add_component("wall_vent", vent)

    def add_ceiling_floor_vent(self, vent: CeilingFloorVent) -> CFASTModel:
        """
        Add a ceiling/floor vent to the model and return a new model instance.

        Parameters
        ----------
        vent : CeilingFloorVent
            Ceiling/floor vent object to add to the model

        Returns
        -------
        CFASTModel
            New model instance with the added ceiling/floor vent

        Examples
        --------
        >>> hatch = CeilingFloorVent(comp_ids=["ROOM1", "ROOM2"], area=0.5)
        >>> updated_model = model.add_ceiling_floor_vent(hatch)
        """
        return self._add_component("cf_vent", vent)

    def add_mechanical_vent(self, vent: MechanicalVent) -> CFASTModel:
        """
        Add a mechanical vent to the model and return a new model instance.

        Parameters
        ----------
        vent : MechanicalVent
            Mechanical vent object to add to the model

        Returns
        -------
        CFASTModel
            New model instance with the added mechanical vent

        Examples
        --------
        >>> hvac = MechanicalVent(comp_ids=["ROOM1", "OUTSIDE"], flow_rate=0.5)
        >>> updated_model = model.add_mechanical_vent(hvac)
        """
        return self._add_component("mech_vent", vent)

    def add_device(self, device: Device) -> CFASTModel:
        """
        Add a device/target to the model and return a new model instance.

        Parameters
        ----------
        device : Device
            Device object to add to the model

        Returns
        -------
        CFASTModel
            New model instance with the added device

        Examples
        --------
        >>> sensor = Device.create_heat_detector(
        ...     comp_id="ROOM1", location=[2.0, 2.0, 2.4], temperature=68.0
        ... )
        >>> updated_model = model.add_device(sensor)
        """
        return self._add_component("device", device)

    def add_surface_connection(self, connection: SurfaceConnection) -> CFASTModel:
        """
        Add a surface connection to the model and return a new model instance.

        Parameters
        ----------
        connection : SurfaceConnection
            Surface connection object to add to the model

        Returns
        -------
        CFASTModel
            New model instance with the added surface connection

        Examples
        --------
        >>> wall_conn = SurfaceConnection.wall_connection(
        ...     comp_ids=["ROOM1", "ROOM2"], fraction=0.5
        ... )
        >>> updated_model = model.add_surface_connection(wall_conn)
        """
        return self._add_component("surface_conn", connection)

    def _resolve_identifier(self, kind: str, identifier: int | str) -> int:
        """Resolve an identifier (index or id string) against a component list."""
        attr, label, id_fields = _COMPONENT_SPECS[kind]

        if isinstance(identifier, int):
            return identifier

        if isinstance(identifier, str):
            for idx, item in enumerate(getattr(self, attr)):
                if any(getattr(item, f, None) == identifier for f in id_fields):
                    return idx
            field_label = "/".join(id_fields) if id_fields else "id"
            raise ValueError(f"No {label} found with {field_label} '{identifier}'")

        raise TypeError(
            f"{label} identifier must be int or str, got {type(identifier)}"
        )

    def _update_component(
        self,
        kind: str,
        identifier: int | str | None = None,
        **kwargs: Any,
    ) -> CFASTModel:
        """Update a component's attributes and return a new model instance.

        Deep-copies the model, locates the target component by identifier
        (defaulting to index 0), applies the kwargs, and returns the new model.
        Backs every ``update_X_params`` public method.
        """
        attr, label, _ = _COMPONENT_SPECS[kind]
        new_model = copy.deepcopy(self)
        coll = getattr(new_model, attr)
        if not coll:
            raise ValueError(f"Model has no {label} to update")

        idx = (
            self._resolve_identifier(kind, identifier) if identifier is not None else 0
        )
        if idx >= len(coll):
            raise IndexError(
                f"{label} index {idx} is out of range. Model has {len(coll)} {label}."
            )

        self._apply_kwargs(coll[idx], label, kwargs)
        return new_model

    def _add_component(self, kind: str, component: Any) -> CFASTModel:
        """Append a component to the relevant list and return a new model."""
        attr, _, _ = _COMPONENT_SPECS[kind]
        new_model = copy.deepcopy(self)
        getattr(new_model, attr).append(component)
        return new_model

    def _apply_kwargs(
        self, target: CFASTComponent, label: str, kwargs: dict[str, Any]
    ) -> None:
        """Apply ``kwargs`` to ``target`` via setattr, raising on unknown params."""
        for param, value in kwargs.items():
            if not hasattr(target, param):
                available = self._get_available_attributes(target)
                raise ValueError(
                    f"{label} has no parameter '{param}'. "
                    f"Available parameters: {', '.join(available)}"
                )
            setattr(target, param, value)
        target._validate()

    def _get_available_attributes(self, obj: Any) -> list[str]:
        """Get list of available non-private, non-callable attributes."""
        return [
            attr
            for attr in dir(obj)
            if not attr.startswith("_") and not callable(getattr(obj, attr))
        ]

    def save(self, file_name: str | None = None) -> str:
        """
        Save the CFAST input file and return its absolute path.

        Parameters
        ----------
        file_name: str, optional
            filename/path for this specific save operation.
            If provided, temporarily overrides the model's file_name for this
            save only. The model's original file_name remains unchanged.
            Useful for creating backups, saving variants, or organizing
            output files.

        Returns
        -------
        str
            Absolute path to the saved input file.

        Examples
        --------
        >>> # Save with default filename
        >>> path = model.save()

        >>> # Save backup without changing model's file_name
        >>> backup_path = model.save(file_name="backup/model_v1.in")
        """
        original_file_name = self.file_name
        if file_name is not None:
            self.file_name = file_name

        try:
            abs_input_file_path = self._write_input()
            return abs_input_file_path
        finally:
            self.file_name = original_file_name

    def summary(self) -> str:
        """
        Return a clear summary of the CFAST model configuration as a string.

        Shows the model info and all components with their current parameter values
        using each component's string representation.

        Returns
        -------
        str
            Formatted summary of the model configuration.

        Examples
        --------
        >>> print(model.summary())
        Model: my_simulation.in
        Simulation: 'Building Fire Test' (3600s)

        Material Properties (2):
            Material(material='GYPSUM', conductivity=0.17, density=800...)

        Compartment (2):
            Compartment(id='ROOM1', width=4.0, depth=3.0, height=2.5...)
        """
        lines: list[str] = []

        lines.append(f"\nModel: {self.file_name}")
        lines.append(
            f"Simulation: '{self.simulation_environment.title}' ({self.simulation_environment.time_simulation}s)"
        )
        lines.append("\nComponents:")

        if self.material_properties:
            lines.append(f"  Material Properties ({len(self.material_properties)}):")
            for mat in self.material_properties:
                lines.append(f"    {mat}")

        if self.compartments:
            lines.append(f"  Compartment ({len(self.compartments)}):")
            for comp in self.compartments:
                lines.append(f"    {comp}")

        if self.wall_vents:
            lines.append(f"  Wall Vents ({len(self.wall_vents)}):")
            for wall_vent in self.wall_vents:
                lines.append(f"    {wall_vent}")

        if self.ceiling_floor_vents:
            lines.append(f"  Ceiling/Floor Vents ({len(self.ceiling_floor_vents)}):")
            for ceiling_floor_vent in self.ceiling_floor_vents:
                lines.append(f"    {ceiling_floor_vent}")

        if self.mechanical_vents:
            lines.append(f"  Mechanical Vents ({len(self.mechanical_vents)}):")
            for mechanical_vent in self.mechanical_vents:
                lines.append(f"    {mechanical_vent}")

        if self.fires:
            lines.append(f"  Fire ({len(self.fires)}):")
            for fire in self.fires:
                lines.append(f"    {fire}")

        if self.devices:
            lines.append(f"  Device ({len(self.devices)}):")
            for device in self.devices:
                lines.append(f"    {device}")

        if self.surface_connections:
            lines.append(f"  Surface Connections ({len(self.surface_connections)}):")
            for conn in self.surface_connections:
                lines.append(f"    {conn}")

        return "\n".join(lines)

    def view_cfast_input_file(self, pretty_print: bool = True) -> str:
        """
        View the contents of the CFAST input file as a string, with optional pretty formatting.

        Parameters
        ----------
        pretty_print: bool, optional
            If True (default), returns a formatted
            string with line numbers and bold section headers for improved
            readability in the terminal. If False, returns the raw input file
            contents as a plain string.

        Notes
        -----
        Use print() to display the formatted content properly:
        print(model.view_cfast_input_file())

        Returns
        -------
        str
            Contents of the input file

        Raises
        ------
        RuntimeError:
            If the input file has not been generated yet (call save() or
            run() first).

        Examples
        --------
        >>> print(model.view_cfast_input_file())  # Pretty-printed with line numbers
        >>> content = model.view_cfast_input_file(pretty_print=False)  # Raw content
        >>> print(content)
        """
        if not self._input_written:
            raise RuntimeError(
                "CFAST input file has not been generated yet. "
                "Call save() or run() before viewing the input file."
            )

        if pretty_print:
            lines = self._written_content.splitlines()
            pretty_lines = []
            for idx, line in enumerate(lines, 1):
                if line.strip().startswith("!!") or line.strip().startswith("&"):
                    pretty_line = f"\033[1m{idx:4d}: {line}\033[0m"  # bold
                else:
                    pretty_line = f"{idx:4d}: {line}"
                pretty_lines.append(pretty_line)
            pretty_content = "\n".join(pretty_lines)
            return pretty_content
        else:
            return self._written_content

    def _get_log(self) -> str:
        """
        Read and return the contents of the CFAST log file.

        The log file contains detailed information about the simulation
        execution, including any warnings or errors that occurred.

        Returns
        -------
        str
            Contents of the log file as a string.

        Raises
        ------
        FileNotFoundError:
            If log file doesn't exist
        IOError:
            If log file cannot be read
        """
        log_file_path = Path(self.file_name).with_suffix(".log")
        with open(log_file_path) as f:
            return f.read()

    def _write_input(self) -> str:
        """
        Generate and write the CFAST input file.

        This method creates a properly formatted CFAST input file by
        combining all the model components (scenario configuration,
        compartments, vents, fires, etc.) into the required format.

        The input file follows the CFAST namelist format with sections for:
        - Header and scenario configuration
        - Material properties
        - Compartment definitions
        - Vent definitions (wall, ceiling/floor, mechanical)
        - Fire definitions
        - Target/sensor definitions

        Returns
        -------
        str
            Path to the created input file.

        Raises
        ------
        IOError:
            If file cannot be written
        PermissionError:
            If write permission is denied

        Notes
        -----
        The file is written to the current working directory unless
        an absolute path is specified in file_name.
        """
        abs_input_file_path = os.path.abspath(self.file_name)
        content_parts = []

        try:
            content_parts.append(self.simulation_environment.to_input_string())

            sections = [
                ("!! Material Properties", self.material_properties),
                ("!! Compartments", self.compartments),
                ("!! Wall Vents", self.wall_vents),
                ("!! Ceiling and Floor Vents", self.ceiling_floor_vents),
                ("!! Mechanical Vents", self.mechanical_vents),
                ("!! Fire", self.fires),
                ("!! Device", self.devices),
                ("!! Surface Connections", self.surface_connections),
            ]

            for header, items in sections:
                content_parts.extend(["\n", f"{header}\n"])
                if items:
                    # Cast items to list to help mypy understand it's iterable
                    items_list = cast(list[Any], items)
                    content_parts.extend(item.to_input_string() for item in items_list)

            content_parts.extend(["\n", "&TAIL /\n"])

            full_content = "".join(content_parts)
            with open(abs_input_file_path, "w", encoding="utf-8") as f:
                f.write(full_content)

            self._written_content = full_content
            self._input_written = True

        except OSError as e:
            raise OSError(
                f"Failed to write CFAST input file to {abs_input_file_path}: {e}"
            ) from e

        return abs_input_file_path

    def _validate_dependencies(self) -> None:
        """
        Validate all component dependencies and CFAST compatibility constraints.

        - Duplicate ``id`` within any component list (compartments, fires, devices,
          wall/ceiling-floor/mechanical vents, material properties).
        - More than 100 compartments (hard CFAST limit).
        - ``comp_id`` of a fire, device, vent, or surface connection referencing an
          undefined compartment (``"OUTSIDE"`` is accepted as second compartment for
          wall vents).
        - ``material_id`` of a device or compartment surface (ceiling/wall/floor)
          referencing an undefined material.
        - ``device_id`` of a fire or vent referencing an undefined device.
        - Fire or device ``location`` outside the bounds of its compartment.

        Raises
        ------
        ValueError
            If any cross-component constraint is violated (would crash CFAST).

        Warns
        -----
        UserWarning
            If a fire or device position is outside its compartment's dimensions
            (suspicious but not always wrong).
        """
        if len(self.compartments) > 100:
            raise ValueError(
                f"CFAST supports a maximum of 100 compartments, got {len(self.compartments)}."
            )

        # Duplicate IDs within each component type
        check_lists: list[tuple[str, list[Any]]] = [
            ("compartments", self.compartments),
            ("fires", self.fires),
            ("devices", self.devices),
            ("wall_vents", self.wall_vents),
            ("ceiling_floor_vents", self.ceiling_floor_vents),
            ("mechanical_vents", self.mechanical_vents),
            ("material_properties", self.material_properties),
        ]
        for label, items in check_lists:
            seen: set[str] = set()
            for item in items:
                if item.id in seen:
                    raise ValueError(f"Duplicate id '{item.id}' found in {label}.")
                seen.add(item.id)

        comp_ids = {c.id for c in self.compartments}
        material_ids = {m.id for m in self.material_properties}
        device_ids = {d.id for d in self.devices}

        # comp_id of Fire/Device must exist in compartments
        for fire in self.fires:
            if fire.comp_id not in comp_ids:
                raise ValueError(
                    f"Fire '{fire.id}': comp_id='{fire.comp_id}' does not match any defined compartment."
                )

        for device in self.devices:
            if device.comp_id not in comp_ids:
                raise ValueError(
                    f"Device '{device.id}': comp_id='{device.comp_id}' does not match any defined compartment."
                )

        # comps_ids of vents must exist in compartments ("OUTSIDE" is valid as second comp for WallVent)
        for vent in self.wall_vents:
            if vent.comps_ids[0] not in comp_ids:
                raise ValueError(
                    f"WallVent '{vent.id}': comps_ids[0]='{vent.comps_ids[0]}' does not match any defined compartment."
                )
            if vent.comps_ids[1] != "OUTSIDE" and vent.comps_ids[1] not in comp_ids:
                raise ValueError(
                    f"WallVent '{vent.id}': comps_ids[1]='{vent.comps_ids[1]}' does not match any defined compartment."
                )

        for cf_vent in self.ceiling_floor_vents:
            for i, cid in enumerate(cf_vent.comps_ids):
                if cid != "OUTSIDE" and cid not in comp_ids:
                    raise ValueError(
                        f"CeilingFloorVent '{cf_vent.id}': comps_ids[{i}]='{cid}' does not match any defined compartment."
                    )

        for m_vent in self.mechanical_vents:
            for i, cid in enumerate(m_vent.comps_ids):
                if cid != "OUTSIDE" and cid not in comp_ids:
                    raise ValueError(
                        f"MechanicalVent '{m_vent.id}': comps_ids[{i}]='{cid}' does not match any defined compartment."
                    )

        # comp_id of SurfaceConnection must exist in compartments
        for sc in self.surface_connections:
            if sc.comp_id not in comp_ids:
                raise ValueError(
                    f"SurfaceConnection: comp_id='{sc.comp_id}' does not match any defined compartment."
                )
            if sc.comp_ids not in comp_ids:
                raise ValueError(
                    f"SurfaceConnection: comp_ids='{sc.comp_ids}' does not match any defined compartment."
                )

        material_map = {m.id: m for m in self.material_properties}

        # material_id of Device/Compartment must exist in material_properties
        for device in self.devices:
            m_id = getattr(device, "material_id", None)
            if m_id is not None and m_id not in material_ids:
                raise ValueError(
                    f"Device '{device.id}': material_id='{m_id}' does not match any defined material."
                )
            if (
                m_id is not None
                and m_id in material_map
                and device.type in {"PLATE", "CYLINDER"}
                and getattr(device, "depth_units", None) == "M"
                and device.temperature_depth is not None
                and device.temperature_depth >= material_map[m_id].thickness
            ):
                raise ValueError(
                    f"Device '{device.id}': temperature_depth={device.temperature_depth} m must be less than "
                    f"material '{m_id}' thickness={material_map[m_id].thickness} m."
                )

        for comp in self.compartments:
            for attr in ("ceiling_mat_id", "wall_mat_id", "floor_mat_id"):
                m_id = getattr(comp, attr, None)
                if m_id is not None and m_id != "OFF" and m_id not in material_ids:
                    raise ValueError(
                        f"Compartment '{comp.id}': {attr}='{m_id}' does not match any defined material."
                    )

        # device_id referenced in Fire or Vent must exist in devices
        for fire in self.fires:
            if fire.device_id is not None and fire.device_id not in device_ids:
                raise ValueError(
                    f"Fire '{fire.id}': device_id='{fire.device_id}' does not match any defined device."
                )

        for vent in self.wall_vents:
            if vent.device_id is not None and vent.device_id not in device_ids:
                raise ValueError(
                    f"WallVent '{vent.id}': device_id='{vent.device_id}' does not match any defined device."
                )

        for cf_vent in self.ceiling_floor_vents:
            if cf_vent.device_id is not None and cf_vent.device_id not in device_ids:
                raise ValueError(
                    f"CeilingFloorVent '{cf_vent.id}': device_id='{cf_vent.device_id}' does not match any defined device."
                )

        for m_vent in self.mechanical_vents:
            if m_vent.device_id is not None and m_vent.device_id not in device_ids:
                raise ValueError(
                    f"MechanicalVent '{m_vent.id}': device_id='{m_vent.device_id}' does not match any defined device."
                )

        comp_map = {c.id: c for c in self.compartments}

        # Fire position outside compartment dimensions
        for fire in self.fires:
            fire_comp = comp_map.get(fire.comp_id)
            if (
                fire_comp is not None
                and fire_comp.width is not None
                and fire_comp.depth is not None
                and len(fire.location) == 2
            ):
                x, y = fire.location
                if not (0 <= x <= fire_comp.width) or not (0 <= y <= fire_comp.depth):
                    warnings.warn(
                        f"Fire '{fire.id}': location={fire.location} is outside compartment "
                        f"'{fire_comp.id}' dimensions ({fire_comp.width} x {fire_comp.depth}).",
                        UserWarning,
                        stacklevel=2,
                    )

        # Device position outside compartment dimensions
        for device in self.devices:
            dev_comp = comp_map.get(device.comp_id)
            if (
                dev_comp is not None
                and dev_comp.width is not None
                and dev_comp.depth is not None
                and dev_comp.height is not None
                and len(device.location) == 3
            ):
                x, y, z = device.location
                if (
                    not (0 <= x <= dev_comp.width)
                    or not (0 <= y <= dev_comp.depth)
                    or not (0 <= z <= dev_comp.height)
                ):
                    warnings.warn(
                        f"Device '{device.id}': location={device.location} is outside compartment "
                        f"'{dev_comp.id}' dimensions ({dev_comp.width} x {dev_comp.depth} x {dev_comp.height}).",
                        UserWarning,
                        stacklevel=2,
                    )

        avail_fire_ids = {fire.id for fire in self.fires}
        for device in self.devices:
            if device.type in {"PLATE", "CYLINDER"}:
                if device.normal is None and device.surface_orientation is not None:
                    if (
                        device.surface_orientation
                        not in Device.VALID_SURFACE_ORIENTATIONS
                    ):
                        if device.surface_orientation not in avail_fire_ids:
                            raise ValueError(
                                f"Device '{device.id}': surface_orientation='{device.surface_orientation}' "
                                "is not a valid orientation and does not match any defined fire id."
                            )
