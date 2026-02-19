from __future__ import annotations

import pytest

from pycfast.surface_connections import SurfaceConnections

"""
Tests for the SurfaceConnections class.
"""


class TestSurfaceConnections:
    """Test class for SurfaceConnections."""

    def test_init_wall_connection(self):
        """Test initialization of a wall surface connection."""
        conn = SurfaceConnections(
            conn_type="WALL",
            comp_id="ROOM1",
            comp_ids="ROOM2",
            fraction=0.5,
        )
        assert conn.conn_type == "WALL"
        assert conn.comp_id == "ROOM1"
        assert conn.comp_ids == "ROOM2"
        assert conn.fraction == 0.5

    def test_init_floor_connection(self):
        """Test initialization of a floor surface connection."""
        conn = SurfaceConnections(
            conn_type="FLOOR",
            comp_id="UPPER",
            comp_ids="LOWER",
            fraction=0.0,
        )
        assert conn.conn_type == "FLOOR"
        assert conn.comp_id == "UPPER"
        assert conn.comp_ids == "LOWER"
        assert conn.fraction == 0.0

    def test_to_input_string_wall_connection(self):
        """Test input string generation for wall connection."""
        conn = SurfaceConnections(
            conn_type="WALL",
            comp_id="ROOM1",
            comp_ids="ROOM2",
            fraction=0.75,
        )
        result = conn.to_input_string()
        assert result.startswith("&CONN")
        assert result.endswith("/\n")
        assert "TYPE = 'WALL'" in result
        assert "COMP_ID = 'ROOM1'" in result
        assert "COMP_IDS = 'ROOM2'" in result
        assert "F = 0.75" in result
        assert "None" not in result

    def test_to_input_string_floor_connection(self):
        """Test input string generation for floor connection."""
        conn = SurfaceConnections(
            conn_type="FLOOR",
            comp_id="UPPER_ROOM",
            comp_ids="LOWER_ROOM",
            fraction=0.0,  # Fraction not used for floor connections
        )
        result = conn.to_input_string()
        assert result.startswith("&CONN")
        assert result.endswith("/\n")
        assert "TYPE = 'FLOOR'" in result
        assert "COMP_ID = 'UPPER_ROOM'" in result
        assert "COMP_IDS = 'LOWER_ROOM'" in result
        assert "F =" not in result

    def test_wall_connection_classmethod(self):
        """Test the wall_connection class method."""
        conn = SurfaceConnections.wall_connection(
            comp_id="LIVING",
            comp_ids="KITCHEN",
            fraction=0.8,
        )
        assert isinstance(conn, SurfaceConnections)
        assert conn.conn_type == "WALL"
        assert conn.comp_id == "LIVING"
        assert conn.comp_ids == "KITCHEN"
        assert conn.fraction == 0.8

    def test_ceiling_floor_connection_classmethod(self):
        """Test the ceiling_floor_connection class method."""
        conn = SurfaceConnections.ceiling_floor_connection(
            comp_id="SECOND_FLOOR",
            comp_ids="FIRST_FLOOR",
        )
        assert isinstance(conn, SurfaceConnections)
        assert conn.conn_type == "FLOOR"
        assert conn.comp_id == "SECOND_FLOOR"
        assert conn.comp_ids == "FIRST_FLOOR"

    @pytest.mark.parametrize(
        "fraction",
        [0.0, 1.0, 0.25],
    )
    def test_to_input_string_wall_with_different_fractions(self, fraction: float):
        """Test input string generation for wall connections with various fraction values."""
        conn = SurfaceConnections("WALL", "ROOM1", "ROOM2", fraction)
        result = conn.to_input_string()
        assert f"F = {fraction}" in result

    def test_to_input_string_compartment_id_formatting(self):
        """Test that compartment IDs are properly quoted in output."""
        conn = SurfaceConnections(
            conn_type="WALL",
            comp_id="COMP_A",
            comp_ids="COMP_B",
            fraction=0.5,
        )
        result = conn.to_input_string()
        assert "COMP_ID = 'COMP_A'" in result
        assert "COMP_IDS = 'COMP_B'" in result

    def test_to_input_string_floor_no_fraction(self):
        """Test that floor connections don't include fraction in output."""
        conn = SurfaceConnections(
            conn_type="FLOOR",
            comp_id="TOP",
            comp_ids="BOTTOM",
            fraction=0.5,  # Should be ignored for floor connections
        )
        result = conn.to_input_string()
        assert "F =" not in result
        assert "/\n" in result

    # Tests for dunder methods
    def test_repr(self) -> None:
        """Test __repr__ method."""
        conn = SurfaceConnections(
            conn_type="WALL", comp_id="ROOM1", comp_ids="ROOM2", fraction=0.75
        )

        repr_str = repr(conn)
        assert "SurfaceConnections(" in repr_str
        assert "conn_type='WALL'" in repr_str
        assert "comp_id='ROOM1'" in repr_str
        assert "comp_ids='ROOM2'" in repr_str
        assert "fraction=0.75" in repr_str

    def test_repr_floor_connection(self) -> None:
        """Test __repr__ method for floor connection."""
        conn = SurfaceConnections(
            conn_type="FLOOR", comp_id="UPPER", comp_ids="LOWER", fraction=None
        )

        repr_str = repr(conn)
        assert "SurfaceConnections(" in repr_str
        assert "conn_type='FLOOR'" in repr_str
        assert "fraction=None" in repr_str

    def test_str(self) -> None:
        """Test __str__ method."""
        conn = SurfaceConnections(
            conn_type="WALL", comp_id="LIVING_ROOM", comp_ids="KITCHEN", fraction=0.6
        )

        str_repr = str(conn)
        assert "Surface Connection (WALL):" in str_repr
        assert "LIVING_ROOM -> KITCHEN" in str_repr

    def test_str_floor_connection(self) -> None:
        """Test __str__ method for floor connection."""
        conn = SurfaceConnections(
            conn_type="FLOOR",
            comp_id="SECOND_FLOOR",
            comp_ids="FIRST_FLOOR",
            fraction=None,
        )

        str_repr = str(conn)
        assert "Surface Connection (FLOOR):" in str_repr
        assert "SECOND_FLOOR -> FIRST_FLOOR" in str_repr

    def test_getitem(self) -> None:
        """Test __getitem__ method."""
        conn = SurfaceConnections(
            conn_type="WALL", comp_id="ROOM_A", comp_ids="ROOM_B", fraction=0.8
        )

        assert conn["conn_type"] == "WALL"
        assert conn["comp_id"] == "ROOM_A"
        assert conn["comp_ids"] == "ROOM_B"
        assert conn["fraction"] == 0.8

    def test_getitem_invalid_key(self) -> None:
        """Test __getitem__ method with invalid key."""
        conn = SurfaceConnections("WALL", "A", "B", 0.5)

        with pytest.raises(
            KeyError, match="Property 'invalid_key' not found in SurfaceConnections"
        ):
            conn["invalid_key"]

    def test_setitem(self) -> None:
        """Test __setitem__ method."""
        conn = SurfaceConnections("WALL", "A", "B", 0.5)

        # Test setting various properties
        conn["conn_type"] = "FLOOR"
        assert conn.conn_type == "FLOOR"

        conn["comp_id"] = "NEW_ROOM"
        assert conn.comp_id == "NEW_ROOM"

        conn["comp_ids"] = "ANOTHER_ROOM"
        assert conn.comp_ids == "ANOTHER_ROOM"

        conn["fraction"] = 0.9
        assert conn.fraction == 0.9

    def test_setitem_none_fraction(self) -> None:
        """Test __setitem__ method with None fraction."""
        conn = SurfaceConnections("WALL", "A", "B", 0.5)

        conn["fraction"] = None
        assert conn.fraction is None

    def test_setitem_invalid_key(self) -> None:
        """Test __setitem__ method with invalid key."""
        conn = SurfaceConnections("WALL", "A", "B", 0.5)

        with pytest.raises(KeyError, match="Cannot set 'invalid_key'"):
            conn["invalid_key"] = "value"

    def test_repr_html(self) -> None:
        """Test _repr_html_ method."""
        conn = SurfaceConnections(
            conn_type="WALL", comp_id="ROOM1", comp_ids="ROOM2", fraction=0.75
        )

        html_str = conn._repr_html_()

        # Check that it returns valid HTML string
        assert isinstance(html_str, str)
        assert len(html_str) > 0

        # Check for expected HTML structure
        assert '<div class="pycfast-card' in html_str
        assert "Surface Connection" in html_str
        assert "Wall" in html_str  # Matches actual implementation format
        assert "ROOM1 → ROOM2" in html_str
        assert "0.75" in html_str

    def test_repr_html_floor_connection(self) -> None:
        """Test _repr_html_ method for floor connection."""
        conn = SurfaceConnections(
            conn_type="FLOOR", comp_id="UPPER", comp_ids="LOWER", fraction=None
        )

        html_str = conn._repr_html_()

        assert isinstance(html_str, str)
        assert "Floor" in html_str  # Matches actual implementation format
        assert "UPPER → LOWER" in html_str
