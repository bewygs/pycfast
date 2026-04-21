from __future__ import annotations

import pytest

from pycfast.wall_vent import WallVent

"""
Tests for the WallVent class.
"""


@pytest.fixture()
def make_wall_vent():
    """Create a WallVent instance with sensible defaults."""

    def _make(**kwargs: object) -> WallVent:
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
        return WallVent(**defaults)  # type: ignore[arg-type]

    return _make


class TestWallVent:
    """Test class for WallVent."""

    def test_init_basic(self):
        """Test basic initialization with required parameters."""
        vent = WallVent(
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
        vent = WallVent(
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
        """Test initialization with default values (zero height/width warns about no flow)."""
        with pytest.warns(UserWarning, match="height or width is 0"):
            vent = WallVent(id="DOOR1", comps_ids=["ROOM1", "ROOM2"])
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
            WallVent(id="DOOR1", comps_ids=comps_ids)

    def test_init_outside_as_first_compartment(self):
        """Test error when OUTSIDE is the first compartment."""
        with pytest.raises(ValueError, match="Compartment order is incorrect"):
            WallVent(id="DOOR1", comps_ids=["OUTSIDE", "ROOM1"])

    @pytest.mark.parametrize("param", ["height", "width", "bottom"])
    def test_init_negative_dimension(self, make_wall_vent, param: str):
        """Test that initialization fails with negative height, width, or bottom."""
        with pytest.raises(ValueError, match="must be non-negative"):
            make_wall_vent(**{param: -1.0})  # type: ignore[arg-type]

    @pytest.mark.parametrize("param", ["pre_fraction", "post_fraction"])
    def test_init_pre_post_fraction_out_of_range(self, make_wall_vent, param: str):
        """Test that initialization fails with pre/post_fraction outside [0, 1]."""
        with pytest.raises(ValueError, match=r"must be in \[0, 1\]"):
            make_wall_vent(**{param: 1.5})  # type: ignore[arg-type]

    def test_init_fraction_values_out_of_range(self, make_wall_vent):
        """Test that initialization fails with fraction values outside [0, 1]."""
        with pytest.raises(ValueError, match=r"must be in \[0, 1\]"):
            make_wall_vent(fraction=[-0.5, 1.0])

    def test_init_mismatched_time_fraction_lists(self):
        """Test that initialization fails with mismatched time and fraction lists."""
        with pytest.raises(ValueError, match="equal length"):
            WallVent(
                id="DOOR1",
                comps_ids=["ROOM1", "ROOM2"],
                open_close_criterion="TIME",
                time=[0.0, 100.0],
                fraction=[1.0],
            )

    @pytest.mark.parametrize(
        "face",
        ["BACK", "TOP", "BOTTOM", "invalid"],
    )
    def test_init_invalid_face(self, make_wall_vent, face: str):
        """Test that initialization fails with invalid face value."""
        with pytest.raises(ValueError, match="face must be one of"):
            make_wall_vent(face=face)

    @pytest.mark.parametrize(
        "criterion",
        ["WIND", "PRESSURE", "invalid"],
    )
    def test_init_invalid_open_close_criterion(self, make_wall_vent, criterion: str):
        """Test that initialization fails with invalid open_close_criterion."""
        with pytest.raises(ValueError, match="open_close_criterion must be one of"):
            make_wall_vent(open_close_criterion=criterion)

    def test_init_temperature_criterion_missing_set_point(self, make_wall_vent):
        """Test that TEMPERATURE criterion without set_point raises."""
        with pytest.raises(ValueError, match="set_point must be specified"):
            make_wall_vent(open_close_criterion="TEMPERATURE", device_id="SENSOR")

    def test_init_temperature_criterion_missing_device_id(self, make_wall_vent):
        """Test that TEMPERATURE criterion without device_id raises."""
        with pytest.raises(ValueError, match="device_id must be specified"):
            make_wall_vent(open_close_criterion="TEMPERATURE", set_point=150.0)

    def test_init_time_criterion_missing_lists(self, make_wall_vent):
        """Test that TIME criterion without time/fraction raises."""
        with pytest.raises(ValueError, match="time and fraction must be specified"):
            make_wall_vent(open_close_criterion="TIME")

    def test_init_time_criterion_negative_time(self, make_wall_vent):
        """Test that negative time values raise."""
        with pytest.raises(ValueError, match="non-negative"):
            make_wall_vent(
                open_close_criterion="TIME",
                time=[-10.0, 100.0],
                fraction=[1.0, 0.5],
            )

    def test_init_time_criterion_non_monotonic(self, make_wall_vent):
        """Test that non-monotonically increasing time values raise."""
        with pytest.raises(ValueError, match="monotonically increasing"):
            make_wall_vent(
                open_close_criterion="TIME",
                time=[0.0, 200.0, 100.0],
                fraction=[1.0, 0.5, 0.0],
            )

    def test_init_invalid_comps_ids_type(self):
        """Test that non-list comps_ids raises TypeError."""
        with pytest.raises(TypeError, match="comps_ids must be a list"):
            WallVent(id="DOOR1", comps_ids="ROOM1,ROOM2")  # type: ignore[arg-type]

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
        vent = WallVent(
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
            "time",
            "fraction",
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
                None,
                None,
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
                "FLUX_SENSOR",
                1.0,
                None,
                None,
                None,
                [
                    "CRITERION = 'FLUX'",
                    "SETPOINT = 50.0",
                    "DEVC_ID = 'FLUX_SENSOR'",
                    "PRE_FRACTION = 1.0",
                ],
                [],
                id="flux-with-device",
            ),
            pytest.param(
                "TIME",
                None,
                None,
                None,
                None,
                [0.0, 100.0],
                [1.0, 0.5],
                [
                    "CRITERION = 'TIME'",
                    "T = 0.0, 100.0",
                    "F = 1.0, 0.5",
                ],
                [],
                id="time-with-lists",
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
        time,
        fraction,
        expected,
        unexpected,
    ):
        """Test input string generation with various open/close criteria."""
        extra_kwargs: dict[str, object] = {"open_close_criterion": criterion}
        if set_point is not None:
            extra_kwargs["set_point"] = set_point
        if device_id is not None:
            extra_kwargs["device_id"] = device_id
        if pre_frac is not None:
            extra_kwargs["pre_fraction"] = pre_frac
        if post_frac is not None:
            extra_kwargs["post_fraction"] = post_frac
        if time is not None:
            extra_kwargs["time"] = time
        if fraction is not None:
            extra_kwargs["fraction"] = fraction

        vent = make_wall_vent(**extra_kwargs)
        result = vent.to_input_string()

        for nml_field in expected:
            assert nml_field in result
        for nml_field in unexpected:
            assert nml_field not in result

    @pytest.mark.parametrize("face", ["FRONT", "REAR", "RIGHT", "LEFT"])
    def test_to_input_string_face(self, make_wall_vent, face):
        """Test input string generation with different face orientations."""
        vent = make_wall_vent(id=f"VENT_{face}", face=face)
        result = vent.to_input_string()
        assert f"FACE = '{face}'" in result

    def test_to_input_string_complex_scenario(self):
        """Test input string generation with all options combined."""
        vent = WallVent(
            id="COMPLEX_DOOR",
            comps_ids=["LIVING", "KITCHEN"],
            bottom=0.1,
            height=1.9,
            width=0.8,
            face="REAR",
            offset=2.5,
            open_close_criterion="TEMPERATURE",
            set_point=75.0,
            device_id="CONTROLLER",
            pre_fraction=0.1,
            post_fraction=0.9,
        )
        result = vent.to_input_string()

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
        assert "FACE = 'REAR'" in result
        assert "OFFSET = 2.5" in result

    # Tests for dunder methods
    def test_repr(self) -> None:
        """Test __repr__ method."""
        vent = WallVent(
            id="DOOR_MAIN",
            comps_ids=["LIVING_ROOM", "KITCHEN"],
            bottom=0.0,
            height=2.1,
            width=0.9,
            face="RIGHT",
            offset=1.5,
        )

        repr_str = repr(vent)
        assert "WallVent(" in repr_str
        assert "id='DOOR_MAIN'" in repr_str
        assert "comps_ids=['LIVING_ROOM', 'KITCHEN']" in repr_str
        assert "bottom=0.0" in repr_str
        assert "height=2.1" in repr_str
        assert "width=0.9" in repr_str
        assert "face='RIGHT'" in repr_str

    def test_str(self) -> None:
        """Test __str__ method."""
        vent = WallVent(
            id="WINDOW_01",
            comps_ids=["BEDROOM", "OUTSIDE"],
            bottom=1.0,
            height=1.2,
            width=1.5,
            face="FRONT",
            offset=2.0,
            open_close_criterion="TEMPERATURE",
            set_point=150.0,
            device_id="TEMP_SENSOR",
        )

        str_repr = str(vent)
        assert "Wall Vent 'WINDOW_01'" in str_repr
        assert "BEDROOM ↔ OUTSIDE" in str_repr
        assert "1.5x1.2 m" in str_repr
        assert "bottom: 1.0 m" in str_repr

    def test_getitem(self) -> None:
        """Test __getitem__ method."""
        vent = WallVent(
            id="TEST_VENT",
            comps_ids=["COMP1", "COMP2"],
            bottom=0.5,
            height=1.8,
            width=0.8,
            face="REAR",
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
        assert vent["face"] == "REAR"
        assert vent["offset"] == 2.5
        assert vent["open_close_criterion"] == "TEMPERATURE"
        assert vent["set_point"] == 100.0
        assert vent["device_id"] == "TEMP_SENSOR_01"
        assert vent["pre_fraction"] == 0.0
        assert vent["post_fraction"] == 1.0

    def test_getitem_invalid_key(self) -> None:
        """Test __getitem__ method with invalid key."""
        vent = WallVent(
            id="VENT1",
            comps_ids=["A", "B"],
            bottom=0.0,
            height=1.0,
            width=1.0,
            face="FRONT",
            offset=0.0,
        )

        with pytest.raises(
            KeyError, match="Property 'invalid_key' not found in WallVent"
        ):
            vent["invalid_key"]

    def test_setitem(self) -> None:
        """Test __setitem__ method."""
        vent = WallVent(
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


class TestWallVentSetItemValidation:
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
        vent = make_wall_vent(
            open_close_criterion="TIME", time=[0.0, 100.0], fraction=[1.0, 0.5]
        )
        with pytest.raises(ValueError, match="equal length"):
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

    def test_setitem_invalid_does_not_mutate_state(self, make_wall_vent):
        """Test that a failed __setitem__ rolls back to the previous value."""
        vent = make_wall_vent(comps_ids=["ROOM1", "OUTSIDE"])
        before = vent.comps_ids.copy()

        with pytest.raises(ValueError):
            vent["comps_ids"] = ["OUTSIDE", "ROOM1"]

        assert vent.comps_ids == before
