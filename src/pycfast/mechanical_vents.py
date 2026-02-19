"""
Mechanical ventilation system definition module for CFAST simulations.

This module provides the MechanicalVents class for defining HVAC systems,
fans, and forced ventilation that actively move air between compartments
or to/from the exterior.
"""

from __future__ import annotations

from typing import Any

from .utils.namelist import NamelistRecord
from .utils.theme import build_card


class MechanicalVents:
    """
    Represents a mechanical ventilation system in a CFAST simulation.

    Fan-duct systems are commonly used in buildings for heating, ventilation, air
    conditioning, pressurization, and exhaust. CFAST models mechanical ventilation
    in terms of user-specified volume flows at various points in the compartment.
    The model does not include duct work or fan curves, and thus mechanical
    ventilation connections are simply described by the connections to the two
    compartments and a fan whose throughput is a constant volumetric flow up to a
    user-specified pressure drop across the fan, dropping to zero at high backwards
    pressure on the fan.

    CFAST does not include provisions for reverse flow through a fan, or a fan curve.
    Rather, you may specify a pressure above which the flow linearly decreases to zero.
    A hyperbolic tangent function is used to ensure a smooth transition from full flow
    at the "Begin Drop Off Pressure" to zero flow at the "Zero Flow Pressure".

    For mechanical vents, there are two species that can be filtered out of the gas
    flow: soot and the user-defined trace species. Filters are applied only to fan
    openings. By default, there is no filtering applied; that is, all of the soot
    and trace species mass in the vent flow is passed through the vent.

    Vents in CFAST can be opened or closed at user-specified times or by a
    user-specified target's surface temperature or incident heat flux. CFAST assumes
    a linear transition between time points for time-based opening changes. For
    condition-based opening changes, the transition from the pre-activation fraction
    to the post-activation fraction is assumed to occur over one second beginning
    when the specified set point value is reached.

    Parameters
    ----------
    id : str
        The selected name must be unique (i.e., not the same as another mechanical
        ventilation system in the same simulation).
    comps_ids : list[str]
        List containing the compartment from which the fan flow originates (first)
        and the compartment to which the fan flow terminates (second).
    area : list[float]
        Cross-sectional area of the opening for each compartment connection.
        Default units: m², default value: [0, 0] m².
    heights : list[float]
        Height of the midpoint of the duct opening above the floor for each
        compartment connection. Default units: m, default value: [0, 0] m.
    orientations : list[str]
        Flow orientation for each connection. A horizontal diffuser implies vertical
        flow through the ceiling or floor of the compartment. A vertical diffuser
        implies horizontal flow through a wall of the compartment.
        Default value: ["VERTICAL", "VERTICAL"].
    flow : float
        Constant flow rate of the fan. Default units: m³/s, default value: 0 m³/s.
    cutoffs : list[float]
        Pressure control values: [Begin Drop Off Pressure, Zero Flow Pressure].
        Above Begin Drop Off Pressure, the flow begins a drop-off to zero. The
        pressure above which the flow is zero is the Zero Flow Pressure.
        Default units: Pa, default values: [200, 300] Pa.
    offsets : list[float]
        For visualization only, the horizontal distances between the center of the
        vent and the origin of the X and Y axes in the first compartment. Format:
        [x_offset, y_offset]. Default units: m, default value: [0, 0] m.
    filter_time : float
        Time during the simulation at which the mechanical vent filtering begins.
        Default units: s, default value: 0 s.
    filter_efficiency : float
        Flow through mechanical vents may include filtering that removes a
        user-specified portion of soot and trace species mass from the flow through
        the vent. Specified as a fraction (0-1). Default value: 0 (no filtering).
    open_close_criterion : str, optional
        The opening/closing can be controlled by a user-specified time, or by a
        user-specified target's surface temperature or incident heat flux.
        Options: "TIME", "TEMPERATURE", "FLUX".
    time : list[float], optional
        Time during the simulation at which to begin or end a change in the open
        fraction. For time-based opening changes, this is a series of time points
        associated with opening fractions. Default units: s, default value: 0 s.
    fraction : list[float], optional
        Fraction between 0 and 1 of the vent width to indicate the vent is closed,
        partially-open, or fully-open at the associated time point.
        Default value: 1 (fully open).
    set_point : float, optional
        The critical value at which the vent opening change will occur. If it is
        less than or equal to zero, the default value of zero is taken. Can be
        temperature (°C) or flux (kW/m²) depending on criterion.
    device_id : str, optional
        User-specified target used to calculate surface temperature or incident
        heat flux to trigger a vent opening change. Target placement is specified
        by the user as part of the associated target definition.
    pre_fraction : float, optional
        Fraction between 0 and 1 of the vent width to indicate the vent is
        partially open at the start of the simulation. Default value: 1 (fully open).
    post_fraction : float, optional
        Opening fraction at the end of the simulation. The transition from the
        pre-activation fraction to the post-activation fraction is assumed to occur
        over one second beginning when the specified set point value is reached.
        Default value: 1 (fully open).

    Examples
    --------
    Create a supply air system:

    >>> supply_fan = MechanicalVents(
    ...     id="SUPPLY_1",
    ...     comps_ids=["OUTSIDE", "ROOM1"],
    ...     area=[0.1, 0.1],              # 0.1 m² grilles
    ...     heights=[3.0, 2.8],           # Near ceiling
    ...     orientations=["HORIZONTAL", "HORIZONTAL"],
    ...     flow=0.5,                     # 0.5 m³/s supply
    ...     cutoffs=[200, 300],           # Standard pressure cutoffs
    ...     offsets=[0, 1.0],             # Positions along walls
    ...     filter_time=0,                # Start filtering immediately
    ...     filter_efficiency=0.0         # No filtration
    ... )

    Create an exhaust fan with time-based control:

    >>> exhaust_fan = MechanicalVents(
    ...     id="EXHAUST_1",
    ...     comps_ids=["KITCHEN", "OUTSIDE"],
    ...     area=[0.05, 0.05],            # Smaller exhaust grilles
    ...     heights=[2.5, 0],             # Kitchen ceiling to outside
    ...     flow=-0.3,                    # Negative for exhaust
    ...     time=[0, 300, 600],           # Control times
    ...     fraction=[0, 1, 0]            # Off, on, off sequence
    ... )
    """

    def __init__(
        self,
        id: str,
        comps_ids: list[str],
        area: list[float] | None = None,
        heights: list[float] | None = None,
        orientations: list[str] | None = None,
        flow: float = 0,
        cutoffs: list[float] | None = None,
        offsets: list[float] | None = None,
        filter_time: float = 0,
        filter_efficiency: float = 0,
        open_close_criterion: str | None = None,
        time: list[float] | None = None,
        fraction: list[float] | None = None,
        set_point: float | None = None,
        device_id: str | None = None,
        pre_fraction: float | None = 1,
        post_fraction: float | None = 1,
    ):
        if area is None:
            area = [0, 0]
        if heights is None:
            heights = [0, 0]
        if orientations is None:
            orientations = ["VERTICAL", "VERTICAL"]
        if cutoffs is None:
            cutoffs = [200, 300]
        if offsets is None:
            offsets = [0, 0]

        self.id = id
        self.comps_ids = comps_ids
        self.area = area
        self.heights = heights
        self.orientations = orientations
        self.flow = flow
        self.cutoffs = cutoffs
        self.offsets = offsets
        self.filter_time = filter_time
        self.filter_efficiency = filter_efficiency
        self.open_close_criterion = open_close_criterion
        self.time = time
        self.fraction = fraction
        self.set_point = set_point
        self.device_id = device_id
        self.pre_fraction = pre_fraction
        self.post_fraction = post_fraction

        self._validate()

    def _validate(self) -> None:
        """Validate the current state of the mechanical vent attributes.

        Raises
        ------
        ValueError
            If any attribute violates the constraints.
        """
        if len(self.comps_ids) != 2:
            raise ValueError("comps_ids must contain exactly 2 compartment IDs.")
        if len(self.area) != 2:
            raise ValueError("area must have exactly 2 elements for each compartment.")
        if len(self.heights) != 2:
            raise ValueError(
                "heights must have exactly 2 elements for each compartment."
            )
        if len(self.orientations) != 2:
            raise ValueError(
                "orientations must have exactly 2 elements for each compartment."
            )
        if len(self.cutoffs) != 2:
            raise ValueError(
                "cutoffs must have exactly 2 elements for each compartment."
            )
        if self.cutoffs[0] < 0 or self.cutoffs[1] < 0:
            raise ValueError("cutoffs must be non-negative.")
        if self.cutoffs[1] < self.cutoffs[0]:
            raise ValueError(
                "Zero flow pressure must be greater than or equal to "
                "begin drop off pressure."
            )
        if len(self.offsets) != 2:
            raise ValueError("offsets must have exactly 2 elements for x, y location.")
        if self.time is not None and self.fraction is not None:
            if len(self.time) != len(self.fraction):
                raise ValueError("Time and fraction lists must be of equal length")

    def __repr__(self) -> str:
        """Return a detailed string representation of the MechanicalVents."""
        return (
            f"MechanicalVents("
            f"id='{self.id}', "
            f"comps_ids={self.comps_ids}, "
            f"flow={self.flow}, "
            f"area={self.area}, "
            f"heights={self.heights}"
            f")"
        )

    def __str__(self) -> str:
        """Return a user-friendly string representation of the MechanicalVents."""
        connection = f"{self.comps_ids[0]} -> {self.comps_ids[1]}"
        flow_str = f"flow: {self.flow} m³/s"
        return f"Mechanical Vent '{self.id}': {connection}, {flow_str}"

    def _repr_html_(self) -> str:
        """Return an HTML representation for Jupyter/interactive environments."""
        flow_val = getattr(self, "flow", 0)
        if flow_val > 0:
            flow_str = f"+{flow_val} m³/s (Supply)"
            flow_color = "#00b894"
        elif flow_val < 0:
            flow_str = f"{flow_val} m³/s (Exhaust)"
            flow_color = "#e17055"
        else:
            flow_str = "0 m³/s (Off)"
            flow_color = "#636e72"

        filter_info = ""
        if hasattr(self, "filter_time") and self.filter_time:
            eff = getattr(self, "filter_efficiency", 0)
            filter_info = (
                f"<div><strong>Filter:</strong> {eff}% eff, τ={self.filter_time}s</div>"
            )

        body_html = f"""
            <div style="font-size: 0.9em; margin-bottom: 8px; font-weight: bold; color: {flow_color};">
                {flow_str}
            </div>
            <div class="pycfast-card-grid">
                <div><strong>Areas:</strong> {getattr(self, "area", "N/A")} m²</div>
                <div><strong>Heights:</strong> {getattr(self, "heights", "N/A")} m</div>
                <div><strong>Orientations:</strong> {getattr(self, "orientations", "N/A")}</div>
                <div><strong>Cutoffs:</strong> {getattr(self, "cutoffs", "N/A")} Pa</div>
                {filter_info}
            </div>
        """

        return build_card(
            icon="🌀",
            gradient=f"linear-gradient(135deg, {flow_color}, {flow_color}aa)",
            title=f"Mechanical Vent: {self.id}",
            subtitle=f"<strong>{self.comps_ids[0]} → {self.comps_ids[1]}</strong>",
            accent_color=flow_color,
            body_html=body_html,
        )

    def __getitem__(self, key: str) -> Any:
        """Get vent property by name for dictionary-like access."""
        if not hasattr(self, key):
            raise KeyError(f"Property '{key}' not found in MechanicalVents.")
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
            raise KeyError(
                f"Cannot set '{key}'. Property does not exist in MechanicalVents."
            )
        old_value = getattr(self, key)
        setattr(self, key, value)
        try:
            self._validate()
        except Exception:
            setattr(self, key, old_value)
            raise

    def to_input_string(self) -> str:
        """
        Generate CFAST input file string for this mechanical vent.

        Returns
        -------
        str
            Formatted string ready for inclusion in CFAST input file.

        Examples
        --------
        >>> vent = MechanicalVents("FAN1", ["OUT", "RM1"], [0.1, 0.1],
        ...                       [3, 2.8], ["HORIZ", "HORIZ"], 0.5,
        ...                       [100, 100], [0, 1], 0, 0)
        >>> print(vent.to_input_string())
        &VENT TYPE = 'MECHANICAL' ID = 'FAN1' COMP_IDS = 'OUT', 'RM1' ...
        """
        rec = NamelistRecord("VENT")
        rec.add_field("TYPE", "MECHANICAL")
        rec.add_field("ID", self.id)
        rec.add_list_field("COMP_IDS", self.comps_ids)
        rec.add_list_field("AREAS", self.area)
        rec.add_list_field("HEIGHTS", self.heights)
        rec.add_list_field("ORIENTATIONS", self.orientations)
        rec.add_field("FLOW", self.flow)
        rec.add_list_field("CUTOFFS", self.cutoffs)
        rec.add_list_field("OFFSETS", self.offsets)

        if self.open_close_criterion is not None:
            rec.add_field("CRITERION", self.open_close_criterion)
            rec.add_numeric_field("SETPOINT", self.set_point)
            rec.add_field("DEVC_ID", self.device_id)
            rec.add_field("PRE_FRACTION", self.pre_fraction)
            rec.add_field("POST_FRACTION", self.post_fraction)

        rec.add_list_field("T", self.time)
        rec.add_list_field("F", self.fraction)
        rec.add_field("FILTER_TIME", self.filter_time)
        rec.add_field("FILTER_EFFICIENCY", self.filter_efficiency)

        return rec.build()
