"""
Visualizations module for CFAST simulations.

This module provides the Visualization class for defining Smokeview
visualization outputs (2-D slices, 3-D slices, and isosurfaces) in a
CFAST simulation.
"""

from __future__ import annotations

import warnings

from ._base_component import CFASTComponent
from .utils.namelist import NamelistRecord


class Visualization(CFASTComponent):
    """
    Represents a Smokeview visualization output in CFAST.

    Calculated results from a CFAST simulation can be visualized using
    Smokeview. In addition to a simplified view of the layer temperatures
    and vent flows, more detailed estimates of gas temperature and gas
    velocity can be visualized.

    There are three types of visualizations:

    - **2-D slice** (``&SLCF DOMAIN = '2-D'``): a single plane slice of
      temperature at the position and axis specified. The slice is placed
      perpendicular to the selected axis (the Y-Z plane for the X axis,
      the X-Z plane for the Y axis, and the X-Y plane for the Z axis).
    - **3-D slice** (``&SLCF DOMAIN = '3-D'``): a set of three animated
      slices whose position can be moved along their respective axes.
    - **Isosurface** (``&ISOF``): a fixed 3-D surface where the gas
      temperature is equal to the value specified.

    Visualizations can be placed in a single compartment or, when no
    compartment is specified, at the same position and axis in all
    compartments.

    Parameters
    ----------
    viz_type : str
        Type of visualization. Options: "2-D" for a single plane slice,
        "3-D" for a set of three animated slices, "ISOSURFACE" for a fixed
        3-D surface of constant gas temperature.
    comp_id : str | None
        Compartment ID where the visualization is placed. If None (default),
        the visualization applies to all compartments. Validated against the
        model compartments in CFASTModel._validate_dependencies.
    plane : str | None
        Axis perpendicular to the slice ("X", "Y" or "Z"). Required for
        2-D slices, must be None otherwise.
    position : float | None
        Position (m) along the specified axis where the slice is placed,
        measured from the compartment origin. Required for 2-D slices,
        must be None otherwise.
    value : float | None
        Gas temperature (°C) of the isosurface. Required for isosurfaces,
        must be None otherwise.

    Raises
    ------
    TypeError
        If viz_type, comp_id or plane are not strings, or if position or
        value are not numeric when provided.
    ValueError
        If viz_type is not "2-D", "3-D" or "ISOSURFACE", if comp_id is an
        empty string, if plane or position are missing for a 2-D slice,
        if plane is not "X", "Y" or "Z", if position is negative, or if
        value is missing for an isosurface.

    Notes
    -----
    By default, slice files are generated with a grid of 50 data points in
    each direction for each compartment specified. The grid spacing can be
    adjusted individually by compartment with the ``grid`` parameter of
    :class:`Compartment`.

    Examples
    --------
    Create a 2-D temperature slice in all compartments:

    >>> slice_2d = Visualization.slice_2d(plane="X", position=2.5)

    Create a 3-D slice in a single compartment:

    >>> slice_3d = Visualization.slice_3d(comp_id="ROOM1")

    Create an isosurface of gas temperature at 305 °C:

    >>> isosurface = Visualization.isosurface(value=305.0)
    """

    VALID_TYPES: frozenset[str] = frozenset({"2-D", "3-D", "ISOSURFACE"})
    VALID_PLANES: frozenset[str] = frozenset({"X", "Y", "Z"})

    def __init__(
        self,
        viz_type: str,
        comp_id: str | None = None,
        plane: str | None = None,
        position: float | None = None,
        value: float | None = None,
    ):
        self.viz_type = viz_type  # "2-D", "3-D" or "ISOSURFACE"
        self.comp_id = comp_id  # None means all compartments, to be validated in _validate_dependencies in CFASTModel
        self.plane = plane
        self.position = position
        self.value = value

        self._validate()
        self._initialized = True

    def _validate(self) -> None:
        """Validate the current state of the visualization attributes.

        Raises
        ------
        TypeError
            If viz_type, comp_id or plane are not strings, or if position
            or value are not numeric when provided.
        ValueError
            If any attribute violates the constraints.

        Warns
        -----
        UserWarning
            If plane, position or value are provided for a visualization
            type that does not use them (should be None).
        """
        if not isinstance(self.viz_type, str):
            raise TypeError(
                f"Visualization: viz_type must be a str, got {type(self.viz_type).__name__}."
            )
        if self.viz_type not in self.VALID_TYPES:
            raise ValueError(
                f"Visualization: viz_type='{self.viz_type}' must be one of {set(self.VALID_TYPES)}."
            )

        if self.comp_id is not None and (
            not isinstance(self.comp_id, str) or not self.comp_id
        ):
            raise ValueError(
                "Visualization: comp_id must be a non-empty string or None."
            )

        if self.viz_type == "2-D":
            if self.plane is None:
                raise ValueError("Visualization: 2-D slice requires a plane value.")
            if not isinstance(self.plane, str):
                raise TypeError(
                    f"Visualization: plane must be a str, got {type(self.plane).__name__}."
                )
            if self.plane not in self.VALID_PLANES:
                raise ValueError(
                    f"Visualization: plane='{self.plane}' must be one of {set(self.VALID_PLANES)}."
                )
            if self.position is None:
                raise ValueError("Visualization: 2-D slice requires a position value.")
            if not isinstance(self.position, (int, float)):
                raise TypeError(
                    f"Visualization: position must be a float, got {type(self.position).__name__}."
                )
            if self.position < 0:
                raise ValueError(
                    f"Visualization: position={self.position} must be >= 0 for 2-D slices."
                )
            if self.value is not None:
                warnings.warn(
                    "Visualization: value should be None for 2-D slices.",
                    UserWarning,
                    stacklevel=2,
                )
        elif self.viz_type == "3-D":
            if any(v is not None for v in (self.plane, self.position, self.value)):
                warnings.warn(
                    "Visualization: plane, position and value should be None for 3-D slices.",
                    UserWarning,
                    stacklevel=2,
                )
        else:  # ISOSURFACE
            if self.value is None:
                raise ValueError("Visualization: isosurface requires a value.")
            if not isinstance(self.value, (int, float)):
                raise TypeError(
                    f"Visualization: value must be a float, got {type(self.value).__name__}."
                )
            if self.plane is not None or self.position is not None:
                warnings.warn(
                    "Visualization: plane and position should be None for isosurfaces.",
                    UserWarning,
                    stacklevel=2,
                )

    def __repr__(self) -> str:
        """Return a detailed string representation of the Visualization."""
        return (
            f"Visualization("
            f"viz_type='{self.viz_type}', "
            f"comp_id={self.comp_id!r}, "
            f"plane={self.plane!r}, "
            f"position={self.position}, "
            f"value={self.value}"
            ")"
        )

    def __str__(self) -> str:
        """Return a user-friendly string representation of the Visualization."""
        compartment = self.comp_id if self.comp_id is not None else "all compartments"
        if self.viz_type == "2-D":
            details = f"plane {self.plane} at {self.position} m"
        elif self.viz_type == "3-D":
            details = "animated slices"
        else:  # ISOSURFACE
            details = f"{self.value} °C"
        return f"Visualization ({self.viz_type}): {details} in {compartment}"

    def to_input_string(self) -> str:
        """
        Convert the visualization to a formatted string for CFAST input file.

        Returns
        -------
        str
            Formatted string ready for inclusion in CFAST input file.

        Examples
        --------
        >>> slice_2d = Visualization.slice_2d(plane="X", position=2.5)
        >>> print(slice_2d.to_input_string())
        &SLCF DOMAIN = '2-D' PLANE = 'X' POSITION = 2.5 /

        >>> slice_3d = Visualization.slice_3d(comp_id="ROOM1")
        >>> print(slice_3d.to_input_string())
        &SLCF COMP_ID = 'ROOM1' DOMAIN = '3-D' /

        >>> isosurface = Visualization.isosurface(value=305.0)
        >>> print(isosurface.to_input_string())
        &ISOF VALUE = 305.0 /
        """
        if self.viz_type == "ISOSURFACE":
            rec = NamelistRecord("ISOF")
            rec.add_field("COMP_ID", self.comp_id)
            rec.add_field("VALUE", self.value)
            return rec.build()

        rec = NamelistRecord("SLCF")
        rec.add_field("COMP_ID", self.comp_id)
        rec.add_field("DOMAIN", self.viz_type)
        if self.viz_type == "2-D":
            rec.add_field("PLANE", self.plane)
            rec.add_field("POSITION", self.position)
        return rec.build()

    @classmethod
    def slice_2d(
        cls, plane: str, position: float = 0.0, comp_id: str | None = None
    ) -> Visualization:
        """
        Create a 2-D slice visualization of gas temperature.

        Parameters
        ----------
        plane : str
            Axis perpendicular to the slice ("X", "Y" or "Z"). The slice is
            placed perpendicular to the selected axis.
        position : float
            Position (m) along the specified axis where the slice is placed,
            measured from the compartment origin. Default: 0.0.
        comp_id : str | None
            Compartment identifier. If None (default), the slice is placed
            at the same position and axis in all compartments.

        Returns
        -------
        Visualization
            Configured visualization instance for a 2-D slice.

        Examples
        --------
        >>> slice_2d = Visualization.slice_2d(plane="Y", position=1.2, comp_id="ROOM1")
        """
        return cls(viz_type="2-D", comp_id=comp_id, plane=plane, position=position)

    @classmethod
    def slice_3d(cls, comp_id: str | None = None) -> Visualization:
        """
        Create a 3-D slice visualization of gas temperature.

        Parameters
        ----------
        comp_id : str | None
            Compartment identifier. If None (default), a 3-D slice is
            created in all compartments.

        Returns
        -------
        Visualization
            Configured visualization instance for a 3-D slice.

        Examples
        --------
        >>> slice_3d = Visualization.slice_3d(comp_id="ROOM1")
        """
        return cls(viz_type="3-D", comp_id=comp_id)

    @classmethod
    def isosurface(cls, value: float, comp_id: str | None = None) -> Visualization:
        """
        Create an isosurface visualization of gas temperature.

        Parameters
        ----------
        value : float
            Gas temperature (°C) of the isosurface.
        comp_id : str | None
            Compartment identifier. If None (default), the isosurface is
            created in all compartments.

        Returns
        -------
        Visualization
            Configured visualization instance for an isosurface.

        Examples
        --------
        >>> isosurface = Visualization.isosurface(value=305.0, comp_id="ROOM1")
        """
        return cls(viz_type="ISOSURFACE", comp_id=comp_id, value=value)
