from __future__ import annotations

import pytest

from pycfast.wall_vents import WallVents

"""
Tests for the WallVents class.
"""


@pytest.fixture()
def make_wall_vent():
    """Create a WallVents instance with sensible defaults."""

    def _make(**kwargs: object) -> WallVents:
        defaults: dict[str, object] = {
            "id": "DOOR1",
            "comps_ids": ["ROOM1", "ROOM2"],
            "bottom": 0.0,
            "height": 2.0,
            "width": 0.9,
            "face": "RIGHT",
            "offset": 1.0,
        }
        defaults.update(kwargs)
        return WallVents(**defaults)  # type: ignore[arg-type]

    return _make


class TestWallVents:
    """Test class for WallVents."""

    def test_init_basic(self):
        """Test basic initialization with required parameters."""
        vent = WallVents(
            id="DOOR1",
            comps_ids=["ROOM1", "ROOM2"],
            bottom=0.0,
            height=2.0,
            width=0.9,
            face="RIGHT",
            offset=1.0,
        )
        assert vent.id == "DOOR1"
        assert vent.comps_ids == ["ROOM1", "ROOM2"]
        assert vent.bottom == 0.0
        assert vent.height == 2.0
        assert vent.width == 0.9
        assert vent.face == "RIGHT"
        assert vent.offset == 1.0
        assert vent.open_close_criterion is None
        assert vent.time is None
        assert vent.fraction is None
        assert vent.set_point is None
        assert vent.device_id is None
        assert vent.pre_fraction == 1
        assert vent.post_fraction == 1

    def test_init_with_all_parameters(self):
        """Test initialization with all parameters."""
        vent = WallVents(
            id="DOOR1",
            comps_ids=["ROOM1", "ROOM2"],
            bottom=0.0,
            height=2.0,
            width=0.9,
            face="RIGHT",
            offset=1.0,
            open_close_criterion="TEMPERATURE",
            time=[0.0, 100.0, 200.0],
            fraction=[1.0, 0.5, 0.0],
            set_point=150.0,
            device_id="TEMP_SENSOR",
            pre_fraction=0.8,
            post_fraction=0.2,
        )
        assert vent.id == "DOOR1"
        assert vent.comps_ids == ["ROOM1", "ROOM2"]
        assert vent.bottom == 0.0
        assert vent.height == 2.0
        assert vent.width == 0.9
        assert vent.face == "RIGHT"
        assert vent.offset == 1.0
        assert vent.open_close_criterion == "TEMPERATURE"
        assert vent.time == [0.0, 100.0, 200.0]
        assert vent.fraction == [1.0, 0.5, 0.0]
        assert vent.set_point == 150.0
        assert vent.device_id == "TEMP_SENSOR"
        assert vent.pre_fraction == 0.8
        assert vent.post_fraction == 0.2

    def test_init_default_values(self):
        """Test initialization with default values."""
        vent = WallVents(id="DOOR1", comps_ids=["ROOM1", "ROOM2"])
        assert vent.bottom == 0
        assert vent.height == 0
        assert vent.width == 0
        assert vent.face == ""
        assert vent.offset == 0

    @pytest.mark.parametrize(
        "comps_ids",
        [
            pytest.param(["ROOM1"], id="too-few"),
            pytest.param(["ROOM1", "ROOM2", "ROOM3"], id="too-many"),
        ],
    )
    def test_init_invalid_comps_ids_length(self, comps_ids: list[str]):
        """Test that initialization fails with wrong number of compartments."""
        with pytest.raises(ValueError, match="exactly 2 compartments"):
            WallVents(id="DOOR1", comps_ids=comps_ids)

    def test_init_outside_as_first_compartment(self):
        """Test error when OUTSIDE is the first compartment."""
        with pytest.raises(ValueError, match="Compartment order is incorrect"):
            WallVents(id="DOOR1", comps_ids=["OUTSIDE", "ROOM1"])

    def test_init_mismatched_time_fraction_lists(self):
        """Test that initialization fails with mismatched time and fraction lists."""
        with pytest.raises(ValueError, match="equal length"):
            WallVents(
                id="DOOR1",
                comps_ids=["ROOM1", "ROOM2"],
                time=[0.0, 100.0],
                fraction=[1.0],
            )

    def test_to_input_string_basic(self, make_wall_vent):
        """Test basic input string generation."""
        vent = make_wall_vent()
        result = vent.to_input_string()
        assert result.startswith("&VENT")
        assert result.endswith("/\n")
        assert "TYPE = 'WALL'" in result
        assert "ID = 'DOOR1'" in result
        assert "COMP_IDS = 'ROOM1', 'ROOM2'" in result
        assert "BOTTOM = 0.0" in result
        assert "HEIGHT = 2.0" in result
        assert "WIDTH = 0.9" in result
        assert "FACE = 'RIGHT'" in result
        assert "OFFSET = 1.0" in result
        assert "None" not in result

    def test_to_input_string_with_outside(self):
        """Test input string generation with outside compartment."""
        vent = WallVents(
            id="WINDOW1",
            comps_ids=["ROOM1", "OUTSIDE"],
            bottom=1.0,
            height=1.5,
            width=2.0,
            face="FRONT",
            offset=0.5,
        )
        result = vent.to_input_string()
        assert "COMP_IDS = 'ROOM1', 'OUTSIDE'" in result

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
            pytest.param(
                "TIME",
                30.0,
                "TIMER",
                None,
                None,
                [
                    "CRITERION = 'TIME'",
                    "SETPOINT = 30.0",
                    "DEVC_ID = 'TIMER'",
                ],
                [],
                id="time-with-device",
            ),
            pytest.param(
                "TEMPERATURE",
                None,
                "TEMP_SENSOR",
                None,
                None,
                [
                    "CRITERION = 'TEMPERATURE'",
                    "DEVC_ID = 'TEMP_SENSOR'",
                ],
                ["SETPOINT"],
                id="temperature-no-setpoint",
            ),
        ],
    )
    def test_to_input_string_criterion(
        self,
        make_wall_vent,
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

        vent = make_wall_vent(**extra_kwargs)
        result = vent.to_input_string()

        for nml_field in expected:
            assert nml_field in result
        for nml_field in unexpected:
            assert nml_field not in result

    def test_to_input_string_with_time_fraction(self, make_wall_vent):
        """Test input string generation with time and fraction data."""
        vent = make_wall_vent(
            time=[0.0, 100.0, 200.0],
            fraction=[1.0, 0.5, 0.0],
        )
        result = vent.to_input_string()
        assert "T = 0.0, 100.0, 200.0" in result
        assert "F = 1.0, 0.5, 0.0" in result

    @pytest.mark.parametrize("face", ["FRONT", "BACK", "RIGHT", "LEFT"])
    def test_to_input_string_face(self, make_wall_vent, face):
        """Test input string generation with different face orientations."""
        vent = make_wall_vent(id=f"VENT_{face}", face=face)
        result = vent.to_input_string()
        assert f"FACE = '{face}'" in result

    def test_to_input_string_complex_scenario(self):
        """Test input string generation with all options combined."""
        vent = WallVents(
            id="COMPLEX_DOOR",
            comps_ids=["LIVING", "KITCHEN"],
            bottom=0.1,
            height=1.9,
            width=0.8,
            face="BACK",
            offset=2.5,
            open_close_criterion="TEMPERATURE",
            time=[0.0, 50.0, 100.0, 150.0],
            fraction=[0.0, 0.3, 0.8, 1.0],
            set_point=75.0,
            device_id="CONTROLLER",
            pre_fraction=0.1,
            post_fraction=0.9,
        )
        result = vent.to_input_string()

        # Check all components are present
        assert "ID = 'COMPLEX_DOOR'" in result
        assert "COMP_IDS = 'LIVING', 'KITCHEN'" in result
        assert "BOTTOM = 0.1" in result
        assert "HEIGHT = 1.9" in result
        assert "WIDTH = 0.8" in result
        assert "CRITERION = 'TEMPERATURE'" in result
        assert "SETPOINT = 75.0" in result
        assert "DEVC_ID = 'CONTROLLER'" in result
        assert "PRE_FRACTION = 0.1" in result
        assert "POST_FRACTION = 0.9" in result
        assert "T = 0.0, 50.0, 100.0, 150.0" in result
        assert "F = 0.0, 0.3, 0.8, 1.0" in result
        assert "FACE = 'BACK'" in result
        assert "OFFSET = 2.5" in result

    def test_compartment_ids_formatting(self):
        """Test that compartment IDs are properly quoted in output."""
        vent = WallVents(
            id="TEST_VENT",
            comps_ids=["COMP_A", "COMP_B"],
            bottom=0.0,
            height=2.0,
            width=1.0,
            face="FRONT",
            offset=0.0,
        )
        result = vent.to_input_string()
        assert "COMP_IDS = 'COMP_A', 'COMP_B'" in result

    # Tests for dunder methods
    def test_repr(self) -> None:
        """Test __repr__ method."""
        vent = WallVents(
            id="DOOR_MAIN",
            comps_ids=["LIVING_ROOM", "KITCHEN"],
            bottom=0.0,
            height=2.1,
            width=0.9,
            face="RIGHT",
            offset=1.5,
            open_close_criterion="TIME",
            set_point=60.0,
        )

        repr_str = repr(vent)
        assert "WallVents(" in repr_str
        assert "id='DOOR_MAIN'" in repr_str
        assert "comps_ids=['LIVING_ROOM', 'KITCHEN']" in repr_str
        assert "bottom=0.0" in repr_str
        assert "height=2.1" in repr_str
        assert "width=0.9" in repr_str
        assert "face='RIGHT'" in repr_str

    def test_str(self) -> None:
        """Test __str__ method."""
        vent = WallVents(
            id="WINDOW_01",
            comps_ids=["BEDROOM", "OUTSIDE"],
            bottom=1.0,
            height=1.2,
            width=1.5,
            face="FRONT",
            offset=2.0,
            open_close_criterion="TEMPERATURE",
            set_point=150.0,
        )

        str_repr = str(vent)
        assert "Wall Vent 'WINDOW_01'" in str_repr
        assert "BEDROOM ↔ OUTSIDE" in str_repr
        assert "1.5x1.2 m" in str_repr
        assert "bottom: 1.0 m" in str_repr

    def test_getitem(self) -> None:
        """Test __getitem__ method."""
        vent = WallVents(
            id="TEST_VENT",
            comps_ids=["COMP1", "COMP2"],
            bottom=0.5,
            height=1.8,
            width=0.8,
            face="BACK",
            offset=2.5,
            open_close_criterion="TEMPERATURE",
            set_point=100.0,
            device_id="TEMP_SENSOR_01",
            pre_fraction=0.0,
            post_fraction=1.0,
        )

        assert vent["id"] == "TEST_VENT"
        assert vent["comps_ids"] == ["COMP1", "COMP2"]
        assert vent["bottom"] == 0.5
        assert vent["height"] == 1.8
        assert vent["width"] == 0.8
        assert vent["face"] == "BACK"
        assert vent["offset"] == 2.5
        assert vent["open_close_criterion"] == "TEMPERATURE"
        assert vent["set_point"] == 100.0
        assert vent["device_id"] == "TEMP_SENSOR_01"
        assert vent["pre_fraction"] == 0.0
        assert vent["post_fraction"] == 1.0

    def test_getitem_invalid_key(self) -> None:
        """Test __getitem__ method with invalid key."""
        vent = WallVents(
            id="VENT1",
            comps_ids=["A", "B"],
            bottom=0.0,
            height=1.0,
            width=1.0,
            face="FRONT",
            offset=0.0,
        )

        with pytest.raises(
            KeyError, match="Property 'invalid_key' not found in WallVents"
        ):
            vent["invalid_key"]

    def test_setitem(self) -> None:
        """Test __setitem__ method."""
        vent = WallVents(
            id="VENT1",
            comps_ids=["A", "B"],
            bottom=0.0,
            height=1.0,
            width=1.0,
            face="FRONT",
            offset=0.0,
        )

        # Test setting various properties
        vent["id"] = "NEW_VENT"
        assert vent.id == "NEW_VENT"

        vent["comps_ids"] = ["ROOM1", "ROOM2"]
        assert vent.comps_ids == ["ROOM1", "ROOM2"]

        vent["bottom"] = 0.3
        assert vent.bottom == 0.3

        vent["height"] = 2.5
        assert vent.height == 2.5

        vent["width"] = 1.2
        assert vent.width == 1.2

        vent["face"] = "LEFT"
        assert vent.face == "LEFT"

        vent["offset"] = 3.0
        assert vent.offset == 3.0

    def test_setitem_invalid_key(self) -> None:
        """Test __setitem__ method with invalid key."""
        vent = WallVents(
            id="VENT1",
            comps_ids=["A", "B"],
            bottom=0.0,
            height=1.0,
            width=1.0,
            face="FRONT",
            offset=0.0,
        )

        with pytest.raises(KeyError, match="Cannot set 'invalid_key'"):
            vent["invalid_key"] = "value"

    def test_repr_html(self) -> None:
        """Test _repr_html_ method."""
        vent = WallVents(
            id="DOOR_MAIN",
            comps_ids=["LIVING_ROOM", "KITCHEN"],
            bottom=0.0,
            height=2.1,
            width=0.9,
            face="RIGHT",
            offset=1.5,
            open_close_criterion="TIME",
            set_point=60.0,
        )

        html_str = vent._repr_html_()

        # Check that it returns valid HTML string
        assert isinstance(html_str, str)
        assert len(html_str) > 0

        # Check for expected HTML structure
        assert '<div class="pycfast-card' in html_str
        assert "Wall Vent: DOOR_MAIN" in html_str
        assert "LIVING_ROOM ↔ KITCHEN" in html_str

        # Check vent properties
        assert "2.1" in html_str  # height
        assert "0.9" in html_str  # width
        assert "RIGHT" in html_str  # face
        assert "1.5" in html_str  # offset


class TestWallVentsSetItemValidation:
    """Test validation in __setitem__ to ensure data integrity."""

    @pytest.mark.parametrize(
        "invalid_comps_ids",
        [
            pytest.param(["ONLY_ONE"], id="too-few"),
            pytest.param(["COMP1", "COMP2", "COMP3"], id="too-many"),
        ],
    )
    def test_setitem_invalid_comps_ids_length(self, make_wall_vent, invalid_comps_ids):
        """Test that __setitem__ rejects comps_ids with wrong length."""
        vent = make_wall_vent()
        with pytest.raises(
            ValueError, match="Wall vent must connect exactly 2 compartments"
        ):
            vent["comps_ids"] = invalid_comps_ids

    def test_setitem_invalid_comps_ids_outside_first(self, make_wall_vent):
        """Test that __setitem__ rejects OUTSIDE as first compartment."""
        vent = make_wall_vent()
        with pytest.raises(ValueError, match="Compartment order is incorrect"):
            vent["comps_ids"] = ["OUTSIDE", "ROOM1"]

    def test_setitem_valid_comps_ids_outside_second(self, make_wall_vent):
        """Test that __setitem__ accepts OUTSIDE as second compartment."""
        vent = make_wall_vent()
        vent["comps_ids"] = ["ROOM1", "OUTSIDE"]
        assert vent.comps_ids == ["ROOM1", "OUTSIDE"]

    @pytest.mark.parametrize(
        ("key", "value"),
        [
            pytest.param("time", [0.0, 100.0, 200.0], id="time-longer-than-fraction"),
            pytest.param("fraction", [1.0], id="fraction-shorter-than-time"),
        ],
    )
    def test_setitem_mismatched_time_fraction(self, make_wall_vent, key, value):
        """Test that __setitem__ rejects mismatched time/fraction list lengths."""
        vent = make_wall_vent(time=[0.0, 100.0], fraction=[1.0, 0.5])
        with pytest.raises(
            ValueError, match="Time and fraction lists must be of equal length"
        ):
            vent[key] = value

    def test_setitem_valid_matching_time_fraction(self, make_wall_vent):
        """Test that __setitem__ accepts matching time/fraction when both are None initially.

        Note: If time and fraction are already set, they cannot be changed independently
        due to the validation constraint. This is expected behavior.
        """
        vent = make_wall_vent(time=None, fraction=None)

        vent["time"] = [0.0, 100.0, 200.0]
        assert vent.time == [0.0, 100.0, 200.0]

        vent["fraction"] = [1.0, 0.5, 0.0]
        assert len(vent.time) == len(vent.fraction) == 3

    def test_setitem_nonexistent_property(self, make_wall_vent):
        """Test that __setitem__ rejects setting nonexistent properties."""
        vent = make_wall_vent()
        with pytest.raises(KeyError, match="Cannot set 'nonexistent'"):
            vent["nonexistent"] = "value"

    def test_setitem_valid_dimension_changes(self, make_wall_vent):
        """Test that __setitem__ accepts valid dimension changes."""
        vent = make_wall_vent()

        vent["width"] = 2.5
        vent["height"] = 3.0
        vent["bottom"] = 0.5

        assert vent.width == 2.5
        assert vent.height == 3.0
        assert vent.bottom == 0.5

    def test_setitem_invalid_does_not_mutate_state(self, make_wall_vent):
        vent = make_wall_vent(comps_ids=["ROOM1", "OUTSIDE"])
        before = vent.comps_ids.copy()

        with pytest.raises(ValueError):
            vent["comps_ids"] = ["OUTSIDE", "ROOM1"]

        assert vent.comps_ids == before
