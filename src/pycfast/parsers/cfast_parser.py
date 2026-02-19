"""
CFAST input file parser module.

This module provides functionality to parse CFAST input files (.in) and convert them
back to CFASTModel objects using the various PyCFAST object.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import f90nml  # type: ignore

from ..ceiling_floor_vents import CeilingFloorVents
from ..compartments import Compartments
from ..devices import Devices
from ..fires import Fires
from ..material_properties import MaterialProperties
from ..mechanical_vents import MechanicalVents
from ..model import CFASTModel
from ..simulation_environment import SimulationEnvironment
from ..surface_connections import SurfaceConnections
from ..wall_vents import WallVents

# CFAST namelist block type constants
BLOCK_TYPE_HEAD = "HEAD"
BLOCK_TYPE_TIME = "TIME"
BLOCK_TYPE_INIT = "INIT"
BLOCK_TYPE_MISC = "MISC"
BLOCK_TYPE_DIAG = "DIAG"
BLOCK_TYPE_MATL = "MATL"
BLOCK_TYPE_COMP = "COMP"
BLOCK_TYPE_VENT = "VENT"
BLOCK_TYPE_FIRE = "FIRE"
BLOCK_TYPE_CHEM = "CHEM"
BLOCK_TYPE_TABL = "TABL"
BLOCK_TYPE_DEVC = "DEVC"
BLOCK_TYPE_CONN = "CONN"
BLOCK_TYPE_TAIL = "TAIL"

# VENT type constants
VENT_TYPE_WALL = "WALL"
VENT_TYPE_FLOOR = "FLOOR"
VENT_TYPE_CEILING = "CEILING"
VENT_TYPE_MECHANICAL = "MECHANICAL"


class CFASTParser:
    """Parser for CFAST input files (.in format).

    This class can read CFAST input files and convert them back to CFASTModel objects
    with all the component classes properly instantiated. The parser handles various
    CFAST namelist blocks including simulation environment, materials, compartments,
    vents, fires, and devices.

    Parameters
    ----------
    simulation_environment: SimulationEnvironment
        object containing simulation settings.
    material_properties: List[MaterialProperties]
        List of MaterialProperties objects.
    compartments: List[Compartments]
        List of Compartments objects.
    wall_vents: List[WallVents]
        List of WallVents objects.
    ceiling_floor_vents: List[CeilingFloorVents]
        List of CeilingFloorVents objects.
    mechanical_vents: List[MechanicalVents]
        List of MechanicalVents objects.
    fires: List[Fires]
        List of Fires objects.
    devices: List[Devices]
        List of Devices objects.
    surface_connections: List[SurfaceConnections]
        List of SurfaceConnections objects.

    Examples
    --------
    >>> parser = CFASTParser()
    >>> model = parser.parse_file("example.in")
    >>> print(model.simulation_environment.title)
    """

    def __init__(self) -> None:
        self.reset()

    def reset(self) -> None:
        """
        Reset parser state for parsing a new file.

        Clears all component lists and reinitializes the simulation environment.
        This method is called automatically when parsing a new file.
        """
        self.simulation_environment: SimulationEnvironment = SimulationEnvironment(
            title=""
        )
        self.material_properties: list[MaterialProperties] = []
        self.compartments: list[Compartments] = []
        self.wall_vents: list[WallVents] = []
        self.ceiling_floor_vents: list[CeilingFloorVents] = []
        self.mechanical_vents: list[MechanicalVents] = []
        self.fires: list[Fires] = []
        self.devices: list[Devices] = []
        self.surface_connections: list[SurfaceConnections] = []

        self._fire_hash_map: dict[
            str, Fires
        ] = {}  # will be useful for merging chemistry, data tables, and fire

    def parse_file(
        self, file_path: str | Path, output_path: str | Path | None = None
    ) -> CFASTModel:
        """
        Parse a CFAST input file and return a CFASTModel object.

        Reads and parses a CFAST input file (.in format), extracting all namelist
        blocks and converting them to appropriate PyCFAST component objects.

        Parameters
        ----------
        file_path: str | Path
            Path to the CFAST input file (.in). Can be a string or Path object.
        output_path: str | Path | None, optional
            Optional path to save the parsed output file. If None, defaults to
            appending '_parsed' to the original file name.


        Returns
        -------
        CFASTModel
            CFASTModel object with all components parsed from the file, including:
            - Simulation environment settings
            - Material properties
            - Compartment definitions
            - Vent configurations
            - Fire definitions
            - Device specifications

        Raises
        ------
        FileNotFoundError:
            If the input file doesn't exist at the specified path.
        ValueError:
            If the file format is invalid or required parameters are missing.

        Examples
        --------
            >>> parser = CFASTParser()
            >>> model = parser.parse_file("/path/to/simulation.in")
            >>> print(f"Parsed {len(model.compartments)} compartments")
        """
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"Input file not found: {file_path}")

        self.reset()

        with open(file_path, encoding="utf-8") as f:
            content = f.read()

        content = sanitize_cfast_title_and_material(content)

        try:
            nml_data = f90nml.read(file_path)
        except Exception as e:
            raise ValueError(f"Failed to parse CFAST file: {e}") from e

        # remove double quotes and double single quotes from every str in nml_data which can make cfast crashes
        for _key, value in nml_data.items():
            if isinstance(value, dict):
                for k, v in value.items():
                    if isinstance(v, str):
                        value[k] = v.replace("'", "").replace('"', "")
        self._parse_namelist_data(nml_data, content)

        if output_path is None:
            file_name = f"{file_path.stem}_parsed{file_path.suffix}"
        else:
            file_name = str(output_path)

        return CFASTModel(
            simulation_environment=self.simulation_environment,
            material_properties=self.material_properties,
            compartments=self.compartments,
            wall_vents=self.wall_vents,
            ceiling_floor_vents=self.ceiling_floor_vents,
            mechanical_vents=self.mechanical_vents,
            fires=self.fires,
            devices=self.devices,
            surface_connections=self.surface_connections,
            file_name=file_name,
        )

    def _parse_namelist_data(self, nml_data: dict, content: str) -> None:
        """
        Parse the namelist data dictionary from f90nml.

        Parameters
        ----------
        nml_data: dict
            Dictionary from f90nml.read() containing all namelist blocks.
        content: str
            String content of the CFAST input file.

        Raises
        ------
        ValueError:
            If an unknown block type is encountered or required data is missing.
        """
        clean_content = self._clean_content(content)
        # Create a dispatch table for block type handlers
        block_handlers = {
            BLOCK_TYPE_HEAD.lower(): self._parse_head_block,
            BLOCK_TYPE_TIME.lower(): self._parse_time_block,
            BLOCK_TYPE_INIT.lower(): self._parse_init_block,
            BLOCK_TYPE_MISC.lower(): self._parse_misc_block,
            BLOCK_TYPE_MATL.lower(): self._parse_material_block,
            BLOCK_TYPE_COMP.lower(): self._parse_compartment_block,
            BLOCK_TYPE_VENT.lower(): self._parse_vent_block,
            BLOCK_TYPE_FIRE.lower(): self._parse_fire_block,
            BLOCK_TYPE_CHEM.lower(): self._parse_chemistry_block,
            BLOCK_TYPE_TABL.lower(): self._parse_table_block,
            BLOCK_TYPE_DEVC.lower(): self._parse_device_block,
            BLOCK_TYPE_CONN.lower(): self._parse_connection_block,
        }

        # f90nml returns a dictionary with namelist names as keys (lowercase)
        for block_name, block_data in nml_data.items():
            block_name_lower = block_name.lower()

            if block_name_lower == BLOCK_TYPE_DIAG.lower():
                self._parse_diag_block(clean_content)
            elif block_name_lower == BLOCK_TYPE_TAIL.lower():
                continue  # TAIL block marks the end of the file
            elif block_name_lower in block_handlers:
                # Convert keys to uppercase for existing parsing methods
                uppercase_data = {k.upper(): v for k, v in block_data.items()}
                block_handlers[block_name_lower](uppercase_data)
            else:
                print(
                    f"Warning: Unknown block type '{block_name}' encountered, skipping."
                )

        # Process fire hash map after all blocks are parsed
        self._finalize_fire_parsing()

    def _parse_diag_block(self, content: str) -> None:
        """Parse DIAG namelist block."""
        try:
            diag_lines = next(
                line
                for line in content.splitlines()
                if line.strip().startswith("&DIAG")
            )
            self.simulation_environment.extra_custom = diag_lines
        except StopIteration:
            # No DIAG block found
            pass

    def _finalize_fire_parsing(self) -> None:
        """
        Finalize fire parsing by adding all fires from hash map to fires list.

        This method is called after all blocks are parsed to ensure that
        chemistry and data table information has been properly associated
        with fire objects.
        """
        for fire in self._fire_hash_map.values():
            self.fires.append(fire)

    def _clean_content(self, content: str) -> str:
        """
        Clean content by removing comments and extra whitespace, joining lines inside blocks.

        Processes the raw input file content by:
        - Removing comment lines (starting with !!)
        - Removing empty lines
        - Joining continuation lines within namelist blocks
        - Preserving block structure

        Parameters
        ----------
        content: str
            Raw content from the CFAST input file.

        Returns
        -------
        str
            Cleaned content string ready for block extraction.
        """
        cleaned_lines = []
        in_block = False
        block_lines: list[str] = []
        for line in content.splitlines():
            stripped = line.strip()
            if not stripped or stripped.startswith("!!"):
                continue
            if stripped.startswith("&"):
                in_block = True
                if block_lines:
                    # Should not happen, but flush if needed
                    cleaned_lines.append(" ".join(block_lines))
                    block_lines = []
                block_lines.append(stripped)
            elif stripped == "/":
                if in_block:
                    block_lines.append(stripped)
                    cleaned_lines.append(" ".join(block_lines))
                    block_lines = []
                    in_block = False
                else:
                    cleaned_lines.append(stripped)
            else:
                if in_block:
                    block_lines.append(stripped)
                else:
                    cleaned_lines.append(stripped)
        if block_lines:
            cleaned_lines.append(" ".join(block_lines))
        return "\n".join(cleaned_lines)

    def _get_param(
        self,
        params: dict,
        key: str,
        default: Any = None,
        required: bool = False,
        param_type: type | None = None,
    ) -> Any:
        """
        Extract and validate parameter from parsed namelist parameters.

        Parameters
        ----------
        params: dict
            Dictionary of parsed parameters from a namelist block.
        key: str
            Parameter name to retrieve (case-sensitive).
        default: Any
            Default value to return if parameter is not found.
        required: bool
            If True, raises ValueError if parameter is missing.
        param_type: type | None
            Optional type to convert the parameter value to.

        Returns
        -------
        Any
            Parameter value, optionally converted to specified type.

        Raises
        ------
        ValueError:
            If required parameter is missing or type conversion fails.

        Examples
        --------
            >>> params = {'WIDTH': '1.5', 'HEIGHT': '2.0'}
            >>> self._get_param(params, 'WIDTH', param_type=float)
            1.5
            >>> self._get_param(params, 'MISSING', default=0.0)
            0.0
        """
        value = params.get(key, default)
        if required and value is None:
            raise ValueError(f"Missing required parameter: {key}")
        if param_type and value is not None:
            try:
                value = param_type(value)
            except Exception as err:
                raise ValueError(
                    f"Parameter {key} could not be converted to {param_type}: {value}"
                ) from err
        return value

    @staticmethod
    def _normalize_comp_ids(comp_ids: Any) -> list[str]:
        """
        Normalize compartment IDs to ensure they are always returned as a list of strings.

        Parameters
        ----------
        comp_ids: Any
            Compartment IDs in various formats (str, list, None, etc.).

        Returns
        -------
        list[str]
            List of compartment ID strings. Empty list if input is None.

        Examples
        --------
        >>> CFASTParser._normalize_comp_ids("COMP1")
        ['COMP1']
        >>> CFASTParser._normalize_comp_ids(["COMP1", "COMP2"])
        ['COMP1', 'COMP2']
        >>> CFASTParser._normalize_comp_ids(None)
        []
        """
        if isinstance(comp_ids, str):
            return [comp_ids]
        elif comp_ids is None:
            return []
        elif not isinstance(comp_ids, list):
            return list(comp_ids)
        return comp_ids

    def _extract_params(
        self, params: dict, param_map: dict[str, dict[str, Any]]
    ) -> dict[str, Any]:
        """
        Extract and validate multiple parameters using a parameter mapping.

        This method provides a way to extract multiple parameters
        from a namelist block using a declarative parameter mapping approach.

        Parameters
        ----------
        params: dict
            Dictionary of parsed parameters from a namelist block.
        param_map: dict[str, dict[str, Any]]
            Dictionary mapping target parameter names to their extraction config.
            Each config dict can contain:
            - 'source': Source parameter name (defaults to target name if not provided)
            - 'required': Whether parameter is required (default: False)
            - 'default': Default value if parameter is missing
            - 'type': Type to convert parameter to
            - 'transform': Optional function to transform the value

        Returns
        -------
        dict[str, Any]
            Dictionary of extracted and validated parameters ready for object construction.

        Raises
        ------
        ValueError:
            If required parameter is missing or type conversion fails.

        Examples
        --------
        >>> param_map = {
        ...     'id': {'source': 'ID', 'required': True, 'type': str},
        ...     'width': {'source': 'WIDTH', 'required': True, 'type': float},
        ...     'active': {'source': 'ACTIVE', 'default': False, 'type': bool}
        ... }
        >>> extracted = self._extract_params(params, param_map)
        >>> device = Device(**extracted)
        """
        extracted = {}

        for target_name, config in param_map.items():
            source_name = config.get("source", target_name.upper())
            required = config.get("required", False)
            default = config.get("default")
            param_type = config.get("type")
            transform = config.get("transform")

            value = self._get_param(
                params,
                source_name,
                default=default,
                required=required,
                param_type=param_type,
            )

            if transform and value is not None:
                try:
                    value = transform(value)
                except Exception as err:
                    raise ValueError(
                        f"Failed to transform parameter {source_name}: {err}"
                    ) from err

            extracted[target_name] = value

        return extracted

    def _parse_head_block(self, params: dict[str, Any]) -> None:
        """Parse HEAD namelist block."""
        if "TITLE" in params:
            self.simulation_environment.title = params.get("TITLE", "")

    def _parse_time_block(self, params: dict[str, Any]) -> None:
        """Parse TIME namelist block."""
        if "SIMULATION" in params:
            self.simulation_environment.time_simulation = params["SIMULATION"]
        if "PRINT" in params:
            self.simulation_environment.print = params["PRINT"]
        if "SMOKEVIEW" in params:
            self.simulation_environment.smokeview = params["SMOKEVIEW"]
        if "SPREADSHEET" in params:
            self.simulation_environment.spreadsheet = params["SPREADSHEET"]

    def _parse_init_block(self, params: dict[str, Any]) -> None:
        """Parse INIT namelist block."""
        if "PRESSURE" in params:
            self.simulation_environment.init_pressure = params["PRESSURE"]
        if "RELATIVE_HUMIDITY" in params:
            self.simulation_environment.relative_humidity = params["RELATIVE_HUMIDITY"]
        if "INTERIOR_TEMPERATURE" in params:
            self.simulation_environment.interior_temperature = params[
                "INTERIOR_TEMPERATURE"
            ]
        if "EXTERIOR_TEMPERATURE" in params:
            self.simulation_environment.exterior_temperature = params[
                "EXTERIOR_TEMPERATURE"
            ]

    def _parse_misc_block(self, params: dict[str, Any]) -> None:
        """Parse MISC namelist block."""
        if "ADIABATIC" in params:
            self.simulation_environment.adiabatic = bool(params["ADIABATIC"])
        if "MAX_TIME_STEP" in params:
            self.simulation_environment.max_time_step = params["MAX_TIME_STEP"]
        if "LOWER_OXYGEN_LIMIT" in params:
            self.simulation_environment.lower_oxygen_limit = params[
                "LOWER_OXYGEN_LIMIT"
            ]

    def _parse_material_block(self, params: dict[str, Any]) -> None:
        """Parse MATL namelist block."""
        param_map = {
            "id": {"source": "ID", "required": True, "type": str},
            "material": {"source": "MATERIAL", "required": True, "type": str},
            "conductivity": {"source": "CONDUCTIVITY", "required": True, "type": float},
            "density": {"source": "DENSITY", "required": True, "type": float},
            "specific_heat": {
                "source": "SPECIFIC_HEAT",
                "required": True,
                "type": float,
            },
            "thickness": {"source": "THICKNESS", "required": True, "type": float},
            "emissivity": {"source": "EMISSIVITY", "required": True, "type": float},
        }
        material_params = self._extract_params(params, param_map)
        material = MaterialProperties(**material_params)
        self.material_properties.append(material)

    def _parse_compartment_block(self, params: dict[str, Any]) -> None:
        """Parse COMP namelist block."""

        def extract_origin_coords(
            origin_list: list[float],
        ) -> tuple[float, float, float]:
            if not origin_list or len(origin_list) < 3:
                raise ValueError("ORIGIN must contain at least 3 coordinates [x, y, z]")
            return origin_list[0], origin_list[1], origin_list[2]

        param_map: dict[str, dict[str, Any]] = {
            "id": {"source": "ID", "required": True, "type": str},
            "width": {"source": "WIDTH", "required": True, "type": float},
            "depth": {"source": "DEPTH", "required": True, "type": float},
            "height": {"source": "HEIGHT", "required": True, "type": float},
            "ceiling_mat_id": {"source": "CEILING_MATL_ID", "default": "OFF"},
            "ceiling_thickness": {"source": "CEILING_THICKNESS", "type": float},
            "wall_mat_id": {"source": "WALL_MATL_ID", "default": "OFF"},
            "wall_thickness": {"source": "WALL_THICKNESS", "type": float},
            "floor_mat_id": {"source": "FLOOR_MATL_ID", "default": "OFF"},
            "floor_thickness": {"source": "FLOOR_THICKNESS", "type": float},
            "shaft": {"source": "SHAFT", "type": bool},
            "hall": {"source": "HALL", "type": bool},
            "leak_area_ratio": {"source": "LEAK_AREA_RATIO", "type": list},
            "cross_sect_areas": {"source": "CROSS_SECT_AREAS", "type": list},
            "cross_sect_heights": {"source": "CROSS_SECT_HEIGHTS", "type": list},
            "_origin": {
                "source": "ORIGIN",
                "required": True,
                "type": list,
                "transform": extract_origin_coords,
            },
        }

        compartment_params = self._extract_params(params, param_map)

        origin_x, origin_y, origin_z = compartment_params.pop("_origin")
        compartment_params.update(
            {"origin_x": origin_x, "origin_y": origin_y, "origin_z": origin_z}
        )

        compartment = Compartments(**compartment_params)
        self.compartments.append(compartment)

    def _parse_vent_block(self, params: dict[str, Any]) -> None:
        """Parse VENT namelist block."""
        vent_type = params.get("TYPE", "").upper()

        if vent_type == VENT_TYPE_WALL:
            self._parse_wall_vent(params)
        elif vent_type in (VENT_TYPE_FLOOR, VENT_TYPE_CEILING):
            self._parse_ceiling_floor_vent(params)
        elif vent_type == VENT_TYPE_MECHANICAL:
            self._parse_mechanical_vent(params)
        else:
            raise ValueError(f"Unknown vent type: {vent_type}")

    def _parse_wall_vent(self, params: dict[str, Any]) -> None:
        """Parse wall vent parameters and create WallVents object."""
        param_map = {
            "id": {"source": "ID", "required": True, "type": str},
            "comps_ids": {
                "source": "COMP_IDS",
                "default": [],
                "type": list,
                "transform": self._normalize_comp_ids,
            },
            "bottom": {"source": "BOTTOM", "required": True, "type": float},
            "height": {"source": "HEIGHT", "default": 0, "type": float},
            "width": {"source": "WIDTH", "required": True, "type": float},
            "face": {"source": "FACE", "default": "", "type": str},
            "offset": {"source": "OFFSET", "required": True, "type": float},
            "open_close_criterion": {"source": "CRITERION", "type": str},
            "time": {"source": "T", "type": list},
            "fraction": {"source": "F", "type": list},
            "set_point": {"source": "SETPOINT", "type": float},
            "device_id": {"source": "DEVC_ID", "type": str},
            "pre_fraction": {"source": "PRE_FRACTION", "type": float},
            "post_fraction": {"source": "POST_FRACTION", "type": float},
        }

        vent_params = self._extract_params(params, param_map)
        vent = WallVents(**vent_params)
        self.wall_vents.append(vent)

    def _parse_ceiling_floor_vent(self, params: dict[str, Any]) -> None:
        """Parse ceiling/floor vent parameters and create CeilingFloorVents object."""
        param_map = {
            "id": {"source": "ID", "required": True, "type": str},
            "comps_ids": {
                "source": "COMP_IDS",
                "default": [],
                "type": list,
                "transform": self._normalize_comp_ids,
            },
            "area": {"source": "AREA", "default": 0.0, "type": float},
            "shape": {"source": "SHAPE", "default": "ROUND", "type": str},
            "width": {"source": "WIDTH", "type": float},
            "offsets": {"source": "OFFSETS", "default": [0, 0], "type": list},
            "open_close_criterion": {"source": "CRITERION", "type": str},
            "time": {"source": "T", "type": list},
            "fraction": {"source": "F", "type": list},
            "set_point": {"source": "SETPOINT", "type": float},
            "device_id": {"source": "DEVC_ID", "type": str},
            "pre_fraction": {"source": "PRE_FRACTION", "type": float},
            "post_fraction": {"source": "POST_FRACTION", "type": float},
        }

        vent_params = self._extract_params(params, param_map)
        vent = CeilingFloorVents(**vent_params)
        self.ceiling_floor_vents.append(vent)

    def _parse_mechanical_vent(self, params: dict[str, Any]) -> None:
        """Parse mechanical vent parameters and create MechanicalVents object."""
        param_map = {
            "id": {"source": "ID", "required": True, "type": str},
            "comps_ids": {
                "source": "COMP_IDS",
                "default": [],
                "type": list,
                "transform": self._normalize_comp_ids,
            },
            "area": {"source": "AREAS", "default": [0, 0], "type": list},
            "heights": {"source": "HEIGHTS", "default": [0, 0], "type": list},
            "orientations": {
                "source": "ORIENTATIONS",
                "default": ["VERTICAL", "VERTICAL"],
                "type": list,
            },
            "flow": {"source": "FLOW", "default": 0.0, "type": float},
            "cutoffs": {"source": "CUTOFFS", "default": [200, 300], "type": list},
            "offsets": {"source": "OFFSETS", "default": [0, 0], "type": list},
            "filter_time": {"source": "FILTER_TIME", "type": float},
            "filter_efficiency": {"source": "FILTER_EFFICIENCY", "type": float},
            "open_close_criterion": {"source": "CRITERION", "type": str},
            "time": {"source": "T", "type": list},
            "fraction": {"source": "F", "type": list},
            "set_point": {"source": "SETPOINT", "type": float},
            "device_id": {"source": "DEVC_ID", "type": str},
            "pre_fraction": {"source": "PRE_FRACTION", "type": float},
            "post_fraction": {"source": "POST_FRACTION", "type": float},
        }

        vent_params = self._extract_params(params, param_map)
        vent = MechanicalVents(**vent_params)
        self.mechanical_vents.append(vent)

    def _parse_fire_block(self, params: dict[str, Any]) -> None:
        """Parse FIRE namelist block."""
        param_map = {
            "id": {"source": "ID", "required": True, "type": str},
            "comp_id": {"source": "COMP_ID", "required": True, "type": str},
            "fire_id": {"source": "FIRE_ID", "required": True, "type": str},
            "location": {"source": "LOCATION", "required": True, "type": list},
            "ignition_criterion": {"source": "IGNITION_CRITERION", "type": str},
            "set_point": {"source": "SETPOINT", "type": str},
            "device_id": {"source": "DEVC_ID", "type": str},
        }

        fire_params = self._extract_params(params, param_map)
        fire = Fires(**fire_params)

        fire.data_table = []

        # Store in hash map using fire_id for later merging with CHEM and TABL blocks
        self._fire_hash_map[fire.fire_id] = fire

    def _parse_chemistry_block(self, params: dict[str, Any]) -> None:
        """Parse CHEM namelist block for fire chemistry."""
        fire_id = self._get_param(params, "ID", required=True, param_type=str)

        if fire_id not in self._fire_hash_map:
            raise ValueError(
                f"FIRE_ID {fire_id} in CHEM block not found in any FIRE block."
            )

        param_map = {
            "carbon": {"source": "CARBON", "required": True, "type": float},
            "chlorine": {"source": "CHLORINE", "required": True, "type": float},
            "hydrogen": {"source": "HYDROGEN", "required": True, "type": float},
            "nitrogen": {"source": "NITROGEN", "required": True, "type": float},
            "oxygen": {"source": "OXYGEN", "required": True, "type": float},
            "heat_of_combustion": {
                "source": "HEAT_OF_COMBUSTION",
                "required": True,
                "type": float,
            },
            "radiative_fraction": {
                "source": "RADIATIVE_FRACTION",
                "required": True,
                "type": float,
            },
        }

        chemistry_params = self._extract_params(params, param_map)

        fire = self._fire_hash_map[fire_id]
        for param_name, value in chemistry_params.items():
            setattr(fire, param_name, value)

        # Update the hash map (CFAST relies on fire_id not id)
        self._fire_hash_map[fire.fire_id] = fire

    def _parse_table_block(self, params: dict[str, Any]) -> None:
        """Parse TABL namelist block for fire data tables."""
        if "LABELS" in params:
            return

        if "DATA" in params:
            param_map = {
                "fire_id": {
                    "source": "ID",
                    "required": True,
                    "type": str,
                },  # same as FIRE_ID
                "data_row": {"source": "DATA", "required": True, "type": list},
            }

            table_params = self._extract_params(params, param_map)
            fire_id = table_params["fire_id"]
            current_row = table_params["data_row"]

            if fire_id not in self._fire_hash_map:
                raise ValueError(
                    f"FIRE_ID {fire_id} in TABL block not found in any FIRE block."
                )

            fire = self._fire_hash_map[fire_id]
            if not hasattr(fire, "data_table"):
                fire.data_table = []
            fire.data_table.append(current_row)

    def _parse_device_block(self, params: dict[str, Any]) -> None:
        """Parse DEVC namelist block."""
        device_type = self._get_param(params, "TYPE", required=True, param_type=str)

        if device_type in ("CYLINDER", "PLATE"):
            param_map = {
                "id": {"source": "ID", "required": True, "type": str},
                "comp_id": {"source": "COMP_ID", "required": True, "type": str},
                "location": {"source": "LOCATION", "required": True, "type": list},
                "type": {"default": device_type},
                "material_id": {"source": "MATL_ID", "required": True, "type": str},
                "surface_orientation": {"source": "SURFACE_ORIENTATION", "type": str},
                "normal": {"source": "NORMAL", "type": list},
                "thickness": {"source": "THICKNESS", "type": float},
                "temperature_depth": {"source": "TEMPERATURE_DEPTH", "type": float},
                "depth_units": {"source": "DEPTH_UNITS", "default": "M", "type": str},
                "adiabatic": {"source": "ADIABATIC_TARGET", "type": bool},
                "convection_coefficients": {
                    "source": "CONVECTION_COEFFICIENTS",
                    "type": list,
                },
            }
            device_params = self._extract_params(params, param_map)
            device = Devices(**device_params)

        elif device_type == "HEAT_DETECTOR":
            param_map = {
                "id": {"source": "ID", "required": True, "type": str},
                "comp_id": {"source": "COMP_ID", "required": True, "type": str},
                "location": {"source": "LOCATION", "required": True, "type": list},
                "setpoint": {"source": "SETPOINT", "required": True, "type": float},
                "rti": {"source": "RTI", "required": True, "type": float},
            }
            device_params = self._extract_params(params, param_map)
            device = Devices.create_heat_detector(**device_params)

        elif device_type == "SMOKE_DETECTOR":
            param_map = {
                "id": {"source": "ID", "required": True, "type": str},
                "comp_id": {"source": "COMP_ID", "required": True, "type": str},
                "location": {"source": "LOCATION", "required": True, "type": list},
                "setpoint": {"source": "SETPOINT", "required": True, "type": float},
                "obscuration": {
                    "source": "OBSCURATION",
                    "default": 23.9334605082804,
                    "type": float,
                },
            }
            device_params = self._extract_params(params, param_map)
            device = Devices.create_smoke_detector(**device_params)

        elif device_type == "SPRINKLER":
            param_map = {
                "id": {"source": "ID", "required": True, "type": str},
                "comp_id": {"source": "COMP_ID", "required": True, "type": str},
                "location": {"source": "LOCATION", "required": True, "type": list},
                "setpoint": {"source": "SETPOINT", "required": True, "type": float},
                "rti": {"source": "RTI", "required": True, "type": float},
                "spray_density": {
                    "source": "SPRAY_DENSITY",
                    "required": True,
                    "type": float,
                },
            }
            device_params = self._extract_params(params, param_map)
            device = Devices.create_sprinkler(**device_params)

        else:
            raise ValueError(f"Unknown device type: {device_type}")

        self.devices.append(device)

    def _parse_connection_block(self, params: dict[str, Any]) -> None:
        """Parse a CONNECTION namelist block."""
        conn_type = self._get_param(params, "TYPE", required=True, param_type=str)

        if conn_type == "WALL":
            param_map = {
                "comp_id": {"source": "COMP_ID", "required": True, "type": str},
                "comp_ids": {"source": "COMP_IDS", "required": True, "type": str},
                "fraction": {"source": "F", "required": True, "type": float},
            }
            conn_params = self._extract_params(params, param_map)
            surface_connection = SurfaceConnections.wall_connection(**conn_params)

        elif conn_type == "FLOOR":
            param_map = {
                "comp_id": {"source": "COMP_ID", "required": True, "type": str},
                "comp_ids": {"source": "COMP_IDS", "required": True, "type": str},
            }
            conn_params = self._extract_params(params, param_map)
            surface_connection = SurfaceConnections.ceiling_floor_connection(
                **conn_params
            )

        else:
            raise ValueError(f"Unknown Surface Connections type: {conn_type}")

        self.surface_connections.append(surface_connection)


def sanitize_cfast_title_and_material(content: str) -> str:
    r"""
    Sanitize TITLE and MATERIAL values in CFAST input file content.

    Cleans problematic characters from TITLE and MATERIAL parameter values
    that can cause parsing issues. This function only modifies these specific
    parameters while leaving all other content unchanged.

    Characters removed/replaced:
    - Commas and slashes are replaced with spaces
    - Apostrophes and double quotes are removed
    - Multiple whitespace is collapsed to single spaces

    Parameters
    ----------
    content: str
        Raw content from a CFAST input file.

    Returns
    -------
    str
        Sanitized content with cleaned TITLE and MATERIAL values.

    Examples
    --------
        Input: "TITLE = 'Test/Case, with \"quotes\"'"
        Output: "TITLE = 'Test Case  with quotes'"

    Notes
    -----
        This preprocessing step helps ensure reliable parsing of CFAST input files
        that may contain special characters in text fields.
    """

    def _strip_quotes(s: str) -> tuple[str, str | None]:
        """Strip outer quotes and return the inner string and quote type."""
        if len(s) >= 2 and s[0] == s[-1] and s[0] in ("'", '"'):
            return s[1:-1], s[0]
        return s, None

    def _decode_token(raw: str) -> str:
        """Decode a parameter value token, handling quoted strings."""
        raw = raw.strip()
        inner, q = _strip_quotes(raw)
        if q == "'":
            return inner.replace("''", "'")  # decode doubled quotes
        if q == '"':
            return inner
        return raw

    def _sanitize_text(s: str) -> str:
        """Sanitize text by removing problematic characters."""
        s = s.replace('"', "").replace("'", "")
        s = s.replace(",", " ").replace("/", " ")
        s = re.sub(r"\s+", " ", s).strip()
        return s

    pattern = re.compile(
        r"""
        (?P<key>\b(?:TITLE|MATERIAL)\b)
        \s*=\s*
        (?P<val>
            "(?:[^"\\]|\\.)*"
            |
            '(?:[^']|'{2})*'
            |
            [^,\s/]+
        )
        """,
        re.VERBOSE,
    )

    def _repl(m: re.Match) -> str:
        key = m.group("key")
        raw_val = m.group("val")
        decoded = _decode_token(raw_val)
        sanitized = _sanitize_text(decoded)
        return f"{key} = '{sanitized}'"

    return pattern.sub(_repl, content)


def parse_cfast_file(
    file_path: str | Path, output_path: str | Path | None = None
) -> CFASTModel:
    """
    Parse a CFAST input file and return a CFASTModel object.

    Convenience function that creates a CFASTParser instance and parses
    the specified file in one call. This is the recommended way to parse
    CFAST input files for most use cases.

    Parameters
    ----------
    file_path: str | Path
        Path to the CFAST input file (.in). Can be string or Path object.

    Returns
    -------
    CFASTModel
        CFASTModel object with all components parsed from the file, including
        simulation environment, materials, compartments, vents, fires, and devices.

    Raises
    ------
    FileNotFoundError:
        If the input file doesn't exist.
    ValueError:
        If the file format is invalid or required parameters are missing.

    Warnings
    --------
        COMPONENT NAMES (TITLE, MATERIAL, ID, ETC.) SHOULD USE ALPHANUMERIC CHARACTERS ONLY.
        SPECIAL CHARACTERS LIKE QUOTES AND SLASHES MAY CAUSE PARSING ISSUES AND WILL BE
        AUTOMATICALLY SANITIZED WHERE POSSIBLE.

    Examples
    --------
    >>> model = parse_cfast_file("simulation.in")
    >>> print(f"Title: {model.simulation_environment.title}")
    >>> print(f"Compartments: {len(model.compartments)}")
    """
    parser = CFASTParser()
    return parser.parse_file(file_path, output_path)
