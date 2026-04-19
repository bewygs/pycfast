from __future__ import annotations

import pytest

from pycfast.compartment import Compartment

"""
Tests for the Compartment class.
"""


class TestCompartment:
    """Test class for Compartment."""

    def test_init_default(self):
        """Test default initialization."""
        comp = Compartment()
        assert comp.id == "Comp 1"
        assert comp.width == 3.6
        assert comp.depth == 2.4
        assert comp.height == 2.4
        assert comp.origin_x == 0
        assert comp.origin_y == 0
        assert comp.origin_z == 0
        assert comp.ceiling_mat_id is None
        assert comp.wall_mat_id is None
        assert comp.floor_mat_id is None
        assert comp.shaft is None
        assert comp.hall is None
        assert comp.leak_area_ratio is None
        assert comp.cross_sect_areas is None
        assert comp.cross_sect_heights is None

    def test_init_with_all_parameters(self):
        """Test initialization with all parameters."""
        comp = Compartment(
            id="BEDROOM",
            width=3.5,
            depth=4.0,
            height=2.4,
            ceiling_mat_id="GYPSUM",
            ceiling_thickness=0.016,
            wall_mat_id="GYPSUM",
            wall_thickness=0.016,
            floor_mat_id="CONCRETE",
            floor_thickness=0.10,
            origin_x=0.0,
            origin_y=0.0,
            origin_z=0.0,
            shaft=False,
            hall=True,
            leak_area_ratio=[0.0001, 0.0002],
            cross_sect_areas=[10.0, 15.0],
            cross_sect_heights=[1.0, 2.0],
        )
        assert comp.id == "BEDROOM"
        assert comp.width == 3.5
        assert comp.depth == 4.0
        assert comp.height == 2.4
        assert comp.ceiling_mat_id == "GYPSUM"
        assert comp.ceiling_thickness == 0.016
        assert comp.wall_mat_id == "GYPSUM"
        assert comp.wall_thickness == 0.016
        assert comp.floor_mat_id == "CONCRETE"
        assert comp.floor_thickness == 0.10
        assert comp.origin_x == 0.0
        assert comp.origin_y == 0.0
        assert comp.origin_z == 0.0
        assert comp.shaft is False
        assert comp.hall is True
        assert comp.leak_area_ratio == [0.0001, 0.0002]
        assert comp.cross_sect_areas == [10.0, 15.0]
        assert comp.cross_sect_heights == [1.0, 2.0]

    def test_init_shaft_and_hall_both_true(self):
        """Test that initialization fails when both shaft and hall are True."""
        with pytest.raises(ValueError, match="shaft and hall cannot both be True"):
            Compartment(id="ROOM1", shaft=True, hall=True)

    def test_init_mismatched_cross_sect_arrays(self):
        """Test that initialization fails with mismatched cross-section arrays."""
        with pytest.raises(ValueError, match="must have the same length"):
            Compartment(
                id="ROOM1",
                cross_sect_areas=[10.0, 15.0],
                cross_sect_heights=[1.0],
            )

    @pytest.mark.parametrize(
        "leak_area_ratio",
        [
            pytest.param([0.1], id="too-few"),
            pytest.param([0.1, 0.2, 0.3], id="too-many"),
        ],
    )
    def test_init_invalid_leak_area_ratio_length(self, leak_area_ratio: list[float]):
        """Test that initialization fails with wrong leak area ratio length."""
        with pytest.raises(ValueError, match="must contain exactly 2 values"):
            Compartment(id="ROOM1", leak_area_ratio=leak_area_ratio)

    @pytest.mark.parametrize("param", ["width", "depth", "height"])
    def test_negative_dimension(self, param: str):
        """Test that initialization fails with negative dimensions."""
        with pytest.raises(ValueError, match="must be positive"):
            Compartment(id="ROOM1", **{param: -1.0})  # type: ignore[arg-type]

    @pytest.mark.parametrize("param", ["origin_x", "origin_y", "origin_z"])
    def test_negative_location(self, param: str):
        """Test that initialization fails with negative origin coordinates."""
        with pytest.raises(ValueError, match=r"must be >= 0"):
            Compartment(id="ROOM1", width=3.0, depth=4.0, height=2.4, **{param: -1.0})  # type: ignore[arg-type]

    def test_to_input_string_basic(self):
        """Test basic input string generation."""
        comp = Compartment(id="ROOM1", width=3.0, depth=4.0, height=2.4)
        result = comp.to_input_string()
        assert result.startswith("&COMP")
        assert result.endswith("/\n")
        assert "ID = 'ROOM1'" in result
        assert "DEPTH = 4.0" in result
        assert "HEIGHT = 2.4" in result
        assert "WIDTH = 3.0" in result
        assert "ORIGIN = 0, 0, 0" in result
        assert "None" not in result

    def test_to_input_string_with_materials(self):
        """Test input string generation with materials."""
        comp = Compartment(
            id="ROOM1",
            width=3.0,
            depth=4.0,
            height=2.4,
            ceiling_mat_id="GYPSUM",
            ceiling_thickness=0.016,
            wall_mat_id="GYPSUM",
            wall_thickness=0.016,
            floor_mat_id="CONCRETE",
            floor_thickness=0.10,
        )
        result = comp.to_input_string()
        assert "CEILING_MATL_ID = 'GYPSUM'" in result
        assert "CEILING_THICKNESS = 0.016" in result
        assert "WALL_MATL_ID = 'GYPSUM'" in result
        assert "WALL_THICKNESS = 0.016" in result
        assert "FLOOR_MATL_ID = 'CONCRETE'" in result
        assert "FLOOR_THICKNESS = 0.1" in result

    @pytest.mark.parametrize(
        ("prop", "kwargs", "expected", "unexpected"),
        [
            pytest.param(
                "shaft",
                {
                    "id": "SHAFT1",
                    "width": 2.0,
                    "depth": 2.0,
                    "height": 10.0,
                    "shaft": True,
                },
                "SHAFT = .TRUE.",
                "HALL",
                id="shaft",
            ),
            pytest.param(
                "hall",
                {
                    "id": "HALL1",
                    "width": 10.0,
                    "depth": 2.0,
                    "height": 2.4,
                    "hall": True,
                },
                "HALL = .TRUE.",
                "SHAFT",
                id="hall",
            ),
        ],
    )
    def test_to_input_string_with_shaft_or_hall(
        self, prop: str, kwargs: dict, expected: str, unexpected: str
    ):
        """Test input string generation with shaft or hall option."""
        comp = Compartment(**kwargs)  # type: ignore[arg-type]
        result = comp.to_input_string()
        assert expected in result
        assert unexpected not in result

    def test_to_input_string_with_cross_sections(self):
        """Test input string generation with variable cross-sections."""
        comp = Compartment(
            id="ROOM1",
            width=3.0,
            depth=4.0,
            height=2.4,
            cross_sect_areas=[10.0, 15.0, 12.0],
            cross_sect_heights=[0.5, 1.0, 2.0],
        )
        result = comp.to_input_string()
        assert "CROSS_SECT_AREAS = 10.0, 15.0, 12.0" in result
        assert "CROSS_SECT_HEIGHTS = 0.5, 1.0, 2.0" in result

    def test_to_input_string_with_leak_area_ratio(self):
        """Test input string generation with leak area ratios."""
        comp = Compartment(
            id="ROOM1",
            width=3.0,
            depth=4.0,
            height=2.4,
            leak_area_ratio=[0.0001, 0.0002],
        )
        result = comp.to_input_string()
        assert "LEAK_AREA_RATIO = 0.0001, 0.0002" in result

    def test_to_input_string_custom_origin(self):
        """Test input string generation with custom origin."""
        comp = Compartment(
            id="ROOM2",
            width=3.0,
            depth=4.0,
            height=2.4,
            origin_x=5.0,
            origin_y=10.0,
            origin_z=3.0,
        )
        result = comp.to_input_string()
        assert "ORIGIN = 5.0, 10.0, 3.0" in result

    def test_to_input_string_partial_origin(self):
        """Test input string generation with partial origin specification."""
        comp = Compartment(
            id="ROOM2",
            width=3.0,
            depth=4.0,
            height=2.4,
            origin_x=5.0,
            origin_y=None,
            origin_z=3.0,
        )
        result = comp.to_input_string()
        assert "ORIGIN = 5.0, 0, 3.0" in result

    def test_to_input_string_materials_without_thickness(self):
        """Test input string generation with materials but without thickness."""
        comp = Compartment(
            id="ROOM1",
            width=3.0,
            depth=4.0,
            height=2.4,
            ceiling_mat_id="GYPSUM",
            wall_mat_id="GYPSUM",
            floor_mat_id="CONCRETE",
        )
        result = comp.to_input_string()
        assert "CEILING_MATL_ID = 'GYPSUM'" in result
        assert "CEILING_THICKNESS" not in result
        assert "WALL_MATL_ID = 'GYPSUM'" in result
        assert "WALL_THICKNESS" not in result
        assert "FLOOR_MATL_ID = 'CONCRETE'" in result
        assert "FLOOR_THICKNESS" not in result

    def test_to_input_string_none_dimensions(self):
        """Test input string generation with None dimensions."""
        comp = Compartment(id="ROOM1", width=None, depth=None, height=None)
        result = comp.to_input_string()
        assert "WIDTH" not in result
        assert "DEPTH" not in result
        assert "HEIGHT" not in result

    @pytest.mark.parametrize(
        "kwargs",
        [
            pytest.param({"cross_sect_areas": [10.0, 15.0]}, id="areas-only"),
            pytest.param({"cross_sect_heights": [1.0, 2.0]}, id="heights-only"),
        ],
    )
    def test_init_cross_sect_one_sided(self, kwargs):
        """Test that providing only one of cross_sect_areas/heights raises ValueError."""
        with pytest.raises(
            ValueError,
            match="cross_sect_areas and cross_sect_heights must both be provided or both be None",
        ):
            Compartment(id="ROOM1", **kwargs)

    @pytest.mark.parametrize(
        ("param", "value"),
        [
            pytest.param("leak_area_ratio", (0.1, 0.2), id="leak_area_ratio-tuple"),
            pytest.param("cross_sect_areas", (10.0, 15.0), id="cross_sect_areas-tuple"),
            pytest.param(
                "cross_sect_heights", (1.0, 2.0), id="cross_sect_heights-tuple"
            ),
        ],
    )
    def test_init_type_error_list_params(self, param: str, value):
        """Test that non-list values for list parameters raise TypeError."""
        kwargs: dict = {"id": "ROOM1"}
        if param == "cross_sect_areas":
            kwargs["cross_sect_heights"] = [1.0, 2.0]
        if param == "cross_sect_heights":
            kwargs["cross_sect_areas"] = [10.0, 15.0]
        with pytest.raises(TypeError, match=f"{param} must be a list"):
            Compartment(**kwargs, **{param: value})

    # Tests for dunder methods
    def test_repr(self) -> None:
        """Test __repr__ method."""
        comp = Compartment(
            id="BEDROOM",
            width=3.5,
            depth=4.0,
            height=2.4,
            ceiling_mat_id="GYPSUM",
            wall_mat_id="CONCRETE",
        )

        repr_str = repr(comp)
        assert "Compartment(" in repr_str
        assert "id='BEDROOM'" in repr_str
        assert "width=3.5" in repr_str
        assert "depth=4.0" in repr_str
        assert "height=2.4" in repr_str

    def test_str(self) -> None:
        """Test __str__ method."""
        comp = Compartment(
            id="LIVING_ROOM",
            width=5.0,
            depth=4.0,
            height=2.8,
            ceiling_mat_id="GYPSUM",
            wall_mat_id="BRICK",
        )

        str_repr = str(comp)
        assert "Compartment 'LIVING_ROOM'" in str_repr
        assert "5.0x4.0x2.8 m" in str_repr
        assert "volume: 56.00 m³" in str_repr
        assert "ceiling: GYPSUM" in str_repr
        assert "wall: BRICK" in str_repr

    def test_str_with_shaft_and_hall(self) -> None:
        """Test __str__ method with shaft property only."""
        comp = Compartment(
            id="CORRIDOR",
            width=2.0,
            depth=10.0,
            height=2.4,
            shaft=True,
            hall=False,  # Only shaft, not both
        )

        str_repr = str(comp)
        assert "Compartment 'CORRIDOR'" in str_repr
        assert "2.0x10.0x2.4 m" in str_repr

    def test_getitem(self) -> None:
        """Test __getitem__ method."""
        comp = Compartment(
            id="TEST_ROOM",
            width=4.0,
            depth=3.0,
            height=2.5,
            ceiling_mat_id="GYPSUM",
            wall_mat_id="CONCRETE",
            floor_mat_id="WOOD",
            origin_x=1.0,
            origin_y=2.0,
            shaft=False,
            hall=True,
        )

        assert comp["id"] == "TEST_ROOM"
        assert comp["width"] == 4.0
        assert comp["depth"] == 3.0
        assert comp["height"] == 2.5
        assert comp["ceiling_mat_id"] == "GYPSUM"
        assert comp["wall_mat_id"] == "CONCRETE"
        assert comp["floor_mat_id"] == "WOOD"
        assert comp["origin_x"] == 1.0
        assert comp["origin_y"] == 2.0
        assert comp["shaft"] is False
        assert comp["hall"] is True

    def test_getitem_invalid_key(self) -> None:
        """Test __getitem__ method with invalid key."""
        comp = Compartment(id="ROOM1")

        with pytest.raises(
            KeyError, match="Property 'invalid_key' not found in Compartment"
        ):
            comp["invalid_key"]

    def test_setitem(self) -> None:
        """Test __setitem__ method."""
        comp = Compartment(id="ROOM1")

        # Test setting various properties
        comp["id"] = "NEW_ROOM"
        assert comp.id == "NEW_ROOM"

        comp["width"] = 5.0
        assert comp.width == 5.0

        comp["depth"] = 6.0
        assert comp.depth == 6.0

        comp["height"] = 3.0
        assert comp.height == 3.0

        comp["ceiling_mat_id"] = "STEEL"
        assert comp.ceiling_mat_id == "STEEL"

        comp["wall_mat_id"] = "CONCRETE"
        assert comp.wall_mat_id == "CONCRETE"

        comp["floor_mat_id"] = "WOOD"
        assert comp.floor_mat_id == "WOOD"

        comp["origin_x"] = 2.5
        assert comp.origin_x == 2.5

        comp["shaft"] = True
        assert comp.shaft is True

        comp["hall"] = False
        assert comp.hall is False

    def test_setitem_list_properties(self) -> None:
        """Test __setitem__ method with list properties."""
        comp = Compartment(id="ROOM1")

        comp["leak_area_ratio"] = [0.001, 0.002]
        assert comp.leak_area_ratio == [0.001, 0.002]

    def test_setitem_cross_sect_requires_both_set(self) -> None:
        """Test that cross_sect_areas/heights cannot be set individually via __setitem__.

        Both fields must be provided together at construction time. Setting one while
        the other is None violates the constraint set by _validate().
        """
        comp = Compartment(id="ROOM1")
        with pytest.raises(ValueError, match="must both be provided or both be None"):
            comp["cross_sect_areas"] = [10.0, 15.0, 20.0]

    def test_setitem_cross_sect_update_when_both_set(self) -> None:
        """Test updating cross_sect_areas when both lists are pre-set and lengths match."""
        comp = Compartment(
            id="ROOM1",
            cross_sect_areas=[10.0, 15.0],
            cross_sect_heights=[1.0, 2.0],
        )
        comp["cross_sect_areas"] = [12.0, 18.0]
        assert comp.cross_sect_areas == [12.0, 18.0]

    def test_setitem_invalid_key(self) -> None:
        """Test __setitem__ method with invalid key."""
        comp = Compartment(id="ROOM1")

        with pytest.raises(KeyError, match="Cannot set 'invalid_key'"):
            comp["invalid_key"] = "value"


