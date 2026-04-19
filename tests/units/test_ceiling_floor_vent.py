from __future__ import annotations

import pytest

from pycfast.ceiling_floor_vent import CeilingFloorVent

"""
Tests for the CeilingFloorVent class.
"""


@pytest.fixture()
def make_ceiling_floor_vent():
    """Create a CeilingFloorVent instance with sensible defaults."""

    def _make(**kwargs: object) -> CeilingFloorVent:
        defaults: dict[str, object] = {
            "id": "VENT1",
            "comps_ids": ["UPPER", "LOWER"],
            "area": 1.0,
        }
        defaults.update(kwargs)
        return CeilingFloorVent(**defaults)  # type: ignore[arg-type]

    return _make


class TestCeilingFloorVent:
    """Test class for CeilingFloorVent."""

    def test_init_basic(self):
        """Test basic initialization with required parameters."""
        vent = CeilingFloorVent(id="VENT1", comps_ids=["UPPER", "LOWER"], area=1.0)
        assert vent.id == "VENT1"
        assert vent.comps_ids == ["UPPER", "LOWER"]
        assert vent.area == 1.0
        assert vent.shape == "ROUND"
        assert vent.width is None
        assert vent.offsets == [0, 0]

    def test_init_with_all_parameters(self):
        """Test initialization with all parameters."""
        vent = CeilingFloorVent(
            id="VENT1",
            comps_ids=["UPPER", "LOWER"],
            area=2.5,
            shape="SQUARE",
            width=1.58,
            offsets=[2.0, 3.0],
            open_close_criterion="TEMPERATURE",
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
        assert vent.set_point == 150.0
        assert vent.device_id == "TEMP_SENSOR"
        assert vent.pre_fraction == 0.8
        assert vent.post_fraction == 0.2

    @pytest.mark.parametrize(
        ("param", "value"),
        [
            pytest.param("comps_ids", "AB", id="comps_ids-string"),
            pytest.param("comps_ids", ("UPPER", "LOWER"), id="comps_ids-tuple"),
            pytest.param("offsets", (1.0, 2.0), id="offsets-tuple"),
            pytest.param("offsets", 1.0, id="offsets-float"),
        ],
    )
    def test_required_list_params_wrong_type(self, param, value):
        """Test that required list parameters reject non-list types."""
        kwargs: dict[str, object] = {
            "id": "VENT1",
            "comps_ids": ["UPPER", "LOWER"],
            "area": 1.0,
            param: value,
        }
        with pytest.raises(TypeError, match=f"{param} must be a list"):
            CeilingFloorVent(**kwargs)  # type: ignore[arg-type]

    @pytest.mark.parametrize(
        ("param", "value"),
        [
            pytest.param("time", 10.0, id="time-float"),
            pytest.param("time", (0.0, 100.0), id="time-tuple"),
            pytest.param("fraction", 0.5, id="fraction-float"),
            pytest.param("fraction", (1.0, 0.5), id="fraction-tuple"),
        ],
    )
    def test_optional_list_params_wrong_type(self, param, value):
        """Test that optional list parameters reject non-list types when provided."""
        kwargs: dict[str, object] = {
            "id": "VENT1",
            "comps_ids": ["UPPER", "LOWER"],
            "area": 1.0,
            "open_close_criterion": "TIME",
            "time": [0.0, 100.0],
            "fraction": [1.0, 0.5],
            param: value,
        }
        with pytest.raises(TypeError, match=f"{param} must be a list"):
            CeilingFloorVent(**kwargs)  # type: ignore[arg-type]

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
            CeilingFloorVent(id="VENT1", comps_ids=comps_ids, area=1.0)

    def test_area_negative_values(self):
        """Test that negative area values are rejected."""
        with pytest.raises(ValueError, match="area must be non-negative"):
            CeilingFloorVent(id="VENT1", comps_ids=["UPPER", "LOWER"], area=-1.0)

    def test_area_warning_for_zero_area(self):
        """Test that a warning is raised for zero area."""
        with pytest.warns(
            UserWarning, match="area=0 means no flow will occur through this vent"
        ):
            CeilingFloorVent(id="VENT1", comps_ids=["UPPER", "LOWER"], area=0.0)

    @pytest.mark.parametrize(
        "invalid_type",
        [pytest.param("ROOF", id="roof"), pytest.param("", id="empty")],
    )
    def test_invalid_type(self, invalid_type: str):
        """Test that invalid type values are rejected."""
        with pytest.raises(ValueError, match="type must be 'FLOOR' or 'CEILING'"):
            CeilingFloorVent(
                id="VENT1", comps_ids=["UPPER", "LOWER"], area=1.0, type=invalid_type
            )

    @pytest.mark.parametrize(
        "invalid_shape",
        [pytest.param("CIRCLE", id="circle"), pytest.param("", id="empty")],
    )
    def test_invalid_shape(self, invalid_shape: str):
        """Test that invalid shape values are rejected."""
        with pytest.raises(ValueError, match="shape must be 'ROUND' or 'SQUARE'"):
            CeilingFloorVent(
                id="VENT1",
                comps_ids=["UPPER", "LOWER"],
                area=1.0,
                shape=invalid_shape,
            )

    @pytest.mark.parametrize(
        "invalid_width",
        [pytest.param(0.0, id="zero"), pytest.param(-1.0, id="negative")],
    )
    def test_invalid_width(self, invalid_width: float):
        """Test that non-positive width values are rejected."""
        with pytest.raises(ValueError, match="width must be positive"):
            CeilingFloorVent(
                id="VENT1",
                comps_ids=["UPPER", "LOWER"],
                area=1.0,
                width=invalid_width,
            )

    def test_invalid_offsets_length(self):
        """Test that offsets with wrong length are rejected."""
        with pytest.raises(ValueError, match="offsets must be a list of two values"):
            CeilingFloorVent(
                id="VENT1",
                comps_ids=["UPPER", "LOWER"],
                area=1.0,
                offsets=[1.0, 2.0, 3.0],
            )

    @pytest.mark.parametrize(
        ("param", "value"),
        [
            pytest.param("pre_fraction", -0.5, id="pre_fraction-negative"),
            pytest.param("post_fraction", -0.5, id="post_fraction-negative"),
            pytest.param("pre_fraction", 1.5, id="pre_fraction-above-1"),
            pytest.param("post_fraction", 1.5, id="post_fraction-above-1"),
        ],
    )
    def test_pre_post_fraction_invalid_values(self, param: str, value: float):
        """Test that invalid pre/post_fraction values (out of [0, 1]) are rejected."""
        with pytest.raises(ValueError, match=r"must be in \[0, 1\]"):
            CeilingFloorVent(
                id="VENT1",
                comps_ids=["UPPER", "LOWER"],
                area=1.0,
                open_close_criterion="TEMPERATURE",
                set_point=150.0,
                device_id="SENSOR",
                **{param: value},  # type: ignore[arg-type]
            )

    def test_fraction_invalid_values(self):
        """Test that fraction values outside [0, 1] are rejected."""
        with pytest.raises(ValueError, match=r"must be in \[0, 1\]"):
            CeilingFloorVent(
                id="VENT1",
                comps_ids=["UPPER", "LOWER"],
                area=1.0,
                open_close_criterion="TIME",
                time=[0.0, 100.0],
                fraction=[-0.5, 1.0],
            )

    def test_invalid_open_close_criterion(self):
        """Test that invalid criterion values are rejected."""
        with pytest.raises(ValueError, match="open_close_criterion must be one of"):
            CeilingFloorVent(
                id="VENT1",
                comps_ids=["UPPER", "LOWER"],
                area=1.0,
                open_close_criterion="PRESSURE",
            )

    @pytest.mark.parametrize(
        "criterion",
        [
            pytest.param("TEMPERATURE", id="temperature"),
            pytest.param("FLUX", id="flux"),
        ],
    )
    def test_criterion_requires_set_point(self, criterion: str):
        """Test that TEMPERATURE and FLUX criteria require set_point."""
        with pytest.raises(ValueError, match="set_point must be specified"):
            CeilingFloorVent(
                id="VENT1",
                comps_ids=["UPPER", "LOWER"],
                area=1.0,
                open_close_criterion=criterion,
                device_id="SENSOR",
            )

    @pytest.mark.parametrize(
        "criterion",
        [
            pytest.param("TEMPERATURE", id="temperature"),
            pytest.param("FLUX", id="flux"),
        ],
    )
    def test_criterion_requires_device_id(self, criterion: str):
        """Test that TEMPERATURE and FLUX criteria require device_id."""
        with pytest.raises(ValueError, match="device_id must be specified"):
            CeilingFloorVent(
                id="VENT1",
                comps_ids=["UPPER", "LOWER"],
                area=1.0,
                open_close_criterion=criterion,
                set_point=100.0,
            )

    def test_time_criterion_requires_time_and_fraction(self):
        """Test that TIME criterion requires both time and fraction lists."""
        with pytest.raises(ValueError, match="time and fraction must be specified"):
            CeilingFloorVent(
                id="VENT1",
                comps_ids=["UPPER", "LOWER"],
                area=1.0,
                open_close_criterion="TIME",
            )

    def test_time_criterion_mismatched_lengths(self):
        """Test that TIME criterion rejects mismatched time/fraction lengths."""
        with pytest.raises(ValueError, match="equal length"):
            CeilingFloorVent(
                id="VENT1",
                comps_ids=["UPPER", "LOWER"],
                area=1.0,
                open_close_criterion="TIME",
                time=[0.0, 100.0],
                fraction=[1.0],
            )

    def test_time_criterion_negative_time_values(self):
        """Test that TIME criterion rejects negative time values."""
        with pytest.raises(ValueError, match="non-negative"):
            CeilingFloorVent(
                id="VENT1",
                comps_ids=["UPPER", "LOWER"],
                area=1.0,
                open_close_criterion="TIME",
                time=[-10.0, 100.0],
                fraction=[1.0, 0.5],
            )

    def test_time_criterion_non_monotonic_time_values(self):
        """Test that TIME criterion rejects non-monotonically increasing time values."""
        with pytest.raises(ValueError, match="monotonically increasing"):
            CeilingFloorVent(
                id="VENT1",
                comps_ids=["UPPER", "LOWER"],
                area=1.0,
                open_close_criterion="TIME",
                time=[100.0, 50.0, 200.0],
                fraction=[1.0, 0.5, 0.0],
            )

    def test_to_input_string_basic(self):
        """Test basic input string generation."""
        vent = CeilingFloorVent(
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
        vent = CeilingFloorVent(
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
                [" T =", " F ="],
                id="temperature-full",
            ),
            pytest.param(
                "FLUX",
                50.0,
                "FLUX_SENSOR",
                1.0,
                None,
                [
                    "CRITERION = 'FLUX'",
                    "SETPOINT = 50.0",
                    "DEVC_ID = 'FLUX_SENSOR'",
                    "PRE_FRACTION = 1.0",
                ],
                [" T =", " F ="],
                id="flux-with-device",
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
        """Test input string generation with all possible options for TIME criterion."""
        vent = CeilingFloorVent(
            id="COMPLEX_VENT",
            comps_ids=["TOP_ROOM", "BOTTOM_ROOM"],
            area=3.14,
            shape="ROUND",
            width=2.0,
            offsets=[1.0, 2.0],
            open_close_criterion="TIME",
            time=[0.0, 50.0, 100.0],
            fraction=[1.0, 0.5, 0.0],
        )
        result = vent.to_input_string()
        assert result.startswith("&VENT")
        assert result.endswith("/\n")
        assert "ID = 'COMPLEX_VENT'" in result
        assert "COMP_IDS = 'TOP_ROOM', 'BOTTOM_ROOM'" in result
        assert "AREA = 3.14" in result
        assert "SHAPE = 'ROUND'" in result
        assert "CRITERION = 'TIME'" in result
        assert "T = 0.0, 50.0, 100.0" in result
        assert "F = 1.0, 0.5, 0.0" in result
        assert "OFFSETS = 1.0, 2.0" in result
        assert "None" not in result

    def test_default_offsets(self):
        """Test that default offsets are set when None is provided."""
        vent = CeilingFloorVent(
            id="VENT1", comps_ids=["UPPER", "LOWER"], area=1.0, offsets=None
        )
        assert vent.offsets == [0, 0]

    def test_repr(self):
        """Test __repr__ method."""
        vent = CeilingFloorVent(
            id="STAIR_VENT",
            comps_ids=["UPPER_FLOOR", "LOWER_FLOOR"],
            area=2.0,
            shape="SQUARE",
            width=1.4,
            offsets=[1.0, 2.0],
        )

        repr_str = repr(vent)
        assert "CeilingFloorVent(" in repr_str
        assert "id='STAIR_VENT'" in repr_str
        assert "comps_ids=['UPPER_FLOOR', 'LOWER_FLOOR']" in repr_str
        assert "area=2.0" in repr_str
        assert "shape='SQUARE'" in repr_str
        assert "width=1.4" in repr_str
        assert "offsets=[1.0, 2.0]" in repr_str

    def test_str(self):
        """Test __str__ method."""
        vent = CeilingFloorVent(
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
        vent = CeilingFloorVent(
            id="CONTROLLED_VENT",
            comps_ids=["UP", "DOWN"],
            area=1.0,
            shape="SQUARE",
            open_close_criterion="TEMPERATURE",
            set_point=200.0,
            device_id="SENSOR",
        )

        str_repr = str(vent)
        assert "criterion: TEMPERATURE" in str_repr

    def test_getitem(self) -> None:
        """Test __getitem__ method."""
        vent = CeilingFloorVent(
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
        vent = CeilingFloorVent(id="VENT1", comps_ids=["UP", "DOWN"], area=1.0)

        with pytest.raises(
            KeyError, match="Property 'invalid_key' not found in CeilingFloorVent"
        ):
            vent["invalid_key"]

    def test_setitem(self) -> None:
        """Test __setitem__ method."""
        vent = CeilingFloorVent(id="VENT1", comps_ids=["UP", "DOWN"], area=1.0)

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
        vent = CeilingFloorVent(id="VENT1", comps_ids=["UP", "DOWN"], area=1.0)

        with pytest.raises(KeyError, match="Cannot set 'invalid_key'"):
            vent["invalid_key"] = "value"


class TestCeilingFloorVentSetItemValidation:
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
        vent = make_ceiling_floor_vent(
            open_close_criterion="TIME",
            time=[0.0, 100.0],
            fraction=[1.0, 0.5],
        )
        with pytest.raises(ValueError, match="equal length"):
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
