from __future__ import annotations

import pytest

from pycfast.ceiling_floor_vents import CeilingFloorVents

"""
Tests for the CeilingFloorVents class.
"""


@pytest.fixture()
def make_ceiling_floor_vent():
    """Create a CeilingFloorVents instance with sensible defaults."""

    def _make(**kwargs: object) -> CeilingFloorVents:
        defaults: dict[str, object] = {
            "id": "VENT1",
            "comps_ids": ["UPPER", "LOWER"],
            "area": 1.0,
        }
        defaults.update(kwargs)
        return CeilingFloorVents(**defaults)  # type: ignore[arg-type]

    return _make


class TestCeilingFloorVents:
    """Test class for CeilingFloorVents."""

    def test_init_basic(self):
        """Test basic initialization with required parameters."""
        vent = CeilingFloorVents(id="VENT1", comps_ids=["UPPER", "LOWER"], area=1.0)
        assert vent.id == "VENT1"
        assert vent.comps_ids == ["UPPER", "LOWER"]
        assert vent.area == 1.0
        assert vent.shape == "ROUND"
        assert vent.width is None
        assert vent.offsets == [0, 0]

    def test_init_with_all_parameters(self):
        """Test initialization with all parameters."""
        vent = CeilingFloorVents(
            id="VENT1",
            comps_ids=["UPPER", "LOWER"],
            area=2.5,
            shape="SQUARE",
            width=1.58,
            offsets=[2.0, 3.0],
            open_close_criterion="TEMPERATURE",
            time=[0.0, 100.0, 200.0],
            fraction=[1.0, 0.5, 0.0],
            set_point=150.0,
            device_id="TEMP_SENSOR",
            pre_fraction=0.8,
            post_fraction=0.2,
        )
        assert vent.id == "VENT1"
        assert vent.comps_ids == ["UPPER", "LOWER"]
        assert vent.area == 2.5
        assert vent.shape == "SQUARE"
        assert vent.width == 1.58
        assert vent.offsets == [2.0, 3.0]
        assert vent.open_close_criterion == "TEMPERATURE"
        assert vent.time == [0.0, 100.0, 200.0]
        assert vent.fraction == [1.0, 0.5, 0.0]
        assert vent.set_point == 150.0
        assert vent.device_id == "TEMP_SENSOR"
        assert vent.pre_fraction == 0.8
        assert vent.post_fraction == 0.2

    @pytest.mark.parametrize(
        "comps_ids",
        [
            pytest.param(["UPPER"], id="too-few"),
            pytest.param(["UPPER", "MIDDLE", "LOWER"], id="too-many"),
        ],
    )
    def test_init_invalid_comps_ids_length(self, comps_ids: list[str]):
        """Test that initialization fails with wrong number of compartments."""
        with pytest.raises(ValueError, match="exactly 2 compartments"):
            CeilingFloorVents(id="VENT1", comps_ids=comps_ids, area=1.0)

    def test_init_mismatched_time_fraction_lists(self):
        """Test that initialization fails with mismatched time and fraction lists."""
        with pytest.raises(ValueError, match="equal length"):
            CeilingFloorVents(
                id="VENT1",
                comps_ids=["UPPER", "LOWER"],
                area=1.0,
                time=[0.0, 100.0],
                fraction=[1.0],
            )

    def test_to_input_string_basic(self):
        """Test basic input string generation."""
        vent = CeilingFloorVents(
            id="HOLE1", comps_ids=["RM_UP", "RM_LOW"], area=1.0, shape="ROUND"
        )
        result = vent.to_input_string()
        assert result.startswith("&VENT")
        assert result.endswith("/\n")
        assert "TYPE = 'FLOOR'" in result
        assert "ID = 'HOLE1'" in result
        assert "COMP_IDS = 'RM_UP', 'RM_LOW'" in result
        assert "AREA = 1.0" in result
        assert "SHAPE = 'ROUND'" in result
        assert "None" not in result

    def test_to_input_string_with_offsets(self):
        """Test input string generation with custom offsets."""
        vent = CeilingFloorVents(
            id="VENT1",
            comps_ids=["UPPER", "LOWER"],
            area=2.0,
            shape="SQUARE",
            offsets=[1.5, 2.5],
        )
        result = vent.to_input_string()
        assert "ID = 'VENT1'" in result
        assert "COMP_IDS = 'UPPER', 'LOWER'" in result
        assert "AREA = 2.0" in result
        assert "SHAPE = 'SQUARE'" in result
        assert "OFFSETS = 1.5, 2.5" in result

    def test_to_input_string_with_time_fraction(self):
        """Test input string generation with time and fraction data."""
        vent = CeilingFloorVents(
            id="VENT1",
            comps_ids=["UPPER", "LOWER"],
            area=1.0,
            time=[0.0, 100.0],
            fraction=[1.0, 0.5],
        )
        result = vent.to_input_string()
        assert "ID = 'VENT1'" in result
        assert "T = 0.0, 100.0" in result
        assert "F = 1.0, 0.5" in result

    @pytest.mark.parametrize(
        (
            "criterion",
            "set_point",
            "device_id",
            "pre_frac",
            "post_frac",
            "expected",
            "unexpected",
        ),
        [
            pytest.param(
                "TEMPERATURE",
                150.0,
                "TEMP_SENSOR",
                0.8,
                0.2,
                [
                    "CRITERION = 'TEMPERATURE'",
                    "SETPOINT = 150.0",
                    "DEVC_ID = 'TEMP_SENSOR'",
                    "PRE_FRACTION = 0.8",
                    "POST_FRACTION = 0.2",
                ],
                [],
                id="temperature-full",
            ),
            pytest.param(
                "FLUX",
                50.0,
                None,
                1.0,
                None,
                [
                    "CRITERION = 'FLUX'",
                    "SETPOINT = 50.0",
                    "PRE_FRACTION = 1.0",
                    "POST_FRACTION = 1",
                ],
                [],
                id="flux-no-device",
            ),
        ],
    )
    def test_to_input_string_criterion(
        self,
        make_ceiling_floor_vent,
        criterion,
        set_point,
        device_id,
        pre_frac,
        post_frac,
        expected,
        unexpected,
    ):
        """Test input string generation with various open/close criteria."""
        extra_kwargs: dict[str, str | float] = {"open_close_criterion": criterion}
        if set_point is not None:
            extra_kwargs["set_point"] = set_point
        if device_id is not None:
            extra_kwargs["device_id"] = device_id
        if pre_frac is not None:
            extra_kwargs["pre_fraction"] = pre_frac
        if post_frac is not None:
            extra_kwargs["post_fraction"] = post_frac

        vent = make_ceiling_floor_vent(**extra_kwargs)
        result = vent.to_input_string()

        for nml_field in expected:
            assert nml_field in result
        for nml_field in unexpected:
            assert nml_field not in result

    def test_to_input_string_with_all_options(self):
        """Test input string generation with all possible options."""
        vent = CeilingFloorVents(
            id="COMPLEX_VENT",
            comps_ids=["TOP_ROOM", "BOTTOM_ROOM"],
            area=3.14,
            shape="ROUND",
            width=2.0,
            offsets=[1.0, 2.0],
            open_close_criterion="TIME",
            time=[0.0, 50.0, 100.0],
            fraction=[1.0, 0.5, 0.0],
            set_point=75.0,
            device_id="CONTROLLER",
            pre_fraction=0.9,
            post_fraction=0.1,
        )
        result = vent.to_input_string()
        assert result.startswith("&VENT")
        assert result.endswith("/\n")
        assert "ID = 'COMPLEX_VENT'" in result
        assert "COMP_IDS = 'TOP_ROOM', 'BOTTOM_ROOM'" in result
        assert "AREA = 3.14" in result
        assert "SHAPE = 'ROUND'" in result
        assert "CRITERION = 'TIME'" in result
        assert "SETPOINT = 75.0" in result
        assert "DEVC_ID = 'CONTROLLER'" in result
        assert "PRE_FRACTION = 0.9" in result
        assert "POST_FRACTION = 0.1" in result
        assert "T = 0.0, 50.0, 100.0" in result
        assert "F = 1.0, 0.5, 0.0" in result
        assert "OFFSETS = 1.0, 2.0" in result
        assert "None" not in result

    def test_default_offsets(self):
        """Test that default offsets are set when None is provided."""
        vent = CeilingFloorVents(
            id="VENT1", comps_ids=["UPPER", "LOWER"], area=1.0, offsets=None
        )
        assert vent.offsets == [0, 0]

    def test_compartment_ids_formatting(self):
        """Test that compartment IDs are properly quoted in output."""
        vent = CeilingFloorVents(
            id="TEST_VENT", comps_ids=["COMP_1", "COMP_2"], area=1.0
        )
        result = vent.to_input_string()
        assert "COMP_IDS = 'COMP_1', 'COMP_2'" in result

    def test_repr(self):
        """Test __repr__ method."""
        vent = CeilingFloorVents(
            id="STAIR_VENT",
            comps_ids=["UPPER_FLOOR", "LOWER_FLOOR"],
            area=2.0,
            shape="SQUARE",
            width=1.4,
            offsets=[1.0, 2.0],
        )

        repr_str = repr(vent)
        assert "CeilingFloorVents(" in repr_str
        assert "id='STAIR_VENT'" in repr_str
        assert "comps_ids=['UPPER_FLOOR', 'LOWER_FLOOR']" in repr_str
        assert "area=2.0" in repr_str
        assert "shape='SQUARE'" in repr_str
        assert "width=1.4" in repr_str
        assert "offsets=[1.0, 2.0]" in repr_str

    def test_str(self):
        """Test __str__ method."""
        vent = CeilingFloorVents(
            id="STAIR_OPENING",
            comps_ids=["UPPER_ROOM", "LOWER_ROOM"],
            area=3.5,
            shape="ROUND",
            width=2.1,
        )

        str_repr = str(vent)
        assert "Ceiling/Floor Vent 'STAIR_OPENING':" in str_repr
        assert "UPPER_ROOM ↕ LOWER_ROOM" in str_repr
        assert "area: 3.5 m²" in str_repr
        assert "shape: ROUND" in str_repr
        assert "width: 2.1" in str_repr

    def test_str_with_criterion(self):
        """Test __str__ method with opening criterion."""
        vent = CeilingFloorVents(
            id="CONTROLLED_VENT",
            comps_ids=["UP", "DOWN"],
            area=1.0,
            shape="SQUARE",
            open_close_criterion="TEMPERATURE",
        )

        str_repr = str(vent)
        assert "criterion: TEMPERATURE" in str_repr

    # Note: __eq__ and __hash__ methods not implemented in current version
    # These tests are removed to match actual implementation

    def test_getitem(self) -> None:
        """Test __getitem__ method."""
        vent = CeilingFloorVents(
            id="TEST_VENT",
            comps_ids=["ROOM1", "ROOM2"],
            area=2.5,
            shape="SQUARE",
            width=1.6,
            offsets=[1.0, 2.0],
        )

        assert vent["id"] == "TEST_VENT"
        assert vent["comps_ids"] == ["ROOM1", "ROOM2"]
        assert vent["area"] == 2.5
        assert vent["shape"] == "SQUARE"
        assert vent["width"] == 1.6
        assert vent["offsets"] == [1.0, 2.0]

    def test_getitem_invalid_key(self) -> None:
        """Test __getitem__ method with invalid key."""
        vent = CeilingFloorVents(id="VENT1", comps_ids=["UP", "DOWN"], area=1.0)

        with pytest.raises(
            KeyError, match="Property 'invalid_key' not found in CeilingFloorVents"
        ):
            vent["invalid_key"]

    def test_setitem(self) -> None:
        """Test __setitem__ method."""
        vent = CeilingFloorVents(id="VENT1", comps_ids=["UP", "DOWN"], area=1.0)

        vent["id"] = "NEW_VENT"
        assert vent.id == "NEW_VENT"

        vent["area"] = 2.5
        assert vent.area == 2.5

        vent["shape"] = "SQUARE"
        assert vent.shape == "SQUARE"

        vent["width"] = 1.8
        assert vent.width == 1.8

    def test_setitem_invalid_key(self) -> None:
        """Test __setitem__ method with invalid key."""
        vent = CeilingFloorVents(id="VENT1", comps_ids=["UP", "DOWN"], area=1.0)

        with pytest.raises(KeyError, match="Cannot set 'invalid_key'"):
            vent["invalid_key"] = "value"

    def test_repr_html(self) -> None:
        """Test _repr_html_ method."""
        vent = CeilingFloorVents(
            id="STAIR_VENT",
            comps_ids=["UPPER_FLOOR", "LOWER_FLOOR"],
            area=2.0,
            shape="SQUARE",
            width=1.4,
            offsets=[1.0, 2.0],
        )

        html_str = vent._repr_html_()

        # Check that it returns valid HTML string
        assert isinstance(html_str, str)
        assert len(html_str) > 0

        # Check for expected HTML structure
        assert '<div class="pycfast-card' in html_str
        assert "Ceiling/Floor Vent: STAIR_VENT" in html_str
        assert "UPPER_FLOOR ↕ LOWER_FLOOR" in html_str

        # Check vent properties
        assert "2.0 m²" in html_str
        assert "SQUARE" in html_str
        assert "1.4" in html_str


