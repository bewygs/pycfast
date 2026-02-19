"""
Compartments definition module for CFAST simulations.

This module provides the Compartments class for defining the size, position,
materials of construction, and flow characteristics for the compartments in
the CFAST simulation.
"""

from __future__ import annotations

from typing import Any

from .utils.namelist import NamelistRecord
from .utils.theme import build_card


class Compartments:
    """
    Defines the size, position, materials of construction, and flow characteristics for compartments.

    The Compartments page defines the size, position, materials of construction, and flow
    characteristics for the compartments in the simulation. In order to model a fire scenario,
    the size and position of each compartment relevant to the scenario must be specified. For a
    compartment, the width, depth, compartment height and height of the floor of the compartment
    provide this specification. The maximum number of compartments for version 7 is 100. The usual
    assumption is that compartments are rectangular parallelepipeds. However, the CFAST model can
    accommodate odd shapes as equivalent floor area parallelepipeds or with a cross-sectional area
    that varies with height.

    Parameters
    ----------
    id : str
        Compartments are identified by a unique alphanumeric name. This may be as simple as
        a single character or number, or a description of the compartment.
    width : float, optional
        Specifies the width of the compartment as measured on the X axis from the origin
        (0,0,0) of the compartment. Default units: m, default value: 3.6 m.
    depth : float, optional
        Specifies the depth of the compartment as measured on the Y axis from the origin
        (0,0,0) of the compartment. Default units: m, default value: 2.4 m.
    height : float, optional
        Specifies the height of the compartment as measured on the Z axis from the origin
        (0,0,0) of the compartment. Default units: m, default value: 2.4 m.
    origin_x : float, optional
        Specifies the absolute x coordinate of the lower, left, front corner of the room.
        All absolute positions for all compartments must be greater than or equal to zero,
        i.e., negative numbers are not allowed for these inputs. Important in positioning
        the compartments for visualization in Smokeview. Default units: m, default value: 0.0 m.
    origin_y : float, optional
        Specifies the absolute y coordinate of the lower, left, front corner of the room.
        All absolute positions for all compartments must be greater than or equal to zero,
        i.e., negative numbers are not allowed for these inputs. Important in positioning
        the compartments for visualization in Smokeview. Default units: m, default value: 0.0 m.
    origin_z : float, optional
        Specifies the height of the floor of each compartment with respect to station elevation
        specified by the internal ambient conditions reference height parameter. The reference
        point must be the same for all elevations in the input data. All absolute positions
        for all compartments must be greater than or equal to zero, i.e., negative numbers are
        not allowed for these inputs. Default units: m, default value: 0.0 m.
    ceiling_mat_id : str, optional
        Material ID from the thermal properties from the Materials tab to define the ceiling
        surface of the compartment. Up to three materials can be used to define the layer(s)
        of the ceiling surface. The innermost layer is specified first. Default value: Off.
    ceiling_thickness : float, optional
        Thickness of each of the layers of the ceiling surface. Default units: m, default
        value: thickness of material specified on the Materials tab.
    wall_mat_id : str, optional
        Material ID from the thermal properties from the Materials tab to define the wall
        surface of the compartment. Up to three materials can be used to define the layer(s)
        of the wall surface. The innermost layer is specified first. Default value: Off.
    wall_thickness : float, optional
        Thickness of each of the layers of the wall surface. Default units: m, default
        value: thickness of material specified on the Materials tab.
    floor_mat_id : str, optional
        Material ID from the thermal properties from the Materials tab to define the floor
        surface of the compartment. Up to three materials can be used to define the layer(s)
        of the floor surface. The innermost layer is specified first. Default value: Off.
    floor_thickness : float, optional
        Thickness of each of the layers of the floor surface. Default units: m, default
        value: thickness of material specified on the Materials tab.
    shaft : bool, optional
        For tall compartments or those removed from the room of fire origin, the compartment
        may be modeled as a single, well-mixed zone rather than the default two-zone assumption.
        A single zone approximation is appropriate for smoke flow far from a fire source. Examples
        are elevators, shafts, complex stairwells, or compartments far from the fire.
    hall : bool, optional
        By specifying the compartment as a corridor, the ceiling jet temperature is calculated
        with a different empirical correlation that results in a somewhat higher temperature near
        the ceiling. This will impact, for example, detectors, sprinkler, and targets near the
        ceiling in corridors.
    leak_area_ratio : list[float], optional
        CFAST can automatically calculate leakage between one or more compartments and the outdoors.
        Leakage is specified as a leakage area per unit wall area and/or per unit floor area.
        Format: [Wall Leakage, Floor Leakage]. Default units: m²/m².
    cross_sect_areas : list[float], optional
        Cross-sectional area at the corresponding height for variable cross-sectional area
        compartments. Used for defining compartment properties for spaces which are not
        rectangular in area. Default units: m².
    cross_sect_heights : list[float], optional
        Height off the floor of the compartment for variable cross-sectional area definition.
        Cross-sectional area values should be input in order by ascending height. Default units: m.

    Notes
    -----
    If the thermophysical properties of the enclosing surfaces are not included, CFAST will
    treat them as adiabatic (no heat transfer). If a name is used which is not in the input
    file, the model should stop with an error message. The back surfaces of compartments are
    assumed to be exposed to ambient conditions unless specifically specified.

    All surfaces (ceiling, walls and floor) are turned off by default. The fully mixed
    (single zone) and corridor models are turned off by default.

    Examples
    --------
    Create a compartment following CFAST conventions:

    >>> room = Compartments(
    ...     id="BEDROOM",
    ...     width=3.5, depth=4.0, height=2.4,  # Size specification
    ...     ceiling_mat_id="GYPSUM", ceiling_thickness=0.016,
    ...     wall_mat_id="GYPSUM", wall_thickness=0.016,
    ...     floor_mat_id="CONCRETE", floor_thickness=0.10,
    ...     origin_x=0.0, origin_y=0.0, origin_z=0.0  # Position
    ... )
    """

    def __init__(
        self,
        id: str = "Comp 1",
        width: float | None = 3.6,
        depth: float | None = 2.4,
        height: float | None = 2.4,
        ceiling_mat_id: str | None = None,
        ceiling_thickness: float | None = None,
        wall_mat_id: str | None = None,
        wall_thickness: float | None = None,
        floor_mat_id: str | None = None,
        floor_thickness: float | None = None,
        origin_x: float | None = 0,
        origin_y: float | None = 0,
        origin_z: float | None = 0,
        shaft: bool | None = None,
        hall: bool | None = None,
        leak_area_ratio: list[float] | None = None,
        cross_sect_areas: list[float] | None = None,
        cross_sect_heights: list[float] | None = None,
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

        self._validate()

    def _validate(self) -> None:
        """Validate the current state of the compartment attributes.

        Raises
        ------
        ValueError
            If any attribute violates the constraints.
        """
        if self.shaft is True and self.hall is True:
            raise ValueError(
                f"Compartment '{self.id}': shaft and hall cannot both be True."
            )

        if self.cross_sect_areas is not None and self.cross_sect_heights is not None:
            if len(self.cross_sect_areas) != len(self.cross_sect_heights):
                raise ValueError(
                    f"Compartment '{self.id}': cross_sect_areas and cross_sect_heights "
                    "must have the same length"
                )

        if self.leak_area_ratio is not None and len(self.leak_area_ratio) != 2:
            raise ValueError(
                f"Compartment '{self.id}': leak_area_ratio must contain exactly 2 values "
                "[wall_leak, floor_leak]"
            )

    def __repr__(self) -> str:
        """Return a detailed string representation of the Compartments."""
        return (
            f"Compartments("
            f"id='{self.id}', "
            f"width={self.width}, depth={self.depth}, height={self.height}, "
            f"ceiling_mat_id='{self.ceiling_mat_id}', wall_mat_id='{self.wall_mat_id}', "
            f"floor_mat_id='{self.floor_mat_id}', "
            f"origin=({self.origin_x}, {self.origin_y}, {self.origin_z})"
            f")"
        )

    def __str__(self) -> str:
        """Return a user-friendly string representation of the Compartments."""
        volume = None
        if (
            self.width is not None
            and self.depth is not None
            and self.height is not None
        ):
            volume = self.width * self.depth * self.height

        materials = []
        if self.ceiling_mat_id:
            materials.append(f"ceiling: {self.ceiling_mat_id}")
        if self.wall_mat_id:
            materials.append(f"wall: {self.wall_mat_id}")
        if self.floor_mat_id:
            materials.append(f"floor: {self.floor_mat_id}")

        material_str = f" ({', '.join(materials)})" if materials else ""

        volume_str = f", volume: {volume:.2f} m³" if volume else ""

        return (
            f"Compartment '{self.id}': "
            f"{self.width}x{self.depth}x{self.height} m{volume_str}{material_str}"
        )

    def _repr_html_(self) -> str:
        """Return an HTML representation for Jupyter/interactive environments."""
        volume = None
        if (
            self.width is not None
            and self.depth is not None
            and self.height is not None
        ):
            volume = self.width * self.depth * self.height

        # Build materials info
        materials_info = []
        if self.ceiling_mat_id:
            thickness_str = (
                f" ({self.ceiling_thickness:.3f}m)"
                if hasattr(self, "ceiling_thickness") and self.ceiling_thickness
                else ""
            )
            materials_info.append(
                f"<div><strong>Ceiling:</strong> {self.ceiling_mat_id}{thickness_str}</div>"
            )
        if self.wall_mat_id:
            thickness_str = (
                f" ({self.wall_thickness:.3f}m)"
                if hasattr(self, "wall_thickness") and self.wall_thickness
                else ""
            )
            materials_info.append(
                f"<div><strong>Walls:</strong> {self.wall_mat_id}{thickness_str}</div>"
            )
        if self.floor_mat_id:
            thickness_str = (
                f" ({self.floor_thickness:.3f}m)"
                if hasattr(self, "floor_thickness") and self.floor_thickness
                else ""
            )
            materials_info.append(
                f"<div><strong>Floor:</strong> {self.floor_mat_id}{thickness_str}</div>"
            )

        materials_html = (
            "".join(materials_info)
            if materials_info
            else "<div><em>No materials specified</em></div>"
        )

        # Special properties
        special_props = []
        if getattr(self, "shaft", False):
            special_props.append("Shaft")
        if getattr(self, "hall", False):
            special_props.append("Hall")
        special_str = (
            f"<div><strong>Type:</strong> {', '.join(special_props)}</div>"
            if special_props
            else ""
        )

        body_html = f"""
            <div class="pycfast-card-grid" style="margin-bottom: 10px;">
                <div><strong>Width:</strong> {self.width} m</div>
                <div><strong>Depth:</strong> {self.depth} m</div>
                <div><strong>Height:</strong> {self.height} m</div>
                {f"<div><strong>Volume:</strong> {volume:.1f} m³</div>" if volume else ""}
            </div>
            <div style="margin-bottom: 10px; font-size: 0.85em;">
                <strong>Origin:</strong> ({self.origin_x}, {self.origin_y}, {self.origin_z}) m
            </div>
            {special_str}
            <details class="pycfast-inline-detail">
                <summary>Materials & Construction</summary>
                <div class="pycfast-detail-content">{materials_html}</div>
            </details>
        """

        subtitle = (
            f"<strong>{self.width}×{self.depth}×{self.height} m</strong>"
            f"{f' • {volume:.1f} m³' if volume else ''}"
        )

        return build_card(
            icon="🏠",
            gradient="linear-gradient(135deg, #5f27cd, #741b47)",
            title=f"Compartment: {self.id}",
            subtitle=subtitle,
            accent_color="#5f27cd",
            body_html=body_html,
        )

    def __getitem__(self, key: str) -> Any:
        """Get compartment property by name for dictionary-like access."""
        if not hasattr(self, key):
            raise KeyError(f"Property '{key}' not found in Compartment.")
        return getattr(self, key)

    def __setitem__(self, key: str, value: Any) -> None:
        """Set compartment property by name for dictionary-like assignment.

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
                f"Cannot set '{key}'. Property does not exist in Compartment."
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
        Generate CFAST input file string for this compartment.

        Returns
        -------
        str
            Formatted string ready for inclusion in CFAST input file.

        Examples
        --------
        >>> comp = Compartments("ROOM1", width=3.0, depth=4.0, height=2.4,
        ...                    ceiling_mat_id="GYPSUM", ceiling_thickness=0.016,
        ...                    wall_mat_id="GYPSUM", wall_thickness=0.016,
        ...                    floor_mat_id="CONCRETE", floor_thickness=0.10,
        ...                    origin_x=0.0, origin_y=0.0, origin_z=0.0)
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
            rec.add_field("CEILING_MATL_ID", self.ceiling_mat_id)
            rec.add_field("CEILING_THICKNESS", self.ceiling_thickness)

        if self.wall_mat_id is not None:
            rec.add_field("WALL_MATL_ID", self.wall_mat_id)
            rec.add_field("WALL_THICKNESS", self.wall_thickness)

        if self.floor_mat_id is not None:
            rec.add_field("FLOOR_MATL_ID", self.floor_mat_id)
            rec.add_field("FLOOR_THICKNESS", self.floor_thickness)

        rec.add_list_field("CROSS_SECT_AREAS", self.cross_sect_areas)
        rec.add_list_field("CROSS_SECT_HEIGHTS", self.cross_sect_heights)

        origin_values = [self.origin_x, self.origin_y, self.origin_z]
        if any(val is not None for val in origin_values):
            sanitized = [v if v is not None else 0 for v in origin_values]
            rec.add_list_field("ORIGIN", sanitized)

        rec.add_list_field("GRID", [50, 50, 50])
        rec.add_list_field("LEAK_AREA_RATIO", self.leak_area_ratio)

        return rec.build()