class TestCompartmentSetItemValidation:
    """Test validation in __setitem__ to ensure data integrity."""

    def test_setitem_shaft_and_hall_both_true(self):
        """Test that __setitem__ rejects shaft and hall both True."""
        comp = Compartment(id="ROOM1", shaft=True)
        with pytest.raises(ValueError, match="shaft and hall cannot both be True"):
            comp["hall"] = True

    @pytest.mark.parametrize(
        "invalid_ratio",
        [
            pytest.param([0.01], id="too-few"),
            pytest.param([0.01, 0.02, 0.03], id="too-many"),
        ],
    )
    def test_setitem_invalid_leak_area_ratio_length(self, invalid_ratio):
        """Test that __setitem__ rejects leak_area_ratio with wrong length."""
        comp = Compartment(id="ROOM1")
        with pytest.raises(
            ValueError, match="leak_area_ratio must contain exactly 2 values"
        ):
            comp["leak_area_ratio"] = invalid_ratio

    def test_setitem_mismatched_cross_sect_lengths(self):
        """Test that __setitem__ rejects mismatched cross section list lengths."""
        comp = Compartment(
            id="ROOM1",
            cross_sect_areas=[1.0, 2.0],
            cross_sect_heights=[0.0, 1.0],
        )
        with pytest.raises(
            ValueError,
            match="cross_sect_areas and cross_sect_heights must have the same length",
        ):
            comp["cross_sect_areas"] = [1.0, 2.0, 3.0]

    def test_setitem_valid_dimension_changes(self):
        """Test that __setitem__ accepts valid dimension changes."""
        comp = Compartment(id="ROOM1")
        comp["width"] = 5.0
        comp["height"] = 3.0
        assert comp.width == 5.0
        assert comp.height == 3.0

    def test_setitem_invalid_does_not_mutate_state(self):
        """Test that a failed __setitem__ rolls back to the previous value."""
        comp = Compartment(id="ROOM1", shaft=True)
        assert comp.shaft is True
        assert comp.hall is None

        with pytest.raises(ValueError):
            comp["hall"] = True

        assert comp.hall is None
