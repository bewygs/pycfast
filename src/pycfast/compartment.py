"""
Compartment definition module for CFAST simulations.

This module provides the Compartment class for defining the size, position,
materials of construction, and flow characteristics for the compartments in
the CFAST simulation.
"""

from __future__ import annotations

from ._base_component import CFASTComponent
from .utils.namelist import NamelistRecord


def _as_list(val: str | float | list | None) -> list:
    if val is None:
        return []
    return val if isinstance(val, list) else [val]


class Compartment(CFASTComponent):
    """
    Defines the size, position, materials of construction, and flow characteristics for compartments.

    Compartments are defined by their geometry and lining materials, which at a minimum
    require a width, depth, and height. The maximum number of compartments is 100. The
    usual assumption is that compartments are rectangular parallelepipeds, but other shapes
    can be modeled via equivalent floor area and perimeter. If desired, compartments can be
    prescribed by the cross-sectional area of the compartment as a function of height from
    floor to ceiling for other shapes. The absolute position of the compartment with respect
    to a single structure reference point can be defined to ease visualization or to allow
    exact placement of vents and surfaces relative to other compartments in a detailed
    calculation.

    Parameters
    ----------
    id : str, optional
        Compartments are identified by a unique name, for which spaces are allowed.
        Default value: ``'Comp 1'``.
    width : float, optional
        Compartment width as measured on the x axis from the origin of the compartment.
        Default units: m, default value: 3.6 m.
    depth : float, optional
        Compartment depth as measured on the y axis from the origin of the compartment.
        Default units: m, default value: 2.4 m.
    height : float, optional
        Compartment height as measured on the z axis from the origin of the compartment.
        Default units: m, default value: 2.4 m.
    ceiling_mat_id : str or list[str], optional
        Material ID(s) of the ceiling, referring to the ``id`` of a :class:`Material`.
        As many as three layers of materials can make up the ceiling, with the surface
        layer specified first. Default value: off.
    ceiling_thickness : float or list[float], optional
        Thickness of each of the layers of the ceiling. Must match the number of
        materials in ``ceiling_mat_id``. Default units: m, default value: the
        ``thickness`` of each material.
    wall_mat_id : str or list[str], optional
        Material ID(s) of the walls, referring to the ``id`` of a :class:`Material`.
        As many as three layers of materials can make up the walls, with the surface
        layer specified first. Default value: off.
    wall_thickness : float or list[float], optional
        Thickness of each of the layers of the walls. Must match the number of
        materials in ``wall_mat_id``. Default units: m, default value: the
        ``thickness`` of each material.
    floor_mat_id : str or list[str], optional
        Material ID(s) of the floor, referring to the ``id`` of a :class:`Material`.
        As many as three layers of materials can make up the floor, with the surface
        layer specified first. Default value: off.
    floor_thickness : float or list[float], optional
        Thickness of each of the layers of the floor. Must match the number of
        materials in ``floor_mat_id``. Default units: m, default value: the
        ``thickness`` of each material.
    origin_x : float, optional
        X coordinate of the lower, left, front corner of the compartment. All coordinates
        for all compartments must be greater than or equal to zero to facilitate
        visualization by Smokeview. Default units: m, default value: 0 m.
    origin_y : float, optional
        Y coordinate of the lower, left, front corner of the compartment. All coordinates
        for all compartments must be greater than or equal to zero to facilitate
        visualization by Smokeview. Default units: m, default value: 0 m.
    origin_z : float, optional
        Z coordinate of the lower, left, front corner of the compartment. All coordinates
        for all compartments must be greater than or equal to zero to facilitate
        visualization by Smokeview. Default units: m, default value: 0 m.
    shaft : bool, optional
        Conditions in the compartment are calculated as a single well-mixed zone. A single
        zone approximation may be appropriate for compartments away from the fire, where
        the two-zone layer stratification is less pronounced than in compartments near the
        fire, or in situations where the stratification does not occur, such as elevators,
        shafts, or stairwells. Cannot be combined with ``hall``. Default value: False.
    hall : bool, optional
        Conditions in the compartment are calculated with the normal two-zone approach,
        but ceiling jet temperatures are calculated with an empirical model that constrains
        the upper layer to a narrow passage. This feature will impact, for example,
        detectors, sprinklers, and targets near the ceiling in corridors. Cannot be
        combined with ``shaft``. Default value: False.
    leak_area_ratio : tuple[float, float], optional
        Leakage area ratio input as the leakage area per unit wall and floor area. CFAST
        uses it to automatically calculate leakage between the compartment and the
        outdoors. Format: (wall, floor). Default units: m²/m², default value: (0, 0).
    cross_sect_areas : list[float], optional
        Cross-sectional area at the corresponding height, for a compartment whose
        horizontal cross-sectional area is a function of height. Must have the same
        length as ``cross_sect_heights``. Default units: m².
    cross_sect_heights : list[float], optional
        Height off the floor of the compartment. Cross-sectional area values should be
        input in order by ascending height. Default units: m.
    grid : tuple[int, int, int], optional
        Number of Smokeview sampling points along x, y, and z axes. These parameters are
        purely for visualization within Smokeview for depicting plume and ceiling jet
        profiles. Specifying a larger number of data points can dramatically slow program
        execution since the gas temperature and velocity are evaluated at each grid
        location every time a Smokeview output is specified. Format: (x, y, z). Default
        value: (50, 50, 50).

    Notes
    -----
    To calculate heat loss through the ceiling, walls, and floor of a compartment, material
    properties must be specified. Separate properties can be specified for the ceiling and
    floor, but the four walls all must have the same set of properties. If the
    thermophysical properties of the surfaces are not specified, they will be treated as
    adiabatic, i.e. no heat transfer. The back surfaces of compartments are assumed to be
    exposed to ambient conditions.

    The normal two-zone model is used by default; the shaft (single-zone) and corridor
    options are off.

    For a variable cross-sectional area, if the first height value is not zero (i.e., at
    floor level), the cross-sectional area is assumed constant from the floor to the height
    specified in the first cross-sectional area value. Similarly, if the last height value is
    not at the specified ceiling height, the cross-sectional area is assumed constant from
    the height specified in the last cross-sectional area value to the ceiling. Between any
    two adjacent cross-sectional area data values, the area is assumed to be a pyramidal
    section (which by definition maintains the same width to depth aspect ratio for the
    compartment from floor to ceiling).

    Typical leakage areas of walls and floors are given in the *Handbook of Smoke Control
    Engineering* (Klote et al., 2012).

    Adapted from the `CFAST User's Guide <https://pages.nist.gov/cfast/>`__.

    Examples
    --------
    Create a compartment following CFAST conventions:

    >>> room = Compartment(
    ...     id="BEDROOM",
    ...     width=3.5,
    ...     depth=4.0,
    ...     height=2.4,
    ...     ceiling_mat_id="GYPSUM",
    ...     ceiling_thickness=0.016,
    ...     wall_mat_id="GYPSUM",
    ...     wall_thickness=0.016,
    ...     floor_mat_id="CONCRETE",
    ...     floor_thickness=0.10,
    ...     origin_x=0.0,
    ...     origin_y=0.0,
    ...     origin_z=0.0
    ... )
    """

    _TUPLE_FIELDS = frozenset({"leak_area_ratio", "grid"})

    def __init__(
        self,
        id: str = "Comp 1",
        width: float | None = 3.6,
        depth: float | None = 2.4,
        height: float | None = 2.4,
        ceiling_mat_id: str | list[str] | None = None,
        ceiling_thickness: float | list[float] | None = None,
        wall_mat_id: str | list[str] | None = None,
        wall_thickness: float | list[float] | None = None,
        floor_mat_id: str | list[str] | None = None,
        floor_thickness: float | list[float] | None = None,
        origin_x: float | None = 0,
        origin_y: float | None = 0,
        origin_z: float | None = 0,
        shaft: bool | None = None,
        hall: bool | None = None,
        leak_area_ratio: tuple[float, float] | None = None,  # (wall_leak, floor_leak)
        cross_sect_areas: list[float] | None = None,
        cross_sect_heights: list[float] | None = None,
        grid: tuple[int, int, int] = (50, 50, 50),
    ):
        self.id = id
        self.width = width
        self.depth = depth
        self.height = height
        self.ceiling_mat_id = ceiling_mat_id
        self.ceiling_thickness = ceiling_thickness
        self.wall_mat_id = wall_mat_id
        self.wall_thickness = wall_thickness
        self.floor_mat_id = floor_mat_id
        self.floor_thickness = floor_thickness
        self.origin_x = origin_x
        self.origin_y = origin_y
        self.origin_z = origin_z
        self.shaft = shaft
        self.hall = hall
        self.leak_area_ratio = leak_area_ratio
        self.cross_sect_areas = cross_sect_areas
        self.cross_sect_heights = cross_sect_heights
        self.grid = grid

        self._validate()
        self._initialized = True

    def _validate(self) -> None:
        """Validate the current state of the compartment attributes.

        Raises
        ------
        TypeError
            If leak_area_ratio, cross_sect_areas, cross_sect_heights or grid
            are not of the expected sequence type, or if a grid value is not
            an int.
        ValueError
            If any attribute violates the constraints.
        """
        if self.shaft is True and self.hall is True:
            raise ValueError(
                f"Compartment '{self.id}': shaft and hall cannot both be True."
            )

        if self.leak_area_ratio is not None and not isinstance(
            self.leak_area_ratio, tuple
        ):
            raise TypeError(
                f"Compartment '{self.id}': leak_area_ratio must be a sequence of "
                f"two values, got {type(self.leak_area_ratio).__name__}."
            )

        for param, list_val in (
            ("cross_sect_areas", self.cross_sect_areas),
            ("cross_sect_heights", self.cross_sect_heights),
        ):
            if list_val is not None and not isinstance(list_val, list):
                raise TypeError(
                    f"Compartment '{self.id}': {param} must be a list, got {type(list_val).__name__}."
                )

        for surface in ("ceiling", "wall", "floor"):
            mat_id = getattr(self, f"{surface}_mat_id")
            thickness = getattr(self, f"{surface}_thickness")
            n_mats = (
                len(mat_id)
                if isinstance(mat_id, list)
                else (1 if mat_id is not None else 0)
            )
            if n_mats > 3:
                raise ValueError(
                    f"Compartment '{self.id}': {surface}_mat_id accepts at most "
                    f"3 materials, got {n_mats}."
                )
            if mat_id is not None and thickness is not None:
                n_thick = len(thickness) if isinstance(thickness, list) else 1
                if n_mats != n_thick:
                    raise ValueError(
                        f"Compartment '{self.id}': {surface}_mat_id has {n_mats} "
                        f"material(s) but {surface}_thickness has {n_thick} value(s). "
                        "They must have the same length."
                    )

        if self.leak_area_ratio is not None and len(self.leak_area_ratio) != 2:
            raise ValueError(
                f"Compartment '{self.id}': leak_area_ratio must contain exactly 2 values "
                "(wall_leak, floor_leak)"
            )

        if (self.cross_sect_areas is None) != (self.cross_sect_heights is None):
            raise ValueError(
                f"Compartment '{self.id}': cross_sect_areas and cross_sect_heights "
                "must both be provided or both be None."
            )

        if self.cross_sect_areas is not None and self.cross_sect_heights is not None:
            if len(self.cross_sect_areas) != len(self.cross_sect_heights):
                raise ValueError(
                    f"Compartment '{self.id}': cross_sect_areas and cross_sect_heights "
                    "must have the same length"
                )

        for dim, val in (
            ("width", self.width),
            ("depth", self.depth),
            ("height", self.height),
        ):
            if val is not None and val <= 0:
                raise ValueError(
                    f"Compartment '{self.id}': {dim} must be positive, got {val}."
                )

        for coord, val in (
            ("origin_x", self.origin_x),
            ("origin_y", self.origin_y),
            ("origin_z", self.origin_z),
        ):
            if val is not None and val < 0:
                raise ValueError(
                    f"Compartment '{self.id}': {coord} must be >= 0, got {val}. "
                    "Negative positions are not allowed by CFAST."
                )

        if not isinstance(self.grid, tuple):
            raise TypeError(
                f"Compartment '{self.id}': grid must be a tuple, "
                f"got {type(self.grid).__name__}."
            )
        if len(self.grid) != 3:
            raise ValueError(
                f"Compartment '{self.id}': grid must be a 3-element sequence "
                f"(grid_x, grid_y, grid_z), got {self.grid!r}."
            )

        for g, val in (
            ("grid_x", self.grid[0]),
            ("grid_y", self.grid[1]),
            ("grid_z", self.grid[2]),
        ):
            if not isinstance(val, int):
                raise TypeError(
                    f"Compartment '{self.id}': {g} must be an int, "
                    f"got {type(val).__name__}."
                )
            if val <= 0:
                raise ValueError(
                    f"Compartment '{self.id}': {g} must be a positive integer, got {val}."
                )

    def __repr__(self) -> str:
        """Return a detailed string representation of the Compartment."""
        return (
            f"Compartment("
            f"id='{self.id}', "
            f"width={self.width}, depth={self.depth}, height={self.height}, "
            f"ceiling_mat_id={self.ceiling_mat_id!r}, wall_mat_id={self.wall_mat_id!r}, "
            f"floor_mat_id={self.floor_mat_id!r}, "
            f"origin=({self.origin_x}, {self.origin_y}, {self.origin_z})"
            ")"
        )

    def __str__(self) -> str:
        """Return a user-friendly string representation of the Compartment."""
        volume = None
        if (
            self.width is not None
            and self.depth is not None
            and self.height is not None
        ):
            volume = self.width * self.depth * self.height

        materials = []
        if self.ceiling_mat_id:
            val = self.ceiling_mat_id
            materials.append(
                f"ceiling: {', '.join(val) if isinstance(val, list) else val}"
            )
        if self.wall_mat_id:
            val = self.wall_mat_id
            materials.append(
                f"wall: {', '.join(val) if isinstance(val, list) else val}"
            )
        if self.floor_mat_id:
            val = self.floor_mat_id
            materials.append(
                f"floor: {', '.join(val) if isinstance(val, list) else val}"
            )

        material_str = f" ({', '.join(materials)})" if materials else ""

        volume_str = f", volume: {volume:.2f} m³" if volume else ""

        return (
            f"Compartment '{self.id}': "
            f"{self.width}x{self.depth}x{self.height} m{volume_str}{material_str}"
        )

    def to_input_string(self) -> str:
        """
        Generate CFAST input file string for this compartment.

        Returns
        -------
        str
            Formatted string ready for inclusion in CFAST input file.

        Examples
        --------
        >>> comp = Compartment(
        ...     id="ROOM1",
        ...     width=3.0,
        ...     depth=4.0,
        ...     height=2.4,
        ...     ceiling_mat_id="GYPSUM",
        ...     ceiling_thickness=0.016,
        ...     wall_mat_id="GYPSUM",
        ...     wall_thickness=0.016,
        ...     floor_mat_id="CONCRETE",
        ...     floor_thickness=0.10,
        ...     origin_x=0.0,
        ...     origin_y=0.0,
        ...     origin_z=0.0
        ... )
        >>> print(comp.to_input_string())
        &COMP ID = 'ROOM1' DEPTH = 4.0 HEIGHT = 2.4 WIDTH = 3.0 ...
        """
        rec = NamelistRecord("COMP")
        rec.add_field("ID", self.id)
        rec.add_field("DEPTH", self.depth)
        rec.add_field("HEIGHT", self.height)
        rec.add_field("WIDTH", self.width)

        if self.shaft is True:
            rec.add_field("SHAFT", True)
        elif self.hall is True:
            rec.add_field("HALL", True)

        if self.ceiling_mat_id is not None:
            rec.add_list_field("CEILING_MATL_ID", _as_list(self.ceiling_mat_id))
            if self.ceiling_thickness is not None:
                rec.add_list_field(
                    "CEILING_THICKNESS", _as_list(self.ceiling_thickness)
                )

        if self.wall_mat_id is not None:
            rec.add_list_field("WALL_MATL_ID", _as_list(self.wall_mat_id))
            if self.wall_thickness is not None:
                rec.add_list_field("WALL_THICKNESS", _as_list(self.wall_thickness))

        if self.floor_mat_id is not None:
            rec.add_list_field("FLOOR_MATL_ID", _as_list(self.floor_mat_id))
            if self.floor_thickness is not None:
                rec.add_list_field("FLOOR_THICKNESS", _as_list(self.floor_thickness))

        rec.add_list_field("CROSS_SECT_AREAS", self.cross_sect_areas)
        rec.add_list_field("CROSS_SECT_HEIGHTS", self.cross_sect_heights)

        origin_values = [self.origin_x, self.origin_y, self.origin_z]
        if any(val is not None for val in origin_values):
            sanitized = [v if v is not None else 0 for v in origin_values]
            rec.add_list_field("ORIGIN", sanitized)

        rec.add_list_field("GRID", self.grid)
        rec.add_list_field("LEAK_AREA_RATIO", self.leak_area_ratio)

        return rec.build()
