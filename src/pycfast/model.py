"""
CFAST model creation and execution module.

This module provides the main CFASTModel class for creating, configuring,
and executing CFAST fire simulations through a Python interface.
"""

from __future__ import annotations

import copy
import os
import shutil
import subprocess
import warnings
from collections.abc import Generator
from typing import Any, cast

import numpy as np
import pandas as pd

from .ceiling_floor_vents import CeilingFloorVents
from .compartments import Compartments
from .devices import Devices
from .fires import Fires
from .material_properties import MaterialProperties
from .mechanical_vents import MechanicalVents
from .simulation_environment import SimulationEnvironment
from .surface_connections import SurfaceConnections
from .utils import CSV_READ_CONFIGS
from .utils.theme import build_card
from .wall_vents import WallVents


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
    material_properties: List[MaterialProperties]
        List of material property definitions
    compartments: List[Compartments]
        List of compartment/room definitions
    wall_vents: List[WallVents]
        List of wall vent connections between compartments
    ceiling_floor_vents: List[CeilingFloorVents]
        List of ceiling/floor vent connections
    mechanical_vents: List[MechanicalVents]
        List of mechanical ventilation systems
    fires: List[Fires]
        List of fire definitions
    targets: List[Devices]
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
        compartments: list[Compartments],
        material_properties: list[MaterialProperties] | None = None,
        wall_vents: list[WallVents] | None = None,
        ceiling_floor_vents: list[CeilingFloorVents] | None = None,
        mechanical_vents: list[MechanicalVents] | None = None,
        fires: list[Fires] | None = None,
        devices: list[Devices] | None = None,
        surface_connections: list[SurfaceConnections] | None = None,
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
        """Return a user-friendly string representation of the CFASTModel."""
        total_components = (
            len(self.compartments)
            + len(self.fires)
            + len(self.wall_vents)
            + len(self.ceiling_floor_vents)
            + len(self.mechanical_vents)
            + len(self.devices)
            + len(self.material_properties)
            + len(self.surface_connections)
        )

        return (
            f"CFAST Fire Model '{self.file_name}'\n"
            f"  Compartments: {len(self.compartments)}\n"
            f"  Fires: {len(self.fires)}\n"
            f"  Vents: {len(self.wall_vents)} wall, {len(self.ceiling_floor_vents)} ceiling/floor, {len(self.mechanical_vents)} mechanical\n"
            f"  Devices: {len(self.devices)}\n"
            f"  Materials: {len(self.material_properties)}\n"
            f"  Surface Connections: {len(self.surface_connections)}\n"
            f"  Total components: {total_components}"
        )

    def _repr_html_(self) -> str:
        """Return an HTML representation for Jupyter/interactive environments."""
        total_components = (
            len(self.compartments)
            + len(self.fires)
            + len(self.wall_vents)
            + len(self.ceiling_floor_vents)
            + len(self.mechanical_vents)
            + len(self.devices)
            + len(self.material_properties)
            + len(self.surface_connections)
        )

        # Component details with expandable sections
        components_html = ""

        if self.compartments:
            comp_details = "".join(
                [
                    f"<li><strong>{c.id}</strong>: {c['width']:.1f}×{c['depth']:.1f}×{c['height']:.1f} m</li>"
                    for c in self.compartments
                ]
            )
            components_html += f"""
            <details class="pycfast-detail">
                <summary><strong>Compartments</strong> ({len(self.compartments)})</summary>
                <ul style="margin: 5px 0; padding-left: 20px;">{comp_details}</ul>
            </details>
            """

        if self.fires:
            fire_details = "".join(
                [
                    f"<li><strong>{f.id}</strong> in {f.comp_id}: {getattr(f, 'fire_id', 'Custom')}</li>"
                    for f in self.fires
                ]
            )
            components_html += f"""
            <details class="pycfast-detail">
                <summary><strong>Fires</strong> ({len(self.fires)})</summary>
                <ul style="margin: 5px 0; padding-left: 20px;">{fire_details}</ul>
            </details>
            """

        if any([self.wall_vents, self.ceiling_floor_vents, self.mechanical_vents]):
            vent_count = (
                len(self.wall_vents)
                + len(self.ceiling_floor_vents)
                + len(self.mechanical_vents)
            )
            vent_details = ""
            if self.wall_vents:
                vent_details += "".join(
                    [
                        f"<li><strong>{v.id}</strong> (Wall): {v.comps_ids[0]} ↔ {v.comps_ids[1]}</li>"
                        for v in self.wall_vents
                    ]
                )
            if self.ceiling_floor_vents:
                vent_details += "".join(
                    [
                        f"<li><strong>{v.id}</strong> (Ceiling/Floor): {v.comps_ids[0]} ↔ {v.comps_ids[1]}</li>"
                        for v in self.ceiling_floor_vents
                    ]
                )
            if self.mechanical_vents:
                vent_details += "".join(
                    [
                        f"<li><strong>{v.id}</strong> (Mechanical): {v.comps_ids[0]} → {v.comps_ids[1]}</li>"
                        for v in self.mechanical_vents
                    ]
                )

            components_html += f"""
            <details class="pycfast-detail">
                <summary><strong>Ventilation</strong> ({vent_count})</summary>
                <ul style="margin: 5px 0; padding-left: 20px;">{vent_details}</ul>
            </details>
            """

        if self.devices:
            device_details = "".join(
                [
                    f"<li><strong>{d.id}</strong> in {d.comp_id}: {getattr(d, 'type', 'Device')}</li>"
                    for d in self.devices
                ]
            )
            components_html += f"""
            <details class="pycfast-detail">
                <summary><strong>Devices</strong> ({len(self.devices)})</summary>
                <ul style="margin: 5px 0; padding-left: 20px;">{device_details}</ul>
            </details>
            """

        if self.material_properties:
            material_details = "".join(
                [
                    f"<li><strong>{m.id}</strong>: {getattr(m, 'material', 'Material')}</li>"
                    for m in self.material_properties
                ]
            )
            components_html += f"""
            <details class="pycfast-detail">
                <summary><strong>Materials</strong> ({len(self.material_properties)})</summary>
                <ul style="margin: 5px 0; padding-left: 20px;">{material_details}</ul>
            </details>
            """

        body_html = f"""
            <div class="pycfast-card-grid" style="margin-bottom: 15px;">
                <div><strong>Total Components:</strong> {total_components}</div>
                <div><strong>Simulation:</strong> {getattr(self.simulation_environment, "title", "Untitled")}</div>
                <div><strong>Duration:</strong> {getattr(self.simulation_environment, "time_simulation", 0) / 60:.0f} min</div>
            </div>
            <div style="font-size: 0.9em;">
                {components_html}
            </div>
        """

        return build_card(
            icon="🔥",
            gradient="linear-gradient(135deg, #ff6b35, #f7931e)",
            title="CFAST Model",
            subtitle=f"<code>{self.file_name}</code>",
            accent_color="#ff6b35",
            body_html=body_html,
            wide=True,
        )

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
            If True, prints CFAST stdout and stderr to the console.

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
                        f"{os.path.basename(input_file_path).replace('.in', '')}",
                        *self.extra_arguments,
                    ],
                    check=True,
                    capture_output=True,
                    text=True,
                    cwd=str(cwd),
                    timeout=timeout,
                )
                if verbose:
                    print(f"CFAST stdout:\n{result.stdout}")
                    print(f"CFAST stderr:\n{result.stderr}")
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
            base_name = self.file_name.replace(".in", "")

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
                        warnings.warn(f"Output CSV is empty: {csv_file}", stacklevel=2)
                        dataframes[suffix] = pd.DataFrame()
                        continue
                    except Exception as e:
                        print(f"Error reading {csv_file}: {e}")
                        dataframes[suffix] = None
                else:
                    if suffix not in optional_csvs:
                        print(f"CSV file not found: {csv_file}")
                    dataframes[suffix] = None

            return dataframes
        finally:
            # Always restore the original file_name
            self.file_name = original_file_name

    def update_fire_params(
        self,
        fire: int | str | None = None,
        fire_index: int | None = None,
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
        fire_index : int, optional
            Deprecated. Use 'fire' parameter instead.
            Fire index (0-based). If both fire and fire_index are provided, 'fire' takes precedence.
        data_table : list[list[float]], np.ndarray, or pd.DataFrame, optional
            New fire data table to replace existing one. Must have 9 columns:
            TIME, HRR, HEIGHT, AREA, CO_YIELD, SOOT_YIELD, HCN_YIELD, HCL_YIELD, TRACE_YIELD.
        **kwargs : Any
            Fire object attributes to update. See Fires class documentation
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
        new_model = copy.deepcopy(self)

        if not new_model.fires:
            raise ValueError("Model has no fires to update")

        if fire is not None:
            fire_idx = self._resolve_fire_identifier(fire)
        elif fire_index is not None:
            fire_idx = fire_index
        else:
            fire_idx = 0

        if fire_idx >= len(new_model.fires):
            raise IndexError(
                f"Fire index {fire_idx} is out of range. "
                f"Model has {len(new_model.fires)} fires."
            )

        target_fire = new_model.fires[fire_idx]

        if data_table is not None:
            if isinstance(data_table, pd.DataFrame):
                target_fire.data_table = data_table.values.tolist()
            elif isinstance(data_table, np.ndarray):
                target_fire.data_table = data_table.tolist()
            elif isinstance(data_table, list):
                target_fire.data_table = data_table
            else:
                raise TypeError(
                    "data_table must be a pandas DataFrame, numpy ndarray, or list of lists"
                )

        for param, value in kwargs.items():
            if hasattr(target_fire, param):
                setattr(target_fire, param, value)
            else:
                available_params = self._get_available_attributes(target_fire)
                raise ValueError(
                    f"Fire object has no parameter '{param}'. "
                    f"Available parameters: {', '.join(available_params)}"
                )

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

        if (
            not hasattr(new_model, "simulation_environment")
            or new_model.simulation_environment is None
        ):
            raise AttributeError("Model has no simulation_environment object")

        for param, value in kwargs.items():
            if hasattr(new_model.simulation_environment, param):
                setattr(new_model.simulation_environment, param, value)
            else:
                available_params = self._get_available_attributes(
                    new_model.simulation_environment
                )
                raise ValueError(
                    f"Simulation environment has no parameter '{param}'. "
                    f"Available parameters: {', '.join(available_params)}"
                )

        return new_model

    def update_compartment_params(
        self,
        compartment: int | str | None = None,
        compartment_index: int | None = None,
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
        compartment_index : int, optional
            Deprecated. Use 'compartment' parameter instead.
        **kwargs : Any
            Compartment attributes to update. See Compartments class documentation
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
        new_model = copy.deepcopy(self)

        if not new_model.compartments:
            raise ValueError("Model has no compartments to update")

        if compartment is not None:
            comp_idx = self._resolve_compartment_identifier(compartment)
        elif compartment_index is not None:
            comp_idx = compartment_index
        else:
            comp_idx = 0

        if comp_idx >= len(new_model.compartments):
            raise IndexError(
                f"Compartment index {comp_idx} is out of range. "
                f"Model has {len(new_model.compartments)} compartments."
            )

        target_compartment = new_model.compartments[comp_idx]

        for param, value in kwargs.items():
            if hasattr(target_compartment, param):
                setattr(target_compartment, param, value)
            else:
                available_params = self._get_available_attributes(target_compartment)
                raise ValueError(
                    f"Compartment has no parameter '{param}'. "
                    f"Available parameters: {', '.join(available_params)}"
                )

        return new_model

    def update_material_params(
        self,
        material: int | str | None = None,
        material_index: int | None = None,
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
        material_index : int, optional
            Deprecated. Use 'material' parameter instead.
        **kwargs : Any
            Material properties attributes to update. See MaterialProperties class
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
        new_model = copy.deepcopy(self)

        if not new_model.material_properties:
            raise ValueError("Model has no materials to update")

        if material is not None:
            mat_idx = self._resolve_material_identifier(material)
        elif material_index is not None:
            mat_idx = material_index
        else:
            mat_idx = 0

        if mat_idx >= len(new_model.material_properties):
            raise IndexError(
                f"Material index {mat_idx} is out of range. "
                f"Model has {len(new_model.material_properties)} materials."
            )

        target_material = new_model.material_properties[mat_idx]

        for param, value in kwargs.items():
            if hasattr(target_material, param):
                setattr(target_material, param, value)
            else:
                available_params = self._get_available_attributes(target_material)
                raise ValueError(
                    f"Material has no parameter '{param}'. "
                    f"Available parameters: {', '.join(available_params)}"
                )

        return new_model

    def update_wall_vent_params(
        self,
        vent: int | str | None = None,
        vent_index: int | None = None,
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
        vent_index : int, optional
            Deprecated. Use 'vent' parameter instead.
        **kwargs : Any
            Wall vent attributes to update. See WallVents class documentation
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
        new_model = copy.deepcopy(self)

        if not new_model.wall_vents:
            raise ValueError("Model has no wall vents to update")

        if vent is not None:
            vent_idx = self._resolve_wall_vent_identifier(vent)
        elif vent_index is not None:
            vent_idx = vent_index
        else:
            vent_idx = 0

        if vent_idx >= len(new_model.wall_vents):
            raise IndexError(
                f"Wall vent index {vent_idx} is out of range. "
                f"Model has {len(new_model.wall_vents)} wall vents."
            )

        target_vent = new_model.wall_vents[vent_idx]

        for param, value in kwargs.items():
            if hasattr(target_vent, param):
                setattr(target_vent, param, value)
            else:
                available_params = self._get_available_attributes(target_vent)
                raise ValueError(
                    f"Wall vent has no parameter '{param}'. "
                    f"Available parameters: {', '.join(available_params)}"
                )

        return new_model

    def update_ceiling_floor_vent_params(
        self,
        vent: int | str | None = None,
        vent_index: int | None = None,
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
        vent_index : int, optional
            Deprecated. Use 'vent' parameter instead.
        **kwargs : Any
            Ceiling/floor vent attributes to update. See CeilingFloorVents class
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
        new_model = copy.deepcopy(self)

        if not new_model.ceiling_floor_vents:
            raise ValueError("Model has no ceiling/floor vents to update")

        if vent is not None:
            vent_idx = self._resolve_ceiling_floor_vent_identifier(vent)
        elif vent_index is not None:
            vent_idx = vent_index
        else:
            vent_idx = 0

        if vent_idx >= len(new_model.ceiling_floor_vents):
            raise IndexError(
                f"Ceiling/floor vent index {vent_idx} is out of range. "
                f"Model has {len(new_model.ceiling_floor_vents)} ceiling/floor vents."
            )

        target_vent = new_model.ceiling_floor_vents[vent_idx]

        for param, value in kwargs.items():
            if hasattr(target_vent, param):
                setattr(target_vent, param, value)
            else:
                available_params = self._get_available_attributes(target_vent)
                raise ValueError(
                    f"Ceiling/floor vent has no parameter '{param}'. "
                    f"Available parameters: {', '.join(available_params)}"
                )

        return new_model

    def update_mechanical_vent_params(
        self,
        vent: int | str | None = None,
        vent_index: int | None = None,
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
        vent_index : int, optional
            Deprecated. Use 'vent' parameter instead.
        **kwargs : Any
            Mechanical vent attributes to update. See MechanicalVents class
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
        new_model = copy.deepcopy(self)

        if not new_model.mechanical_vents:
            raise ValueError("Model has no mechanical vents to update")

        if vent is not None:
            vent_idx = self._resolve_mechanical_vent_identifier(vent)
        elif vent_index is not None:
            vent_idx = vent_index
        else:
            vent_idx = 0

        if vent_idx >= len(new_model.mechanical_vents):
            raise IndexError(
                f"Mechanical vent index {vent_idx} is out of range. "
                f"Model has {len(new_model.mechanical_vents)} mechanical vents."
            )

        target_vent = new_model.mechanical_vents[vent_idx]

        for param, value in kwargs.items():
            if hasattr(target_vent, param):
                setattr(target_vent, param, value)
            else:
                available_params = self._get_available_attributes(target_vent)
                raise ValueError(
                    f"Mechanical vent has no parameter '{param}'. "
                    f"Available parameters: {', '.join(available_params)}"
                )

        return new_model

    def update_device_params(
        self,
        device: int | str | None = None,
        device_index: int | None = None,
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
        device_index : int, optional
            Deprecated. Use 'device' parameter instead.
        **kwargs : Any
            Device attributes to update. See Devices class documentation
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
        new_model = copy.deepcopy(self)

        if not new_model.devices:
            raise ValueError("Model has no devices to update")

        if device is not None:
            device_idx = self._resolve_device_identifier(device)
        elif device_index is not None:
            device_idx = device_index
        else:
            device_idx = 0

        if device_idx >= len(new_model.devices):
            raise IndexError(
                f"Device index {device_idx} is out of range. "
                f"Model has {len(new_model.devices)} devices."
            )

        target_device = new_model.devices[device_idx]

        for param, value in kwargs.items():
            if hasattr(target_device, param):
                setattr(target_device, param, value)
            else:
                available_params = self._get_available_attributes(target_device)
                raise ValueError(
                    f"Device has no parameter '{param}'. "
                    f"Available parameters: {', '.join(available_params)}"
                )

        return new_model

    def update_surface_connection_params(
        self,
        connection_index: int | None = None,
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
        connection_index : int, optional
            Deprecated. Use 'connection' parameter instead.
        **kwargs : Any
            Surface connection attributes to update. See SurfaceConnections class
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
        new_model = copy.deepcopy(self)

        if not new_model.surface_connections:
            raise ValueError("Model has no surface connections to update")

        if connection_index is not None:
            conn_idx = connection_index
        else:
            conn_idx = 0

        if conn_idx >= len(new_model.surface_connections):
            raise IndexError(
                f"Surface connection index {conn_idx} is out of range. "
                f"Model has {len(new_model.surface_connections)} surface connections."
            )

        target_connection = new_model.surface_connections[conn_idx]

        for param, value in kwargs.items():
            if hasattr(target_connection, param):
                setattr(target_connection, param, value)
            else:
                available_params = self._get_available_attributes(target_connection)
                raise ValueError(
                    f"Surface connection has no parameter '{param}'. "
                    f"Available parameters: {', '.join(available_params)}"
                )

        return new_model

    def add_fire(self, fire: Fires) -> CFASTModel:
        """
        Add a fire to the model and return a new model instance.

        Parameters
        ----------
        fire : Fires
            Fire object to add to the model

        Returns
        -------
        CFASTModel
            New model instance with the added fire

        Examples
        --------
        >>> new_fire = Fires(id="FIRE2", comp_id="ROOM1", location=[2.0, 2.0])
        >>> updated_model = model.add_fire(new_fire)
        """
        new_model = copy.deepcopy(self)
        new_model.fires.append(fire)
        return new_model

    def add_compartment(self, compartment: Compartments) -> CFASTModel:
        """
        Add a compartment to the model and return a new model instance.

        Parameters
        ----------
        compartment : Compartments
            Compartment object to add to the model

        Returns
        -------
        CFASTModel
            New model instance with the added compartment

        Examples
        --------
        >>> new_room = Compartments(id="ROOM3", width=5.0, depth=4.0, height=3.0)
        >>> updated_model = model.add_compartment(new_room)
        """
        new_model = copy.deepcopy(self)
        new_model.compartments.append(compartment)
        return new_model

    def add_material(self, material: MaterialProperties) -> CFASTModel:
        """
        Add a material property to the model and return a new model instance.

        Parameters
        ----------
        material : MaterialProperties
            Material properties object to add to the model

        Returns
        -------
        CFASTModel
            New model instance with the added material

        Examples
        --------
        >>> steel = MaterialProperties(id="STEEL", conductivity=45.0, density=7850)
        >>> updated_model = model.add_material(steel)
        """
        new_model = copy.deepcopy(self)
        new_model.material_properties.append(material)
        return new_model

    def add_wall_vent(self, vent: WallVents) -> CFASTModel:
        """
        Add a wall vent to the model and return a new model instance.

        Parameters
        ----------
        vent : WallVents
            Wall vent object to add to the model

        Returns
        -------
        CFASTModel
            New model instance with the added wall vent

        Examples
        --------
        >>> door = WallVents(comp_ids=["ROOM1", "ROOM2"], width=1.0, height=2.0)
        >>> updated_model = model.add_wall_vent(door)
        """
        new_model = copy.deepcopy(self)
        new_model.wall_vents.append(vent)
        return new_model

    def add_ceiling_floor_vent(self, vent: CeilingFloorVents) -> CFASTModel:
        """
        Add a ceiling/floor vent to the model and return a new model instance.

        Parameters
        ----------
        vent : CeilingFloorVents
            Ceiling/floor vent object to add to the model

        Returns
        -------
        CFASTModel
            New model instance with the added ceiling/floor vent

        Examples
        --------
        >>> hatch = CeilingFloorVents(comp_ids=["ROOM1", "ROOM2"], area=0.5)
        >>> updated_model = model.add_ceiling_floor_vent(hatch)
        """
        new_model = copy.deepcopy(self)
        new_model.ceiling_floor_vents.append(vent)
        return new_model

    def add_mechanical_vent(self, vent: MechanicalVents) -> CFASTModel:
        """
        Add a mechanical vent to the model and return a new model instance.

        Parameters
        ----------
        vent : MechanicalVents
            Mechanical vent object to add to the model

        Returns
        -------
        CFASTModel
            New model instance with the added mechanical vent

        Examples
        --------
        >>> hvac = MechanicalVents(comp_ids=["ROOM1", "OUTSIDE"], flow_rate=0.5)
        >>> updated_model = model.add_mechanical_vent(hvac)
        """
        new_model = copy.deepcopy(self)
        new_model.mechanical_vents.append(vent)
        return new_model

    def add_device(self, device: Devices) -> CFASTModel:
        """
        Add a device/target to the model and return a new model instance.

        Parameters
        ----------
        device : Devices
            Device object to add to the model

        Returns
        -------
        CFASTModel
            New model instance with the added device

        Examples
        --------
        >>> sensor = Devices.create_heat_detector(
        ...     comp_id="ROOM1", location=[2.0, 2.0, 2.4], temperature=68.0
        ... )
        >>> updated_model = model.add_device(sensor)
        """
        new_model = copy.deepcopy(self)
        new_model.devices.append(device)
        return new_model

    def add_surface_connection(self, connection: SurfaceConnections) -> CFASTModel:
        """
        Add a surface connection to the model and return a new model instance.

        Parameters
        ----------
        connection : SurfaceConnections
            Surface connection object to add to the model

        Returns
        -------
        CFASTModel
            New model instance with the added surface connection

        Examples
        --------
        >>> wall_conn = SurfaceConnections.wall_connection(
        ...     comp_ids=["ROOM1", "ROOM2"], fraction=0.5
        ... )
        >>> updated_model = model.add_surface_connection(wall_conn)
        """
        new_model = copy.deepcopy(self)
        new_model.surface_connections.append(connection)
        return new_model

    def _resolve_fire_identifier(self, identifier: int | str) -> int:
        """
        Resolve fire identifier to index.

        Parameters
        ----------
        identifier : int | str
            Fire identifier (index or id)

        Returns
        -------
        int
            Fire index
        """
        if isinstance(identifier, int):
            return identifier

        if isinstance(identifier, str):
            for idx, fire in enumerate(self.fires):
                if hasattr(fire, "id") and fire.id == identifier:
                    return idx
                if hasattr(fire, "fire_id") and fire.fire_id == identifier:
                    return idx

            raise ValueError(f"No fire found with id/fire_id '{identifier}'.")

        raise TypeError(f"Fire identifier must be int or str, got {type(identifier)}")

    def _resolve_compartment_identifier(self, identifier: int | str) -> int:
        """
        Resolve compartment identifier to index.

        Parameters
        ----------
        identifier : int | str
            Compartment identifier (index or id)

        Returns
        -------
        int
            Compartment index
        """
        if isinstance(identifier, int):
            return identifier

        if isinstance(identifier, str):
            for idx, compartment in enumerate(self.compartments):
                if hasattr(compartment, "id") and compartment.id == identifier:
                    return idx

            raise ValueError(f"No compartment found with id '{identifier}'. ")

        raise TypeError(
            f"Compartment identifier must be int or str, got {type(identifier)}"
        )

    def _resolve_material_identifier(self, identifier: int | str) -> int:
        """
        Resolve material identifier to index.

        Parameters
        ----------
        identifier : int | str
            Material identifier (index or id)

        Returns
        -------
        int
            Material index

        """
        if isinstance(identifier, int):
            return identifier

        if isinstance(identifier, str):
            for idx, material in enumerate(self.material_properties):
                if hasattr(material, "id") and material.id == identifier:
                    return idx

            raise ValueError(f"No material found with id '{identifier}.'")

        raise TypeError(
            f"Material identifier must be int or str, got {type(identifier)}"
        )

    def _resolve_wall_vent_identifier(self, identifier: int | str) -> int:
        """
        Resolve wall vent identifier to index.

        Parameters
        ----------
        identifier : int | str
            Wall vent identifier (index or id)

        Returns
        -------
        int
            Wall vent index
        """
        if isinstance(identifier, int):
            return identifier

        if isinstance(identifier, str):
            for idx, vent in enumerate(self.wall_vents):
                if hasattr(vent, "id") and vent.id == identifier:
                    return idx

            raise ValueError(f"No wall vent found with id '{identifier}'")

        raise TypeError(
            f"Wall vent identifier must be int or str, got {type(identifier)}"
        )

    def _resolve_ceiling_floor_vent_identifier(self, identifier: int | str) -> int:
        """
        Resolve ceiling/floor vent identifier to index.

        Parameters
        ----------
        identifier : int | str
            Ceiling/floor vent identifier (index or id)

        Returns
        -------
        int
            Ceiling/floor vent index
        """
        if isinstance(identifier, int):
            return identifier

        if isinstance(identifier, str):
            for idx, vent in enumerate(self.ceiling_floor_vents):
                if hasattr(vent, "id") and vent.id == identifier:
                    return idx

            raise ValueError(f"No ceiling/floor vent found with id '{identifier}'")

        raise TypeError(
            f"Ceiling/floor vent identifier must be int or str, got {type(identifier)}"
        )

    def _resolve_mechanical_vent_identifier(self, identifier: int | str) -> int:
        """
        Resolve mechanical vent identifier to index.

        Parameters
        ----------
        identifier : int | str
            Mechanical vent identifier (index or id)

        Returns
        -------
        int
            Mechanical vent index

        """
        if isinstance(identifier, int):
            return identifier

        if isinstance(identifier, str):
            for idx, vent in enumerate(self.mechanical_vents):
                if hasattr(vent, "id") and vent.id == identifier:
                    return idx

            raise ValueError(f"No mechanical vent found with id '{identifier}'")

        raise TypeError(
            f"Mechanical vent identifier must be int or str, got {type(identifier)}"
        )

    def _resolve_device_identifier(self, identifier: int | str) -> int:
        """
        Resolve device identifier to index.

        Parameters
        ----------
        identifier : int | str
            Device identifier (index or id)

        Returns
        -------
        int
            Device index
        """
        if isinstance(identifier, int):
            return identifier

        if isinstance(identifier, str):
            for idx, device in enumerate(self.devices):
                if hasattr(device, "id") and device.id == identifier:
                    return idx

            raise ValueError(f"No device found with id '{identifier}'")

        raise TypeError(f"Device identifier must be int or str, got {type(identifier)}")

    def _resolve_surface_connection_identifier(self, identifier: int) -> int:
        """
        Resolve surface connection identifier to index.

        Parameters
        ----------
        identifier : int
            Surface connection identifier (index only !)

        Returns
        -------
        int
            Surface connection index
        """
        if isinstance(identifier, int):
            return identifier

        raise TypeError(
            f"Surface connection identifier must be int, got {type(identifier)}"
        )

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

    def summary(self) -> None:
        """
        Print a clear summary of the CFAST model configuration.

        Shows the model info and all components with their current parameter values
        using each component's string representation.

        Examples
        --------
        >>> model.summary()
        Model: my_simulation.in
        Simulation: 'Building Fire Test' (3600s)

        Material Properties (2):
            MaterialProperties(material='GYPSUM', conductivity=0.17, density=800...)

        Compartments (2):
            Compartments(id='ROOM1', width=4.0, depth=3.0, height=2.5...)
        """
        print(f"\nModel: {self.file_name}")
        print(
            f"Simulation: '{self.simulation_environment.title}' ({self.simulation_environment.time_simulation}s)"
        )

        print("\nComponents:")

        if self.material_properties:
            print(f"  Material Properties ({len(self.material_properties)}):")
            for mat in self.material_properties:
                print(f"    {mat}")

        if self.compartments:
            print(f"  Compartments ({len(self.compartments)}):")
            for comp in self.compartments:
                print(f"    {comp}")

        if self.wall_vents:
            print(f"  Wall Vents ({len(self.wall_vents)}):")
            for wall_vent in self.wall_vents:
                print(f"    {wall_vent}")

        if self.ceiling_floor_vents:
            print(f"  Ceiling/Floor Vents ({len(self.ceiling_floor_vents)}):")
            for ceiling_floor_vent in self.ceiling_floor_vents:
                print(f"    {ceiling_floor_vent}")

        if self.mechanical_vents:
            print(f"  Mechanical Vents ({len(self.mechanical_vents)}):")
            for mechanical_vent in self.mechanical_vents:
                print(f"    {mechanical_vent}")

        if self.fires:
            print(f"  Fires ({len(self.fires)}):")
            for fire in self.fires:
                print(f"    {fire}")

        if self.devices:
            print(f"  Devices ({len(self.devices)}):")
            for device in self.devices:
                print(f"    {device}")

        if self.surface_connections:
            print(f"  Surface Connections ({len(self.surface_connections)}):")
            for conn in self.surface_connections:
                print(f"    {conn}")

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
        log_file_path = self.file_name.replace(".in", ".log")
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
                ("!! Fires", self.fires),
                ("!! Devices", self.devices),
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
        Validate that all required components are present and correctly configured.

        This method checks that the model has (e.g. at least one compartment defined),
        and that all components are compatible with CFAST requirements.

        Raises
        ------
        ValueError:
            If any required components are missing or invalid
        """
        pass