class TestCeilingFloorVentsSetItemValidation:
    """Test validation in __setitem__ to ensure data integrity."""

    @pytest.mark.parametrize(
        "invalid_comps_ids",
        [
            pytest.param(["ONLY_ONE"], id="too-few"),
            pytest.param(["C1", "C2", "C3"], id="too-many"),
        ],
    )
    def test_setitem_invalid_comps_ids_length(
        self, make_ceiling_floor_vent, invalid_comps_ids
    ):
        """Test that __setitem__ rejects comps_ids with wrong length."""
        vent = make_ceiling_floor_vent()
        with pytest.raises(
            ValueError, match="Ceiling/floor vent must connect exactly 2 compartments"
        ):
            vent["comps_ids"] = invalid_comps_ids

    @pytest.mark.parametrize(
        ("key", "value"),
        [
            pytest.param("time", [0.0, 100.0, 200.0], id="time-longer-than-fraction"),
            pytest.param("fraction", [1.0], id="fraction-shorter-than-time"),
        ],
    )
    def test_setitem_mismatched_time_fraction(
        self, make_ceiling_floor_vent, key, value
    ):
        """Test that __setitem__ rejects mismatched time/fraction list lengths."""
        vent = make_ceiling_floor_vent(time=[0.0, 100.0], fraction=[1.0, 0.5])
        with pytest.raises(
            ValueError, match="Time and fraction lists must be of equal length"
        ):
            vent[key] = value

    def test_setitem_valid_area_change(self, make_ceiling_floor_vent):
        """Test that __setitem__ accepts valid property changes."""
        vent = make_ceiling_floor_vent()
        vent["area"] = 3.5
        assert vent.area == 3.5

    def test_setitem_invalid_does_not_mutate_state(self, make_ceiling_floor_vent):
        """Test that a failed __setitem__ rolls back to the previous value."""
        vent = make_ceiling_floor_vent(comps_ids=["UPPER", "LOWER"])
        before = vent.comps_ids.copy()

        with pytest.raises(ValueError):
            vent["comps_ids"] = ["ONLY_ONE"]

        assert vent.comps_ids == before
