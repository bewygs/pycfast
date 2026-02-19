"""
Wall vent definition module for CFAST simulations.

This module provides the WallVents class for defining openings in walls
that connect compartments horizontally, such as doors, windows, and openings.
"""

from __future__ import annotations

from typing import Any

from .utils.namelist import NamelistRecord
from .utils.theme import build_card


class WallVents:
    """
    Represents wall openings connecting two compartments that physically overlap in elevation.

    Wall vents are doors or windows that connect compartments that physically overlap in
    elevation, or that connect to the outside. Horizontal flow connections may also be used
    to account for leakage between compartments or to the outdoors. Natural ventilation can
    occur when two compartments are connected via open doorways or windows (Wall Vents).
    If no vents are specified between two compartments, they are assumed to be isolated from
    each other.

    Parameters
    ----------
    id : str
        The selected name must be unique (i.e., not the same as another vent in the same
        simulation).
    comps_ids : list[str]
        List of two compartment IDs connected by this vent. The first compartment is the
        reference for all vent specifications. All specifications of the vent are made
        relative to the floor of the first compartment.
    bottom : float, optional
        Position of the bottom of the opening relative to the floor of the first compartment.
        Default units: m, default value: 0 m.
    height : float, optional
        Height of the opening relative to the bottom of the opening. Default units: m,
        default value: 0 m.
    width : float, optional
        The width of the opening. Default units: m, default value: 0 m.
    face : str
        The wall on which the vent is positioned. Choices are Front, Rear, Right, Left and
        are relative to the X-Z plane (Front and Rear faces are parallel to the X-axis;
        left and right are parallel to the Y-axis).
    offset : float, optional
        For visualization only, the horizontal distance between the near edge of the vent
        and the origin of the axis defined by the selected face in the first compartment.
        Default units: m, default value: 0 m.
    open_close_criterion : str, optional
        The opening/closing can be controlled by a user-specified time, or by a user-specified
        target's surface temperature or incident heat flux. Options: "TIME", "TEMPERATURE", "FLUX".
    time : list[float], optional
        Time during the simulation at which to begin or end a change in the open fraction.
        For time-based opening changes, this is a series of time points associated with
        opening fractions. Default units: s, default value: 0 s.
    fraction : list[float], optional
        Fraction between 0 and 1 of the vent width to indicate the vent is closed,
        partially-open, or fully-open at the associated time point. Default value: 1 (fully open).
    set_point : float, optional
        The critical value at which the vent opening change will occur. If it is less than
        or equal to zero, the default value of zero is taken. Can be temperature (°C) or
        flux (kW/m²) depending on criterion.
    device_id : str, optional
        User-specified target ID used to calculate surface temperature or incident heat flux
        to trigger a vent opening change. Target placement is specified by the user as part
        of the associated target definition.
    pre_fraction : float, optional
        Fraction between 0 and 1 of the vent width to indicate the vent is partially open
        at the start of the simulation. Default value: 1 (fully open).
    post_fraction : float, optional
        Opening fraction at the end of the simulation. The transition from the pre-activation
        fraction to the post-activation value is assumed to occur over one second beginning
        when the specified set point value is reached. Default value: 1 (fully open).

    Notes
    -----
    CFAST assumes a linear transition between time points. If the initial time specified
    for a time-changing opening fraction is non-zero, the vent is assumed to be open at
    the initial value of the open fraction from the beginning of the simulation up to and
    including the time associated with the initial value of the opening fraction. If the
    final value of the opening fraction is less than the total simulation time, the vent
    is assumed to be open at the final value of the opening fraction from and including
    the time associated with the final value of the opening fraction until the end of
    the simulation.

    Examples
    --------
    Create a door between two rooms following CFAST conventions:

    >>> door = WallVents(
    ...     id="DOOR_1_2",
    ...     comps_ids=["ROOM1", "ROOM2"],
    ...     bottom=0,           # Bottom at floor level (relative to first)
    ...     height=2.0,         # Height of opening relative to bottom
    ...     width=0.9,          # Width of the opening
    ...     face="RIGHT",       # Wall on which vent is positioned
    ...     offset=1.0          # Distance from origin for visualization
    ... )
    """

    def __init__(
        self,
        id: str,
        comps_ids: list[str],
        bottom: float | None = 0,
        height: float | None = 0,
        width: float | None = 0,
        face: str = "",
        offset: float | None = 0,
        open_close_criterion: str | None = None,  # can be "TIME","FLUX","TEMPERATURE"
        time: list[float] | None = None,
        fraction: list[float] | None = None,
        set_point: float
        | None = None,  # depends on criterion can be temperature (°C) or flux (kW/m²)
        device_id: str | None = None,  # trigger target ID for open/close criterion
        pre_fraction: float | None = 1,
        post_fraction: float | None = 1,
    ):
        self.id = id
        self.comps_ids = comps_ids
        self.bottom = bottom
        self.height = height
        self.width = width
        self.face = face
        self.offset = offset
        self.open_close_criterion = open_close_criterion
        self.time = time
        self.fraction = fraction
        self.set_point = set_point
        self.device_id = device_id
        self.pre_fraction = pre_fraction
        self.post_fraction = post_fraction

        self._validate()

    def _validate(self) -> None:
        """Validate the current state of the wall vent attributes.

        Raises
        ------
        ValueError
            If any attribute violates the constraints.
        """
        if len(self.comps_ids) != 2:
            raise ValueError("Wall vent must connect exactly 2 compartments")

        if self.comps_ids[0] == "OUTSIDE":
            raise ValueError(
                "Compartment order is incorrect. "
                "Outside must always be second compartment."
            )

        if self.time is not None and self.fraction is not None:
            if len(self.time) != len(self.fraction):
                raise ValueError("Time and fraction lists must be of equal length")

    def __repr__(self) -> str:
        """Return a detailed string representation of the WallVents."""
        return (
            f"WallVents("
            f"id='{self.id}', "
            f"comps_ids={self.comps_ids}, "
            f"bottom={self.bottom}, height={self.height}, width={self.width}, "
            f"face='{self.face}', offset={self.offset}"
            f")"
        )

    def __str__(self) -> str:
        """Return a user-friendly string representation of the WallVents."""
        connection = f"{self.comps_ids[0]} ↔ {self.comps_ids[1]}"
        size_info = f"{self.width}x{self.height} m"
        position_info = f"bottom: {self.bottom} m"

        return f"Wall Vent '{self.id}': {connection}, {size_info}, {position_info}"

    def _repr_html_(self) -> str:
        """Return an HTML representation for Jupyter/interactive environments."""
        area = (getattr(self, "width", 0) or 0) * (getattr(self, "height", 0) or 0)
        face_str = getattr(self, "face", "Unknown")

        criterion_info = ""
        if hasattr(self, "open_close_criterion") and self.open_close_criterion:
            criterion_info = f"<div><strong>Control:</strong> {self.open_close_criterion} @ {getattr(self, 'set_point', 'N/A')}</div>"

        body_html = f"""
            <div class="pycfast-card-grid">
                <div><strong>Dimensions:</strong> {getattr(self, "width", "N/A")}×{getattr(self, "height", "N/A")} m</div>
                <div><strong>Area:</strong> {area:.2f} m²</div>
                <div><strong>Wall face:</strong> {face_str}</div>
                <div><strong>Bottom height:</strong> {getattr(self, "bottom", "N/A")} m</div>
                <div><strong>Offset:</strong> {getattr(self, "offset", "N/A")} m</div>
                {criterion_info}
            </div>
        """

        return build_card(
            icon="🚪",
            gradient="linear-gradient(135deg, #fd79a8, #e84393)",
            title=f"Wall Vent: {self.id}",
            subtitle=f"<strong>{self.comps_ids[0]} ↔ {self.comps_ids[1]}</strong>",
            accent_color="#e84393",
            body_html=body_html,
        )

    def __getitem__(self, key: str) -> Any:
        """Get vent property by name for dictionary-like access."""
        if not hasattr(self, key):
            raise KeyError(f"Property '{key}' not found in WallVents.")
        return getattr(self, key)

    def __setitem__(self, key: str, value: Any) -> None:
        """Set vent property by name for dictionary-like assignment.

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
            raise KeyError(f"Cannot set '{key}'. Property does not exist in WallVents.")
        old_value = getattr(self, key)
        setattr(self, key, value)
        try:
            self._validate()
        except Exception:
            setattr(self, key, old_value)
            raise

    def to_input_string(self) -> str:
        """
        Generate CFAST input file string for this wall vent.

        Returns
        -------
        str
            Formatted string ready for inclusion in CFAST input file.

        Examples
        --------
        >>> vent = WallVents("DOOR1", ["RM1", "RM2"], 0.0, 2.0, 0.9, "RIGHT", 1.0)
        >>> print(vent.to_input_string())
        &VENT TYPE = 'WALL' ID = 'DOOR1' COMP_IDS = 'RM1', 'RM2' BOTTOM = 0.0 ...
        """
        rec = NamelistRecord("VENT")
        rec.add_field("TYPE", "WALL")
        rec.add_field("ID", self.id)
        rec.add_list_field("COMP_IDS", self.comps_ids)
        rec.add_field("BOTTOM", self.bottom)
        rec.add_field("HEIGHT", self.height)
        rec.add_field("WIDTH", self.width)

        if self.open_close_criterion is not None:
            rec.add_field("CRITERION", self.open_close_criterion)
            rec.add_field("SETPOINT", self.set_point)
            rec.add_field("DEVC_ID", self.device_id)
            rec.add_field("PRE_FRACTION", self.pre_fraction)
            rec.add_field("POST_FRACTION", self.post_fraction)

        if self.time is not None and self.fraction is not None:
            rec.add_list_field("T", self.time)
            rec.add_list_field("F", self.fraction)

        rec.add_field("FACE", self.face)
        rec.add_field("OFFSET", self.offset)

        return rec.build()
