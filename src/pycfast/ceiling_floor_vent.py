"""
Ceiling/Floor Vents definition module for CFAST simulations.

This module provides the CeilingFloorVent class for defining vertical
flow vent connections between compartments.
"""

from __future__ import annotations

import warnings

from ._base_component import CFASTComponent
from .utils.namelist import NamelistRecord


class CeilingFloorVent(CFASTComponent):
    """
    Represents vertical flow vent connections between compartments.

    Examples of these openings are scuttles in a ship, or a hole in the roof of a residence.
    Connections can exist between compartments or between a compartment and the outdoors.
    Combined buoyancy and pressure-driven flow through a vertical flow vent is possible when
    the connected spaces adjacent to the vent are filled with gases of different density in
    an unstable configuration, with the density of the top space greater than that of the
    bottom space. With a moderate cross-vent pressure difference, the instability leads to a
    bi-directional flow between the two spaces. For relatively large cross-vent pressure
    difference the flow through the vent is unidirectional.

    Parameters
    ----------
    id : str
        The selected name must be unique (i.e., not the same as another vent in the same
        simulation).
    comps_ids : list[str]
        List containing [top_compartment, bottom_compartment] IDs. Top compartment is where
        the vent is in the floor, bottom compartment is the adjacent compartment where the
        vent is in the ceiling.
    area : float
        Cross-sectional area of the vent opening. Default units: m², default value: 0 m².
    type : str, optional
        Type of ceiling/floor vent. Options: "FLOOR" or "CEILING".
    shape : str, optional
        The shape factor changes the calculation of the effective diameter of the vent and
        flow coefficients for flow through the vent. Options: "ROUND" or "SQUARE".
    offsets : list[float], optional
        For visualization only, the horizontal distances between the center of the vent and
        the origin of the X and Y axes in the upper compartment. Format: [x_offset, y_offset].
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
        fraction to the post-activation fraction is assumed to occur over one second beginning
        when the specified set point value is reached. Default value: 1 (fully open).

    Notes
    -----
    CFAST assumes a linear transition between time points. If the initial time specified
    for a time-changing opening fraction is non-zero, the vent is assumed to be open at
    the initial value of the open fraction from the beginning of the simulation up to and
    including the time associated with the initial value of the opening fraction.

    CFAST allows only a single ceiling/floor connection between any pair of compartments
    included in a simulation because the empirical correlation governing the flow was
    developed using only a single opening between connected compartments.

    Vertical connections can only be created between compartments that could be physically
    stacked based on specified floor and ceiling elevations for the compartments. Some
    overlap between the absolute floor height of one compartment and the absolute ceiling
    height of another compartment is allowed. However, whether the compartments are stacked
    or overlap somewhat, the ceiling/floor absolute elevations must be within 0.01 m of
    each other. The check is not done when the connection is to the outside.

    Examples
    --------
    Create a ceiling/floor vent connection:

    >>> vent = CeilingFloorVent(
    ...     id="HOLE1",
    ...     comps_ids=["UPPER_RM", "LOWER_RM"],
    ...     area=1.0,
    ...     shape="ROUND",
    ...     offsets=[2.0, 3.0]
    ... )
    """

    def __init__(
        self,
        id: str,
        comps_ids: list[str],  # [top_compartment, bottom_compartment]
        area: float = 0,
        type: str = "FLOOR",  # "FLOOR" or "CEILING" this doesn't seem to change final results
        shape: str = "ROUND",  # "ROUND" or "SQUARE"
        offsets: list[float] | None = None,  # [x, y] position in meters
        open_close_criterion: str | None = None,  # can be "TIME","FLUX","TEMPERATURE"
        time: list[float] | None = None,  # Time series for opening changes
        fraction: list[float] | None = None,  # Opening fraction (0=closed, 1=open)
        set_point: float
        | None = None,  # Required value for vent opening change (temp °C or flux kW/m²)
        device_id: str | None = None,  # Trigger target ID for condition control
        pre_fraction: float | None = 1,  # Pre-activation fraction (default: 1)
        post_fraction: float | None = 1,  # Post-activation fraction (default: 1)
    ):
        if offsets is None:
            offsets = [0, 0]

        self.id = id
        self.type = type
        self.comps_ids = comps_ids
        self.area = area
        self.shape = shape
        self.offsets = offsets
        self.open_close_criterion = open_close_criterion
        self.time = time
        self.fraction = fraction
        self.set_point = set_point
        self.device_id = device_id
        self.pre_fraction = pre_fraction
        self.post_fraction = post_fraction

        self._validate()
        self._initialized = True

    def _validate(self) -> None:
        """Validate the current state of the ceiling/floor vent attributes.

        Raises
        ------
        TypeError
            If list parameters (comps_ids, offsets, time, fraction) are not lists.
        ValueError
            If any attribute violates the constraints.

        Warns
        -----
        UserWarning
            If area is 0 (no flow will occur through this vent).
        """
        for param, list_val in (
            ("comps_ids", self.comps_ids),
            ("offsets", self.offsets),
        ):
            if not isinstance(list_val, list):
                raise TypeError(
                    f"CeilingFloorVent '{self.id}': {param} must be a list, got {type(list_val).__name__}."
                )
        for param, opt_list_val in (
            ("time", self.time),
            ("fraction", self.fraction),
        ):
            if opt_list_val is not None and not isinstance(opt_list_val, list):
                raise TypeError(
                    f"CeilingFloorVent '{self.id}': {param} must be a list, got {type(opt_list_val).__name__}."
                )

        if len(self.comps_ids) != 2:
            raise ValueError("Ceiling/floor vent must connect exactly 2 compartments")

        if self.area < 0:
            raise ValueError(
                f"CeilingFloorVent '{self.id}': area must be non-negative, got {self.area}."
            )

        for label, frac_val in (
            ("pre_fraction", self.pre_fraction),
            ("post_fraction", self.post_fraction),
        ):
            if frac_val is not None and not 0.0 <= frac_val <= 1.0:
                raise ValueError(
                    f"CeilingFloorVent '{self.id}': {label}={frac_val} must be in [0, 1], got {frac_val}."
                )

        if self.fraction is not None:
            for i, f in enumerate(self.fraction):
                if not 0.0 <= f <= 1.0:
                    raise ValueError(
                        f"CeilingFloorVent '{self.id}': fraction[{i}]={f} must be in [0, 1], got {f}."
                    )

        if self.area == 0:
            warnings.warn(
                f"CeilingFloorVent '{self.id}': area=0 means no flow will occur through this vent, got area={self.area}.",
                UserWarning,
                stacklevel=2,
            )

        if self.offsets is not None and len(self.offsets) != 2:
            raise ValueError(
                f"CeilingFloorVent '{self.id}': offsets must be a list of two values [x_offset, y_offset], got {self.offsets}."
            )

        if self.type not in {"FLOOR", "CEILING"}:
            raise ValueError(
                f"CeilingFloorVent '{self.id}': type must be 'FLOOR' or 'CEILING', got '{self.type}'."
            )

        if self.shape not in {"ROUND", "SQUARE"}:
            raise ValueError(
                f"CeilingFloorVent '{self.id}': shape must be 'ROUND' or 'SQUARE', got '{self.shape}'."
            )

        if self.open_close_criterion is not None:
            valid_criteria = {"TIME", "TEMPERATURE", "FLUX"}
            if self.open_close_criterion not in valid_criteria:
                raise ValueError(
                    f"CeilingFloorVent '{self.id}': open_close_criterion must be one of {valid_criteria}, got '{self.open_close_criterion}'."
                )
            if (
                self.open_close_criterion in {"TEMPERATURE", "FLUX"}
                and self.set_point is None
            ):
                raise ValueError(
                    f"CeilingFloorVent '{self.id}': set_point must be specified when open_close_criterion is '{self.open_close_criterion}', got set_point={self.set_point}."
                )
            if (
                self.open_close_criterion in {"TEMPERATURE", "FLUX"}
                and self.device_id is None
            ):
                raise ValueError(
                    f"CeilingFloorVent '{self.id}': device_id must be specified when open_close_criterion is '{self.open_close_criterion}'."
                )
            if self.open_close_criterion == "TIME":
                if self.time is None or self.fraction is None:
                    raise ValueError(
                        f"CeilingFloorVent '{self.id}': time and fraction must be specified when open_close_criterion is 'TIME'."
                    )
                if len(self.time) != len(self.fraction):
                    raise ValueError(
                        f"CeilingFloorVent '{self.id}': time and fraction lists must be of equal length, got {len(self.time)} and {len(self.fraction)}."
                    )
                if any(t < 0 for t in self.time):
                    raise ValueError(
                        f"CeilingFloorVent '{self.id}': all time values must be non-negative, got {self.time}."
                    )
                if self.time != sorted(self.time):
                    raise ValueError(
                        f"CeilingFloorVent '{self.id}': time values must be monotonically increasing, got {self.time}."
                    )

    def __repr__(self) -> str:
        """Return a detailed string representation of the CeilingFloorVent."""
        return (
            f"CeilingFloorVent("
            f"id='{self.id}', "
            f"comps_ids={self.comps_ids}, "
            f"area={self.area}, type='{self.type}', shape='{self.shape}', "
            f"offsets={self.offsets}"
            ")"
        )

    def __str__(self) -> str:
        """Return a user-friendly string representation of the CeilingFloorVent."""
        connection = f"{self.comps_ids[0]} ↕ {self.comps_ids[1]}"
        area_info = f"area: {self.area} m²"
        shape_info = f"shape: {self.shape}"

        optional_info = []
        if self.open_close_criterion:
            optional_info.append(f"criterion: {self.open_close_criterion}")

        optional_str = f" ({', '.join(optional_info)})" if optional_info else ""

        return (
            f"Ceiling/Floor Vent '{self.id}': "
            f"{connection}, {area_info}, {shape_info}{optional_str}"
        )

    def to_input_string(self) -> str:
        """
        Generate CFAST input file string for this ceiling/floor vent.

        Returns
        -------
        str
            Formatted string ready for inclusion in CFAST input file.

        Examples
        --------
        >>> vent = CeilingFloorVent(
        ...     id="HOLE1",
        ...     comps_ids=["RM_UP", "RM_LOW"],
        ...     area=1.0,
        ...     shape="ROUND",
        ...     offsets=[0, 0]
        ... )
        >>> print(vent.to_input_string())
        &VENT TYPE = 'FLOOR' ID = 'HOLE1' COMP_IDS = 'RM_UP', 'RM_LOW' AREA = 1.0 SHAPE = 'ROUND' OFFSETS = 0, 0 /
        """
        rec = NamelistRecord("VENT")
        rec.add_field("TYPE", self.type)
        rec.add_field("ID", self.id)
        rec.add_list_field("COMP_IDS", self.comps_ids)
        rec.add_field("AREA", self.area)
        rec.add_field("SHAPE", self.shape)

        if self.open_close_criterion is not None:
            rec.add_field("CRITERION", self.open_close_criterion)
            if self.open_close_criterion in {"TEMPERATURE", "FLUX"}:
                rec.add_numeric_field("SETPOINT", self.set_point)
                rec.add_field("DEVC_ID", self.device_id)
                rec.add_field("PRE_FRACTION", self.pre_fraction)
                rec.add_field("POST_FRACTION", self.post_fraction)
            if self.open_close_criterion == "TIME":
                rec.add_list_field("T", self.time)
                rec.add_list_field("F", self.fraction)
        rec.add_list_field("OFFSETS", self.offsets)

        return rec.build()
