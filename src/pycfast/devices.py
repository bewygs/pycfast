"""
Device definition module for CFAST simulations.

This module provides the Device class for defining measurement devices
and sensors in a fire simulation, including both targets and detectors.
"""

from __future__ import annotations

from typing import Any

from .utils.namelist import NamelistRecord
from .utils.theme import build_card


class Devices:
    """
    Represents measurement and fire protection devices in a CFAST simulation.

    This class encompasses both targets and detection/suppression devices. Targets are
    any objects in the simulation that can heat up via radiative and convective heat
    transfer. The heat conduction into the target is performed via a one-dimensional
    calculation in either cartesian or cylindrical coordinates.

    Sprinklers and detectors are both considered detection devices by the CFAST model
    and are handled using the same inputs. Detection is based upon heat transfer to
    the detector. Fire suppression by a user-specified water spray begins once the
    associated detection device is activated.

    For targets, if the target is only needed to report the local gas temperature,
    which may include the plume or ceiling jet, then you may specify arbitrary
    properties and normal vector. The output spreadsheet file includes the local
    gas temperature in addition to the target temperature.

    Care should be taken when specifying detectors to activate based on smoke
    obscuration since the only calculation included in CFAST is a simple two-zone
    calculation of soot concentration that does not include the impact of an initial
    ceiling layer as is done for temperature-based calculations.

    Parameters
    ----------
    id : str
        The selected name must be unique (i.e., not the same as another target or
        detector in the same simulation).
    comp_id : str
        The compartment in which the target or detector is located.
    location : list[float]
        Position of the device as distances from the compartment walls and floor.
        Format: [x, y, z] where x is distance from left wall, y is distance from
        front wall, z is height above floor. Default units: m.
    type : str
        Type of device. Options: "PLATE", "CYLINDER" (targets), "HEAT_DETECTOR",
        "SMOKE_DETECTOR", "SPRINKLER" (detectors).
    material_id : str
        What the target is made of. Any existing material in the list of thermal
        properties may be used here. There can be only one material per target.
        Required for target types only.
    surface_orientation : str, optional
        Predefined surface orientation for targets. Alternative to specifying
        normal vector directly.
    normal : list[float], optional
        Specifies a vector of unit length perpendicular to the exposed surface of
        the target. Format: [nx, ny, nz]. For example, the vector (-1,0,0) indicates
        that the target is facing the left wall. The vector (0,0,1) is facing the ceiling.
        Required for targets when surface_orientation is not specified.
    thickness : float, optional
        Thickness of the target material. If not specified, will use value from
        the material definition.
    temperature_depth : float
        For each target, CFAST calculates the internal temperature at a number of
        node points within the target. By default, the reported internal temperature
        is the temperature at the center of the target. This input allows the user
        to override this default position. The input represents the position as a
        fraction of the thickness from the front surface to the back surface of the
        material. Default units: none, default value: 0.5.
    depth_units : str
        Units for depth measurement. Default: "M" for meters.
    setpoint : float, optional
        For heat detectors and sprinklers: the temperature at or above which the
        detector link activates. Default units: °C, default value: dependent on type.
        For smoke detectors: the obscuration at or above which the detector activates.
        Default units: %/m, default value: 23.93 %/m (8 %/ft).
    rti : float, optional
        The Response Time Index (RTI) for the sprinkler or detection device.
        Default units: (m·s)^(1/2).
    obscuration : float
        The obscuration at or above which the smoke detector activates.
        Default units: %/m, default value: 23.93 %/m (8 %/ft).
    spray_density : float, optional
        The amount of water dispersed by a sprinkler. The units for spray density
        are length/time, derived by dividing the volumetric flow rate by the spray
        area. The suppression calculation is based upon an experimental correlation
        by Evans. Default units: m/s.
    adiabatic : bool
        Usually should never be used, only when DIAG. Default: False.
    convection_coefficients : list[float], optional
        Usually should never be used, only when DIAG.

    Raises
    ------
    ValueError
        If location is not a list of 3 numbers.
        If target type is specified but required target parameters are missing.
        If detector type is specified but required detector parameters are missing.
        If both normal and surface_orientation are specified or both are None.
        If normal vector is not a list of 3 numbers.
        If unknown device type is specified.

    Examples
    --------
    Create a plate target:

    >>> target = Devices(
    ...     id="WALL_TARGET",
    ...     comp_id="ROOM1",
    ...     location=[2.0, 3.0, 1.5],     # 2m from left, 3m from front, 1.5m high
    ...     type="PLATE",
    ...     material_id="GYPSUM",
    ...     normal=[-1, 0, 0],            # Facing left wall
    ...     temperature_depth=0.5         # Center of target
    ... )

    Create a heat detector:

    >>> detector = Devices(
    ...     id="HEAT_DET_1",
    ...     comp_id="KITCHEN",
    ...     location=[2.5, 2.5, 2.4],     # Ceiling mounted
    ...     type="HEAT_DETECTOR",
    ...     material_id="STEEL",          # Detector material
    ...     setpoint=68,                  # Activate at 68°C
    ...     rti=50,                       # RTI of 50 (m·s)^(1/2)
    ...     temperature_depth=0.5
    ... )

    Create a sprinkler:

    >>> sprinkler = Devices(
    ...     id="SPRINKLER_1",
    ...     comp_id="OFFICE",
    ...     location=[3.0, 3.0, 2.4],     # Ceiling mounted
    ...     type="SPRINKLER",
    ...     material_id="STEEL",
    ...     setpoint=74,                  # Activate at 74°C
    ...     rti=100,                      # RTI of 100 (m·s)^(1/2)
    ...     spray_density=0.002,          # 2 mm/s spray density
    ...     temperature_depth=0.5
    ... )

    Create a smoke detector:

    >>> smoke_det = Devices(
    ...     id="SMOKE_DET_1",
    ...     comp_id="CORRIDOR",
    ...     location=[5.0, 1.0, 2.4],     # Ceiling mounted
    ...     type="SMOKE_DETECTOR",
    ...     material_id="PLASTIC",
    ...     obscuration=23.93,            # Default obscuration threshold
    ...     temperature_depth=0.5
    ... )

    Notes
    -----
    For sprinkler suppression, several cautions should be observed:

    1) The first sprinkler activated controls the effect on the fire heat release rate.
       Subsequent sprinklers have no additional effect.
    2) The fire suppression algorithm assumes the effect is solely to reduce the heat
       release rate. Effects on gas temperatures or mixing are ignored.
    3) The sprinkler always reduces the heat release rate. The ability of a fire to
       overwhelm an under-designed sprinkler is not modeled.
    4) Since sprinkler dynamics and spray effects on gas temperatures are not modeled,
       calculated activation times of secondary devices after the first sprinkler
       should not be relied upon.

    Often, smoke alarm activation is simulated with a temperature-based criterion
    (as a heat alarm), typically 5°C to 10°C above ambient, rather than using
    obscuration due to limitations in the two-zone soot calculation.
    """

    def __init__(
        self,
        id: str,
        comp_id: str,
        location: list[float | int],
        type: str,
        material_id: str,
        surface_orientation: str | None = None,
        normal: list[float | int] | None = None,
        thickness: float | None = None,
        temperature_depth: float = 0.5,
        depth_units: str = "M",
        setpoint: float | None = None,
        rti: float | None = None,
        obscuration: float = 23.93,
        spray_density: float | None = None,
        adiabatic: bool = False,
        convection_coefficients: list[float] | None = None,
    ):
        if len(location) != 3 or not all(
            isinstance(coord, int | float) for coord in location
        ):
            raise ValueError(
                "location must be a list of 3 numbers representing [x, y, z] position."
            )

        # Define target and detector types
        target_types = {"PLATE", "CYLINDER"}
        detector_types = {"HEAT_DETECTOR", "SMOKE_DETECTOR", "SPRINKLER"}

        self.id = id
        self.comp_id = comp_id
        self.location = location
        self.type = type
        self.adiabatic = adiabatic
        self.convection_coefficients = convection_coefficients

        if type in target_types:
            self.material_id = material_id
            self.surface_orientation = surface_orientation
            self.normal = normal
            self.thickness = thickness
            self.temperature_depth = temperature_depth
            self.depth_units = depth_units

        elif type in detector_types:
            self.setpoint = setpoint
            self.rti = rti
            self.spray_density = spray_density
            self.obscuration = obscuration

        else:
            raise ValueError(
                f"Unknown device type '{type}'. "
                f"Must be one of: {target_types | detector_types}"
            )

        self._validate()

    def __repr__(self) -> str:
        """Return a detailed string representation of the Devices."""
        location_str = f"[{', '.join(map(str, self.location))}]"

        if self.type in {"PLATE", "CYLINDER"}:
            return (
                f"Devices("
                f"id='{self.id}', type='{self.type}', comp_id='{self.comp_id}', "
                f"location={location_str}, material_id='{self.material_id}', "
                f"thickness={self.thickness}, temperature_depth={self.temperature_depth}"
                f")"
            )
        else:  # Detectors
            detector_params = []
            if hasattr(self, "setpoint") and self.setpoint is not None:
                detector_params.append(f"setpoint={self.setpoint}")
            if hasattr(self, "rti") and self.rti is not None:
                detector_params.append(f"rti={self.rti}")
            if hasattr(self, "spray_density") and self.spray_density is not None:
                detector_params.append(f"spray_density={self.spray_density}")

            detector_str = f", {', '.join(detector_params)}" if detector_params else ""

            return (
                f"Devices("
                f"id='{self.id}', type='{self.type}', comp_id='{self.comp_id}', "
                f"location={location_str}{detector_str}"
                f")"
            )

    def __str__(self) -> str:
        """Return a user-friendly string representation of the Devices."""
        location_str = f"({self.location[0]}, {self.location[1]}, {self.location[2]})"

        if self.type in {"PLATE", "CYLINDER"}:
            device_info = f"Target '{self.id}' ({self.type})"
            details = f"material: {self.material_id}, depth: {self.temperature_depth}m"
            if self.thickness:
                details += f", thickness: {self.thickness}m"
        else:  # Detectors
            device_info = (
                f"Detector '{self.id}' ({self.type.replace('_', ' ').title()})"
            )
            details_list = []
            if hasattr(self, "setpoint") and self.setpoint is not None:
                if self.type == "HEAT_DETECTOR":
                    details_list.append(f"setpoint: {self.setpoint}°C")
                else:
                    details_list.append(f"setpoint: {self.setpoint}")
            if hasattr(self, "rti") and self.rti is not None:
                details_list.append(f"RTI: {self.rti}")
            if hasattr(self, "spray_density") and self.spray_density is not None:
                details_list.append(f"spray: {self.spray_density}")

            details = ", ".join(details_list) if details_list else "configured"

        return f"{device_info} in '{self.comp_id}' at {location_str} ({details})"

    def _repr_html_(self) -> str:
        """Return an HTML representation for Jupyter/interactive environments."""
        device_type = getattr(self, "type", "UNKNOWN")
        location_str = f"({', '.join(map(str, getattr(self, 'location', [])))})"

        # Icon and color based on device type
        if "HEAT" in device_type:
            icon = "🌡️"
            color = "#e17055"
            type_name = "Heat Detector"
        elif "SMOKE" in device_type:
            icon = "💨"
            color = "#636e72"
            type_name = "Smoke Detector"
        elif "SPRINKLER" in device_type:
            icon = "💧"
            color = "#0984e3"
            type_name = "Sprinkler"
        elif "TARGET" in device_type or device_type in {"PLATE", "CYLINDER"}:
            icon = "🎯"
            color = "#6c5ce7"
            type_name = "Target"
        else:
            icon = "📊"
            color = "#00b894"
            type_name = device_type.replace("_", " ").title()

        # Device-specific properties
        props_html = ""
        if hasattr(self, "setpoint") and self.setpoint is not None:
            unit = "°C" if device_type == "HEAT_DETECTOR" else ""
            props_html += f"<div><strong>Setpoint:</strong> {self.setpoint}{unit}</div>"
        if hasattr(self, "rti") and self.rti is not None:
            props_html += f"<div><strong>RTI:</strong> {self.rti} (m·s)½</div>"
        if hasattr(self, "material_id") and self.material_id:
            props_html += f"<div><strong>Material:</strong> {self.material_id}</div>"
        if hasattr(self, "surface_orientation") and self.surface_orientation:
            props_html += (
                f"<div><strong>Orientation:</strong> {self.surface_orientation}</div>"
            )
        if hasattr(self, "thickness") and self.thickness is not None:
            props_html += f"<div><strong>Thickness:</strong> {self.thickness} m</div>"
        if hasattr(self, "spray_density") and self.spray_density is not None:
            props_html += (
                f"<div><strong>Spray density:</strong> {self.spray_density}</div>"
            )

        body_html = f"""
            <div class="pycfast-card-grid">
                <div><strong>Location:</strong> {location_str}</div>
                <div><strong>Type:</strong> {type_name}</div>
                {props_html}
            </div>
        """

        return build_card(
            icon=icon,
            gradient=f"linear-gradient(135deg, {color}, {color}aa)",
            title=f"Device: {self.id}",
            subtitle=f"<strong>{type_name}</strong> in <strong>{self.comp_id}</strong>",
            accent_color=color,
            body_html=body_html,
        )

    def __getitem__(self, key: str) -> Any:
        """Get device property by name for dictionary-like access."""
        if not hasattr(self, key):
            raise KeyError(f"Property '{key}' not found in Devices.")
        return getattr(self, key)

    def __setitem__(self, key: str, value: Any) -> None:
        """Set device property by name for dictionary-like assignment.

        Validates the object state after setting the attribute to ensure
        all constraints are still satisfied.

        Raises
        ------
        KeyError
            If the property does not exist.
        ValueError
            If setting this value would violate object constraints.
        """
        if not hasattr(self, key):
            raise KeyError(f"Cannot set '{key}'. Property does not exist in Devices.")
        old_value = getattr(self, key)
        setattr(self, key, value)
        try:
            self._validate()
        except Exception:
            setattr(self, key, old_value)
            raise

    def _validate(self) -> None:
        """Validate the current state of the device attributes.

        Raises
        ------
        ValueError
            If any attribute violates the constraints.
        """
        if len(self.location) != 3 or not all(
            isinstance(coord, int | float) for coord in self.location
        ):
            raise ValueError(
                "location must be a list of 3 numbers representing [x, y, z] position."
            )

        target_types = {"PLATE", "CYLINDER"}
        detector_types = {"HEAT_DETECTOR", "SMOKE_DETECTOR", "SPRINKLER"}

        if self.type in target_types:
            if not getattr(self, "material_id", None):
                raise ValueError(f"Target type '{self.type}' requires material_id")

            normal = getattr(self, "normal", None)
            surface_orientation = getattr(self, "surface_orientation", None)
            if (normal is None and surface_orientation is None) or (
                normal is not None and surface_orientation is not None
            ):
                raise ValueError(
                    f"Target type '{self.type}' requires either normal or "
                    f"surface_orientation (but not both)"
                )
            if normal is not None and surface_orientation is None:
                if (
                    not isinstance(normal, list)
                    or len(normal) != 3
                    or not all(isinstance(n, int | float) for n in normal)
                ):
                    raise ValueError(
                        "normal must be a list of 3 numbers representing [nx, ny, nz]."
                    )

        elif self.type in detector_types:
            if self.type == "HEAT_DETECTOR":
                if not all(
                    [
                        getattr(self, "setpoint", None) is not None,
                        getattr(self, "rti", None) is not None,
                    ]
                ):
                    raise ValueError(
                        "HEAT_DETECTOR requires setpoint and rti parameters"
                    )
            elif self.type == "SPRINKLER":
                if not all(
                    [
                        getattr(self, "setpoint", None) is not None,
                        getattr(self, "rti", None) is not None,
                        getattr(self, "spray_density", None) is not None,
                    ]
                ):
                    raise ValueError(
                        "SPRINKLER requires setpoint, rti, and spray_density parameters"
                    )

        elif self.type not in target_types | detector_types:
            raise ValueError(
                f"Unknown device type '{self.type}'. "
                f"Must be one of: {target_types | detector_types}"
            )

    def to_input_string(self) -> str:
        """
        Generate CFAST input file string for this device.

        Returns
        -------
            Formatted string ready for inclusion in CFAST input file.

        Examples
        --------
        >>> target = Devices.create_target(
        ...     id="WALL_TARGET",
        ...     comp_id="ROOM1",
        ...     location=[2.0, 3.0, 1.5],
        ...     type="PLATE",
        ...     material_id="GYPSUM",
        ...     normal=[-1, 0, 0],
        ...     temperature_depth=0.5
        ... )
        >>> print(target.to_input_string())
        &DEVC ID = 'WALL_TARGET' COMP_ID = 'ROOM1' LOCATION = 2.0, 3.0, 1.5 ...

        """
        rec = NamelistRecord("DEVC")
        rec.add_field("ID", self.id)
        rec.add_field("COMP_ID", self.comp_id)
        rec.add_list_field("LOCATION", self.location)
        rec.add_field("TYPE", self.type)

        if self.type in {"PLATE", "CYLINDER"}:
            rec.add_field("MATL_ID", self.material_id)
            if self.normal is None and self.surface_orientation is not None:
                rec.add_field("SURFACE_ORIENTATION", self.surface_orientation)
            if self.normal is not None and self.surface_orientation is None:
                rec.add_list_field("NORMAL", self.normal)
            rec.add_field("THICKNESS", self.thickness)
            rec.add_field("TEMPERATURE_DEPTH", self.temperature_depth)
            rec.add_field("DEPTH_UNITS", self.depth_units)

        elif self.type == "HEAT_DETECTOR":
            rec.add_field("SETPOINT", self.setpoint)
            rec.add_field("RTI", self.rti)

        elif self.type == "SMOKE_DETECTOR":
            rec.add_list_field("SETPOINTS", [self.obscuration, self.obscuration])

        elif self.type == "SPRINKLER":
            rec.add_field("SETPOINT", self.setpoint)
            rec.add_field("RTI", self.rti)
            rec.add_field("SPRAY_DENSITY", self.spray_density)

        if self.adiabatic:
            rec.add_field("ADIABATIC_TARGET", True)
        if self.convection_coefficients:
            rec.add_list_field("CONVECTION_COEFFICIENTS", self.convection_coefficients)

        return rec.build()

    @classmethod
    def create_target(
        cls,
        id: str,
        comp_id: str,
        location: list[float | int],
        type: str,
        material_id: str,
        temperature_depth: float = 0.5,
        thickness: float | None = None,
        surface_orientation: str | None = None,
        normal: list[float | int] | None = None,
        depth_units: str = "M",
        adiabatic: bool = False,
        convection_coefficients: list[float] | None = None,
    ) -> Devices:
        """
        Create a target device.

        Parameters
        ----------
        id: str
            Unique identifier
        comp_id: str
            Compartment ID
        location: list[float | int]
            [x, y, z] position
        target_type: str
            "PLATE" or "CYLINDER"
        material_id: str
            Material identifier
        surface_orientation: str | None
            Surface orientation string (mutually exclusive with normal)
        normal: list[float | int] | None
            [nx, ny, nz] normal vector (mutually exclusive with surface_orientation)
        thickness: float | None
            Target thickness in meters
        temperature_depth: float
            Temperature measurement depth in meters
        depth_units: str
            Depth units, defaults to "M"

        Returns
        -------
        Devices
            Device instance configured as a target

        Raises
        ------
        ValueError
            If both surface_orientation and normal are provided,
            or if neither is provided
        """
        # Validate that exactly one of surface_orientation or normal is provided
        if (normal is None and surface_orientation is None) or (
            normal is not None and surface_orientation is not None
        ):
            raise ValueError(
                f"Target type '{type}' requires either normal or "
                f"surface_orientation (but not both)"
            )

        return cls(
            id=id,
            comp_id=comp_id,
            location=location,
            type=type,
            material_id=material_id,
            surface_orientation=surface_orientation,
            normal=normal,
            thickness=thickness,
            temperature_depth=temperature_depth,
            depth_units=depth_units,
            adiabatic=adiabatic,
            convection_coefficients=convection_coefficients,
        )

    @classmethod
    def create_heat_detector(
        cls,
        id: str,
        comp_id: str,
        location: list[float | int],
        setpoint: float,
        rti: float,
    ) -> Devices:
        """
        Create a heat detector.

        Parameters
        ----------
        id: str
            Unique identifier
        comp_id: str
            Compartment ID
        location: list[float | int]
            [x, y, z] position
        setpoint: float
            Activation temperature
        rti: float
            Response Time Index

        Returns
        -------
        Devices
            Device instance configured as a heat detector
        """
        return cls(
            id=id,
            comp_id=comp_id,
            location=location,
            type="HEAT_DETECTOR",
            material_id="",  # Not used for detectors
            setpoint=setpoint,
            rti=rti,
        )

    @classmethod
    def create_smoke_detector(
        cls,
        id: str,
        comp_id: str,
        location: list[float | int],
        setpoint: float,
        obscuration: float = 23.93,
    ) -> Devices:
        """
        Create a smoke detector.

        Parameters
        ----------
        id: str
            Unique identifier
        comp_id: str
            Compartment ID
        location: list[float | int]
            [x, y, z] position
        setpoint: float
            Activation threshold (e.g., obscuration)
        obscuration: float
            Obscuration value, default: 23.93 %/m

        Returns
        -------
        Devices
            Device instance configured as a smoke detector
        """
        return cls(
            id=id,
            comp_id=comp_id,
            location=location,
            type="SMOKE_DETECTOR",
            material_id="",  # Not used for detectors
            setpoint=setpoint,
            obscuration=obscuration,
        )

    @classmethod
    def create_sprinkler(
        cls,
        id: str,
        comp_id: str,
        location: list[float | int],
        setpoint: float,
        rti: float,
        spray_density: float,
    ) -> Devices:
        """
        Create a sprinkler.

        Parameters
        ----------
        id: str
            Unique identifier
        comp_id: str
            Compartment ID
        location: list[float | int]
            [x, y, z] position
        setpoint: float
            Activation temperature
        rti: float
            Response Time Index
        spray_density: float
            Spray density in m/s

        Returns
        -------
        Devices
            Device instance configured as a sprinkler
        """
        return cls(
            id=id,
            comp_id=comp_id,
            location=location,
            type="SPRINKLER",
            material_id="",  # Not used for detectors
            setpoint=setpoint,
            rti=rti,
            spray_density=spray_density,
        )
