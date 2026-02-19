"""
Surface connections module for CFAST simulations.

This module provides the SurfaceConnections class for defining heat transfer
between compartments through solid boundaries (walls, ceilings, and floors)
by means of conduction.
"""

from __future__ import annotations

import warnings
from typing import Any

from .utils.namelist import NamelistRecord
from .utils.theme import build_card


class SurfaceConnections:
    """
    Represents surface connections for heat transfer between compartments in CFAST.

    The Surface Connections functionality allows the user to define heat transfer
    between compartments in a simulation. Energy can be transferred from compartment
    to compartment through solid boundaries (walls, ceilings and floors) by means
    of conduction. The heat transfer between connected compartments is modeled by
    setting the boundary condition for the outside surface of a compartment to the
    temperature of the outside surface of the connected compartment. Temperatures
    are determined by the solver so that the heat flux striking the wall surface
    (both interior and exterior) is consistent with the temperature gradient at
    that surface.

    There are two types of surface connections:

    - **Horizontal Heat Transfer (Wall Connections)**: Heat transfer through
      vertical surfaces (walls) between adjacent compartments. The fraction
      parameter specifies what portion of the vertical surface area connects
      the two compartments.

    - **Vertical Heat Transfer (Floor/Ceiling Connections)**: Heat transfer
      through horizontal surfaces between compartments stacked vertically.
      The connection is through the floor of the top compartment and the
      ceiling of the bottom compartment.

    Important considerations:

    - For horizontal heat transfer, you must include a connection for each
      compartment (bidirectional: compartment 1→2 AND compartment 2→1)
    - For consistency, the fraction for each compartment needs to specify
      equal areas in the two compartments
    - Fractions for connections should add to unity
    - An error is generated if fractions for a compartment add to >1
    - If fractions add to <1, remaining surface area connects to outdoors

    Parameters
    ----------
    conn_type : str
        Type of surface connection. Options: "WALL" for horizontal heat transfer
        through vertical surfaces, "FLOOR" for vertical heat transfer through
        horizontal surfaces.
    comp_id : str
        First compartment ID. For wall connections, this is the first of the
        compartments whose walls are connected for horizontal heat transfer.
        For floor connections, this is the top compartment (connection through
        its floor).
    comp_ids : str
        Second compartment ID. For wall connections, this is the second of the
        compartments whose walls are connected for horizontal heat transfer.
        For floor connections, this is the bottom compartment (connection through
        its ceiling).
    fraction : float | None
        Fraction of vertical surface areas connected (0-1). Only used for wall
        connections. Specifies the fraction of the vertical surface area of the
        first compartment that connects the first and second compartment pair.
        Must be None for floor/ceiling connections.

    Raises
    ------
    ValueError
        If conn_type is not "WALL" or "FLOOR", if fraction is specified for
        floor connections, or if fraction is outside valid range for wall
        connections.

    Notes
    -----
    For wall connections between compartments of different sizes, the fraction
    values must be calculated to ensure equal contact areas:
    - Connection 1→2: fraction = contact_area / total_wall_area_comp1
    - Connection 2→1: fraction = contact_area / total_wall_area_comp2

    For floor/ceiling connections, the entire horizontal interface is assumed
    to participate in heat transfer, so no fraction is needed.

    Examples
    --------
    Create a wall connection between two rooms:

    >>> # For 1mx1mx1m compartments sharing 1m² wall out of 4m² total wall area
    >>> wall_conn_1to2 = SurfaceConnections.wall_connection(
    ...     comp_id="ROOM1",
    ...     comp_ids="ROOM2",
    ...     fraction=0.25  # 1m²/4m² = 0.25
    ... )
    >>> wall_conn_2to1 = SurfaceConnections.wall_connection(
    ...     comp_id="ROOM2",
    ...     comp_ids="ROOM1",
    ...     fraction=0.25  # Bidirectional connection required
    ... )

    Create a floor/ceiling connection between stacked compartments:

    >>> floor_conn = SurfaceConnections.ceiling_floor_connection(
    ...     comp_id="UPPER_ROOM",    # Top compartment
    ...     comp_ids="LOWER_ROOM"    # Bottom compartment
    ... )

    Different sized compartments example:

    >>> # Compartment 1: 1x1x1m, Compartment 2: 2x2x2m
    >>> # Connection 1→2: 1m²/4m² = 0.25
    >>> # Connection 2→1: 1m²/16m² = 0.125 (same 1m² area, different base)
    >>> conn_1to2 = SurfaceConnections.wall_connection("COMP1", "COMP2", 0.25)
    >>> conn_2to1 = SurfaceConnections.wall_connection("COMP2", "COMP1", 0.125)
    """

    def __init__(
        self,
        conn_type: str,
        comp_id: str,
        comp_ids: str,
        fraction: float | None = None,
    ):
        self.conn_type = conn_type
        self.comp_id = comp_id
        self.comp_ids = comp_ids
        self.fraction = fraction

    def __repr__(self) -> str:
        """Return a detailed string representation of the SurfaceConnections."""
        return (
            f"SurfaceConnections("
            f"conn_type='{self.conn_type}', "
            f"comp_id='{self.comp_id}', "
            f"comp_ids='{self.comp_ids}', "
            f"fraction={self.fraction}"
            f")"
        )

    def __str__(self) -> str:
        """Return a user-friendly string representation of the SurfaceConnections."""
        connection = f"{self.comp_id} -> {self.comp_ids}"
        return f"Surface Connection ({self.conn_type}): {connection}"

    def _repr_html_(self) -> str:
        """Return an HTML representation for Jupyter/interactive environments."""
        conn_type_str = getattr(self, "conn_type", "Unknown").title()

        # Icon and color based on connection type
        if self.conn_type == "WALL":
            icon = "🧱"
            color = "#e17055"
        elif self.conn_type == "FLOOR":
            icon = "🏗️"
            color = "#636e72"
        elif self.conn_type == "CEILING":
            icon = "🏠"
            color = "#74b9ff"
        else:
            icon = "🔗"
            color = "#6c5ce7"

        fraction_info = ""
        if hasattr(self, "fraction") and self.fraction is not None:
            fraction_info = f"<div><strong>Fraction:</strong> {self.fraction}</div>"

        body_html = f"""
            <div class="pycfast-card-grid">
                <div><strong>Type:</strong> {conn_type_str}</div>
                <div><strong>From:</strong> {self.comp_id}</div>
                <div><strong>To:</strong> {self.comp_ids}</div>
                {fraction_info}
            </div>
        """

        return build_card(
            icon=icon,
            gradient=f"linear-gradient(135deg, {color}, {color}aa)",
            title="Surface Connection",
            subtitle=f"<strong>{conn_type_str}</strong>: {self.comp_id} → {self.comp_ids}",
            accent_color=color,
            body_html=body_html,
        )

    def __getitem__(self, key: str) -> Any:
        """Get property by name for dictionary-like access."""
        if not hasattr(self, key):
            raise KeyError(f"Property '{key}' not found in SurfaceConnections.")
        return getattr(self, key)

    def __setitem__(self, key: str, value: Any) -> None:
        """Set property by name for dictionary-like assignment."""
        if not hasattr(self, key):
            raise KeyError(
                f"Cannot set '{key}'. Property does not exist in SurfaceConnections."
            )
        setattr(self, key, value)

    def to_input_string(self) -> str:
        """
        Convert the surface connection to a formatted string for CFAST input file.

        Returns
        -------
        str
            Formatted string ready for inclusion in CFAST input file.

        Examples
        --------
        >>> wall_conn = SurfaceConnections.wall_connection("ROOM1", "ROOM2", 0.25)
        >>> print(wall_conn.to_input_string())
        &CONN TYPE = 'WALL' COMP_ID = 'ROOM1' COMP_IDS = 'ROOM2' F = 0.25 /

        >>> floor_conn = SurfaceConnections.ceiling_floor_connection("UPPER", "LOWER")
        >>> print(floor_conn.to_input_string())
        &CONN TYPE = 'FLOOR' COMP_ID = 'UPPER' COMP_IDS = 'LOWER' /
        """
        rec = NamelistRecord("CONN")
        rec.add_field("TYPE", self.conn_type)
        rec.add_field("COMP_ID", self.comp_id)
        rec.add_field("COMP_IDS", self.comp_ids)

        if self.conn_type == "WALL":
            rec.add_field("F", self.fraction)
        elif self.conn_type == "FLOOR" and self.fraction is not None:
            warnings.warn(
                "Fraction should be None for FLOOR connections.",
                UserWarning,
                stacklevel=2,
            )

        return rec.build()

    @classmethod
    def wall_connection(
        cls, comp_id: str, comp_ids: str, fraction: float
    ) -> SurfaceConnections:
        """
        Create a surface connection for horizontal heat transfer through walls.

        Parameters
        ----------
        comp_id : str
            First compartment identifier (source compartment for this connection).
        comp_ids : str
            Second compartment identifier (target compartment for this connection).
        fraction : float
            Fraction of the vertical surface area of the first compartment that
            connects to the second compartment. Valid range: 0.0 to 1.0.
            This represents the contact area divided by the total wall area
            of the source compartment.

        Returns
        -------
        SurfaceConnections
            Configured surface connection instance for wall heat transfer.
        """
        return cls(
            conn_type="WALL", comp_id=comp_id, comp_ids=comp_ids, fraction=fraction
        )

    @classmethod
    def ceiling_floor_connection(
        cls, comp_id: str, comp_ids: str
    ) -> SurfaceConnections:
        """
        Create a surface connection for vertical heat transfer through floors/ceilings.

        This class method creates a floor/ceiling connection between two
        compartments for vertical heat transfer through horizontal surfaces.
        The connection is established between the floor of the top compartment
        and the ceiling of the bottom compartment. Unlike wall connections,
        only one connection definition is needed (not bidirectional).

        Parameters
        ----------
        comp_id : str
            Top compartment identifier. Heat transfer occurs through the floor
            of this compartment.
        comp_ids : str
            Bottom compartment identifier. Heat transfer occurs through the
            ceiling of this compartment.

        Returns
        -------
        SurfaceConnections
            Configured surface connection instance for floor/ceiling heat transfer.
        """
        return cls(conn_type="FLOOR", comp_id=comp_id, comp_ids=comp_ids, fraction=None)
