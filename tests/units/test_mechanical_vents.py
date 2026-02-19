from __future__ import annotations

import pytest

from pycfast.mechanical_vents import MechanicalVents

"""
Tests for the MechanicalVents class.
"""


@pytest.fixture()
def make_mechanical_vent():
    """Create a MechanicalVents instance with sensible defaults."""

    def _make(**kwargs: object) -> MechanicalVents:
        defaults: dict[str, object] = {
            "id": "FAN1",
            "comps_ids": ["OUTSIDE", "ROOM1"],
            "area": [0.1, 0.1],
            "heights": [3.0, 2.8],
            "orientations": ["HORIZONTAL", "HORIZONTAL"],
            "flow": 0.5,
            "cutoffs": [100, 150],
            "offsets": [0.0, 1.0],
            "filter_time": 0.0,
            "filter_efficiency": 0.0,
        }
        defaults.update(kwargs)
        return MechanicalVents(**defaults)  # type: ignore[arg-type]

    return _make


class TestMechanicalVents:
    """Test class for MechanicalVents."""

    def test_init_basic(self):
        """Test basic initialization with minimal parameters."""
        vent = MechanicalVents(
            id="VENT_1",
            comps_ids=["ROOM1", "ROOM2"],
            area=[0.5, 0.5],
            heights=[2.0, 2.0],
            orientations=["VERTICAL", "VERTICAL"],
            offsets=[0.0, 0.0],
        )
        assert vent.id == "VENT_1"
        assert vent.comps_ids == ["ROOM1", "ROOM2"]
        assert vent.area == [0.5, 0.5]
        assert vent.heights == [2.0, 2.0]
        assert vent.orientations == ["VERTICAL", "VERTICAL"]
        assert vent.flow == 0
        assert vent.cutoffs == [200, 300]
        assert vent.offsets == [0.0, 0.0]
        assert vent.filter_time == 0
        assert vent.filter_efficiency == 0

    def test_init_with_all_parameters(self):
        """Test initialization with all parameters."""
        vent = MechanicalVents(
            id="SUPPLY_1",
            comps_ids=["OUTSIDE", "ROOM1"],
            area=[0.1, 0.1],
            heights=[3.0, 2.8],
            orientations=["HORIZONTAL", "HORIZONTAL"],
            flow=0.5,
            cutoffs=[100, 150],
            offsets=[0.0, 1.0],
            filter_time=0.0,
            filter_efficiency=0.0,
            open_close_criterion="TEMPERATURE",
            time=[0.0, 100.0, 200.0],
            fraction=[1.0, 0.5, 0.0],
            set_point=150.0,
            device_id="TEMP_SENSOR",
            pre_fraction=0.8,
            post_fraction=0.2,
        )
        assert vent.id == "SUPPLY_1"
        assert vent.comps_ids == ["OUTSIDE", "ROOM1"]
        assert vent.area == [0.1, 0.1]
        assert vent.heights == [3.0, 2.8]
        assert vent.orientations == ["HORIZONTAL", "HORIZONTAL"]
        assert vent.flow == 0.5
        assert vent.cutoffs == [100, 150]
        assert vent.offsets == [0.0, 1.0]
        assert vent.filter_time == 0.0
        assert vent.filter_efficiency == 0.0
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
            pytest.param(["ROOM1"], id="too-few"),
            pytest.param(["ROOM1", "ROOM2", "ROOM3"], id="too-many"),
        ],
    )
    def test_init_invalid_comps_ids_length(self, comps_ids: list[str]):
        """Test that initialization fails with wrong number of compartments."""
        with pytest.raises(ValueError, match="exactly 2 compartment IDs"):
            MechanicalVents(id="FAN1", comps_ids=comps_ids)

    @pytest.mark.parametrize(
        ("field", "bad_value", "match"),
        [
            pytest.param("area", [0.1], "area must have exactly 2 elements", id="area"),
            pytest.param(
                "heights", [3.0], "heights must have exactly 2 elements", id="heights"
            ),
            pytest.param(
                "orientations",
                ["HORIZONTAL"],
                "orientations must have exactly 2 elements",
                id="orientations",
            ),
            pytest.param(
                "cutoffs",
                [100.0],
                "cutoffs must have exactly 2 elements",
                id="cutoffs",
            ),
            pytest.param(
                "offsets",
                [0.0],
                "offsets must have exactly 2 elements",
                id="offsets",
            ),
        ],
    )
    def test_init_invalid_list_length(self, field: str, bad_value: list, match: str):
        """Test that initialization fails with wrong list length."""
        with pytest.raises(ValueError, match=match):
            MechanicalVents(
                id="FAN1",
                comps_ids=["OUTSIDE", "ROOM1"],
                **{field: bad_value},
            )

    @pytest.mark.parametrize(
        "cutoffs",
        [
            pytest.param([-10.0, 100.0], id="negative-first"),
            pytest.param([100.0, -10.0], id="negative-second"),
        ],
    )
    def test_init_negative_cutoffs(self, cutoffs: list[float]):
        """Test that initialization fails with negative cutoff values."""
        with pytest.raises(ValueError, match="cutoffs must be non-negative"):
            MechanicalVents(
                id="FAN1",
                comps_ids=["OUTSIDE", "ROOM1"],
                cutoffs=cutoffs,
            )

    def test_init_invalid_cutoffs_order(self):
        """Test that initialization fails when second cutoff is less than first."""
        with pytest.raises(ValueError, match="Zero flow pressure must be greater"):
            MechanicalVents(
                id="FAN1",
                comps_ids=["OUTSIDE", "ROOM1"],
                cutoffs=[150.0, 100.0],  # Second cutoff less than first
            )

    def test_to_input_string_basic(self):
        """Test basic input string generation."""
        vent = MechanicalVents(
            id="FAN1",
            comps_ids=["OUTSIDE", "ROOM1"],
            area=[0.1, 0.1],
            heights=[3.0, 2.8],
            orientations=["HORIZONTAL", "HORIZONTAL"],
            flow=0.5,
            cutoffs=[100, 150],
            offsets=[0.0, 1.0],
            filter_time=0.0,
            filter_efficiency=0.0,
        )
        result = vent.to_input_string()

        # Check basic components
        assert "&VENT TYPE = 'MECHANICAL'" in result
        assert "ID = 'FAN1'" in result
        assert "COMP_IDS = 'OUTSIDE', 'ROOM1'" in result
        assert "AREAS = 0.1, 0.1" in result
        assert "HEIGHTS = 3.0, 2.8" in result
        assert "ORIENTATIONS = 'HORIZONTAL', 'HORIZONTAL'" in result
        assert "FLOW = 0.5" in result
        assert "CUTOFFS = 100, 150" in result
        assert "OFFSETS = 0.0, 1.0" in result
        assert "FILTER_TIME = 0.0" in result
        assert "FILTER_EFFICIENCY = 0.0" in result
        assert result.endswith("/\n")

    def test_to_input_string_with_criterion(self, make_mechanical_vent):
        """Test input string generation with open/close criterion."""
        vent = make_mechanical_vent(
            open_close_criterion="TEMPERATURE",
            set_point=150.0,
            device_id="TEMP_SENSOR",
            pre_fraction=0.8,
            post_fraction=0.2,
        )
        result = vent.to_input_string()

        assert "CRITERION = 'TEMPERATURE'" in result
        assert "SETPOINT = 150.0" in result
        assert "DEVC_ID = 'TEMP_SENSOR'" in result
        assert "PRE_FRACTION = 0.8" in result
        assert "POST_FRACTION = 0.2" in result

    def test_to_input_string_with_time_fraction(self, make_mechanical_vent):
        """Test input string generation with time and fraction data."""
        vent = make_mechanical_vent(
            time=[0.0, 100.0, 200.0],
            fraction=[1.0, 0.5, 0.0],
        )
        result = vent.to_input_string()

        assert "T = 0.0, 100.0, 200.0" in result
        assert "F = 1.0, 0.5, 0.0" in result

    def test_to_input_string_exhaust_fan(self):
        """Test input string generation for exhaust fan (negative flow)."""
        vent = MechanicalVents(
            id="EXHAUST1",
            comps_ids=["ROOM1", "OUTSIDE"],
            area=[0.05, 0.05],
            heights=[2.5, 3.0],
            orientations=["VERTICAL", "VERTICAL"],
            flow=-0.3,  # Negative for exhaust
            cutoffs=[200, 300],
            offsets=[1.0, 0.0],
            filter_time=0,
            filter_efficiency=0,
        )
        result = vent.to_input_string()

        assert "FLOW = -0.3" in result
        assert "COMP_IDS = 'ROOM1', 'OUTSIDE'" in result

    def test_to_input_string_with_filtration(self):
        """Test input string generation with filtration parameters."""
        vent = MechanicalVents(
            id="FILTERED_SUPPLY",
            comps_ids=["OUTSIDE", "ROOM1"],
            area=[0.2, 0.2],
            heights=[3.0, 2.8],
            orientations=["HORIZONTAL", "HORIZONTAL"],
            flow=1.0,
            cutoffs=[100, 150],
            offsets=[0.0, 1.0],
            filter_time=300.0,  # 5 minute time constant
            filter_efficiency=0.95,  # 95% efficient
        )
        result = vent.to_input_string()

        assert "FILTER_TIME = 300.0" in result
        assert "FILTER_EFFICIENCY = 0.95" in result

    def test_to_input_string_criterion_without_optional_params(
        self, make_mechanical_vent
    ):
        """Test input string generation with criterion but no optional parameters."""
        vent = make_mechanical_vent(open_close_criterion="FLUX")
        result = vent.to_input_string()

        assert "CRITERION = 'FLUX'" in result
        assert "SETPOINT" not in result
        assert "DEVC_ID" not in result
        assert "PRE_FRACTION = 1" in result
        assert "POST_FRACTION = 1" in result

    def test_to_input_string_multiple_orientations(self):
        """Test input string generation with different orientations."""
        vent = MechanicalVents(
            id="MIXED_VENT",
            comps_ids=["ROOM1", "ROOM2"],
            area=[0.1, 0.2],
            heights=[2.5, 3.0],
            orientations=["HORIZONTAL", "VERTICAL"],
            flow=0.4,
            cutoffs=[150, 200],
            offsets=[0.5, 1.5],
            filter_time=0.0,
            filter_efficiency=0.0,
        )
        result = vent.to_input_string()

        assert "ORIENTATIONS = 'HORIZONTAL', 'VERTICAL'" in result
        assert "AREAS = 0.1, 0.2" in result
        assert "HEIGHTS = 2.5, 3.0" in result

    def test_to_input_string_none_filter_params(self):
        """Test input string generation with None filter parameters."""
        vent = MechanicalVents(
            id="FAN1",
            comps_ids=["OUTSIDE", "ROOM1"],
            area=[0.1, 0.1],
            heights=[3.0, 2.8],
            orientations=["HORIZONTAL", "HORIZONTAL"],
            flow=0.5,
            cutoffs=[100, 150],
            offsets=[0.0, 1.0],
            filter_time=0,
            filter_efficiency=0,
        )
        result = vent.to_input_string()

        assert "FILTER_TIME = 0" in result
        assert "FILTER_EFFICIENCY = 0" in result

    def test_default_values_initialization(self):
        """Test that default values are properly set during initialization."""
        vent = MechanicalVents(
            id="FAN1",
            comps_ids=["OUTSIDE", "ROOM1"],
            offsets=[0.0, 1.0],  # Required parameter
        )

        # Check defaults are applied
        assert vent.area == [0, 0]
        assert vent.heights == [0, 0]
        assert vent.orientations == ["VERTICAL", "VERTICAL"]
        assert vent.cutoffs == [200, 300]
        assert vent.flow == 0

    def test_repr(self) -> None:
        """Test __repr__ method."""
        vent = MechanicalVents(
            id="SUPPLY_FAN",
            comps_ids=["OUTSIDE", "LOBBY"],
            area=[0.2, 0.2],
            heights=[3.5, 2.5],
            orientations=["HORIZONTAL", "HORIZONTAL"],
            flow=1.2,
            cutoffs=[120, 180],
            offsets=[0.5, 1.0],
        )

        repr_str = repr(vent)
        assert "MechanicalVents(" in repr_str
        assert "id='SUPPLY_FAN'" in repr_str
        assert "comps_ids=['OUTSIDE', 'LOBBY']" in repr_str
        assert "flow=1.2" in repr_str
        assert "area=[0.2, 0.2]" in repr_str
        assert "heights=[3.5, 2.5]" in repr_str

    def test_str(self) -> None:
        """Test __str__ method."""
        vent = MechanicalVents(
            id="EXHAUST_01",
            comps_ids=["KITCHEN", "OUTSIDE"],
            area=[0.15, 0.15],
            heights=[2.8, 3.0],
            orientations=["VERTICAL", "VERTICAL"],
            flow=-0.8,  # Negative for exhaust
            cutoffs=[150, 200],
            offsets=[1.5, 0.0],
        )

        str_repr = str(vent)
        assert "Mechanical Vent 'EXHAUST_01'" in str_repr
        assert "KITCHEN -> OUTSIDE" in str_repr
        assert "flow: -0.8 m³/s" in str_repr

    def test_str_with_supply_flow(self) -> None:
        """Test __str__ method with positive supply flow."""
        vent = MechanicalVents(
            id="SUPPLY_02",
            comps_ids=["OUTSIDE", "BEDROOM"],
            area=[0.1, 0.1],
            heights=[3.0, 2.5],
            flow=0.6,  # Positive for supply
            offsets=[0.0, 2.0],
        )

        str_repr = str(vent)
        assert "Mechanical Vent 'SUPPLY_02'" in str_repr
        assert "OUTSIDE -> BEDROOM" in str_repr
        assert "flow: 0.6 m³/s" in str_repr

    def test_getitem(self) -> None:
        """Test __getitem__ method."""
        vent = MechanicalVents(
            id="TEST_VENT",
            comps_ids=["ROOM_A", "ROOM_B"],
            area=[0.25, 0.25],
            heights=[2.2, 2.2],
            orientations=["HORIZONTAL", "HORIZONTAL"],
            flow=0.4,
            cutoffs=[100, 150],
            offsets=[0.8, 1.2],
            filter_time=10.0,
            filter_efficiency=0.85,
            open_close_criterion="TEMPERATURE",
            time=[0.0, 300.0],
            fraction=[1.0, 0.0],
            set_point=80.0,
        )

        assert vent["id"] == "TEST_VENT"
        assert vent["comps_ids"] == ["ROOM_A", "ROOM_B"]
        assert vent["area"] == [0.25, 0.25]
        assert vent["heights"] == [2.2, 2.2]
        assert vent["orientations"] == ["HORIZONTAL", "HORIZONTAL"]
        assert vent["flow"] == 0.4
        assert vent["cutoffs"] == [100, 150]
        assert vent["offsets"] == [0.8, 1.2]
        assert vent["filter_time"] == 10.0
        assert vent["filter_efficiency"] == 0.85
        assert vent["open_close_criterion"] == "TEMPERATURE"
        assert vent["time"] == [0.0, 300.0]
        assert vent["fraction"] == [1.0, 0.0]
        assert vent["set_point"] == 80.0

    def test_getitem_with_none_values(self) -> None:
        """Test __getitem__ method with None values."""
        vent = MechanicalVents(
            id="MINIMAL_VENT", comps_ids=["ROOM1", "ROOM2"], offsets=[0.0, 0.0]
        )

        assert vent["filter_time"] == 0
        assert vent["filter_efficiency"] == 0
        assert vent["open_close_criterion"] is None
        assert vent["time"] is None
        assert vent["fraction"] is None
        assert vent["set_point"] is None

    def test_getitem_invalid_key(self) -> None:
        """Test __getitem__ method with invalid key."""
        vent = MechanicalVents(
            id="VENT1", comps_ids=["ROOM1", "ROOM2"], offsets=[0.0, 0.0]
        )

        with pytest.raises(
            KeyError, match="Property 'invalid_property' not found in MechanicalVents"
        ):
            vent["invalid_property"]

    def test_setitem(self) -> None:
        """Test __setitem__ method."""
        vent = MechanicalVents(
            id="MODIFIABLE_VENT",
            comps_ids=["HALL", "OFFICE"],
            area=[0.12, 0.12],
            heights=[2.5, 2.5],
            flow=0.3,
            offsets=[0.0, 1.0],
        )

        # Modify basic properties
        vent["id"] = "NEW_VENT_ID"
        vent["flow"] = 0.75
        vent["area"] = [0.2, 0.2]
        vent["heights"] = [3.0, 3.0]
        vent["orientations"] = ["VERTICAL", "VERTICAL"]
        vent["cutoffs"] = [80, 120]
        vent["offsets"] = [1.5, 2.0]

        assert vent.id == "NEW_VENT_ID"
        assert vent.flow == 0.75
        assert vent.area == [0.2, 0.2]
        assert vent.heights == [3.0, 3.0]
        assert vent.orientations == ["VERTICAL", "VERTICAL"]
        assert vent.cutoffs == [80, 120]
        assert vent.offsets == [1.5, 2.0]

    def test_setitem_compartment_lists(self) -> None:
        """Test __setitem__ method with compartment lists."""
        vent = MechanicalVents(
            id="LIST_VENT", comps_ids=["ROOM1", "ROOM2"], offsets=[0.0, 0.0]
        )

        # Modify compartment connection
        vent["comps_ids"] = ["OUTSIDE", "MEETING_ROOM"]

        assert vent.comps_ids == ["OUTSIDE", "MEETING_ROOM"]

    def test_setitem_invalid_key(self) -> None:
        """Test __setitem__ method with invalid key."""
        vent = MechanicalVents(
            id="VENT1", comps_ids=["ROOM1", "ROOM2"], offsets=[0.0, 0.0]
        )

        with pytest.raises(
            KeyError,
            match="Cannot set 'nonexistent_attr'. Property does not exist in MechanicalVents",
        ):
            vent["nonexistent_attr"] = "some_value"

    def test_repr_html(self) -> None:
        """Test _repr_html_ method."""
        vent = MechanicalVents(
            id="SUPPLY_FAN",
            comps_ids=["OUTSIDE", "LOBBY"],
            area=[0.2, 0.2],
            heights=[3.5, 2.5],
            orientations=["HORIZONTAL", "HORIZONTAL"],
            flow=1.2,
            cutoffs=[120, 180],
            offsets=[0.5, 1.0],
        )

        html_str = vent._repr_html_()

        # Check that it returns valid HTML string
        assert isinstance(html_str, str)
        assert len(html_str) > 0

        # Check for expected HTML structure
        assert '<div class="pycfast-card' in html_str
        assert "Mechanical Vent: SUPPLY_FAN" in html_str
        assert "OUTSIDE → LOBBY" in html_str

        # Check vent properties
        assert "1.2 m³/s" in html_str
        assert "3.5" in html_str  # height
        assert "0.2" in html_str  # area


class TestMechanicalVentsSetItemValidation:
    """Test validation in __setitem__ to ensure data integrity."""

    @pytest.mark.parametrize(
        ("key", "value", "match"),
        [
            pytest.param(
                "comps_ids",
                ["ONLY_ONE"],
                "comps_ids must contain exactly 2",
                id="comps_ids",
            ),
            pytest.param(
                "area",
                [0.1],
                "area must have exactly 2 elements",
                id="area",
            ),
            pytest.param(
                "heights",
                [1.0, 2.0, 3.0],
                "heights must have exactly 2 elements",
                id="heights",
            ),
            pytest.param(
                "orientations",
                ["VERTICAL"],
                "orientations must have exactly 2 elements",
                id="orientations",
            ),
            pytest.param(
                "cutoffs",
                [100],
                "cutoffs must have exactly 2 elements",
                id="cutoffs",
            ),
            pytest.param(
                "offsets",
                [0.0, 0.0, 0.0],
                "offsets must have exactly 2 elements",
                id="offsets",
            ),
        ],
    )
    def test_setitem_invalid_list_length(self, make_mechanical_vent, key, value, match):
        """Test that __setitem__ rejects lists with wrong length."""
        vent = make_mechanical_vent()
        with pytest.raises(ValueError, match=match):
            vent[key] = value

    @pytest.mark.parametrize(
        "invalid_cutoffs",
        [
            pytest.param([-1, 300], id="negative-first"),
            pytest.param([200, -1], id="negative-second"),
        ],
    )
    def test_setitem_negative_cutoffs(self, make_mechanical_vent, invalid_cutoffs):
        """Test that __setitem__ rejects negative cutoffs."""
        vent = make_mechanical_vent()
        with pytest.raises(ValueError, match="cutoffs must be non-negative"):
            vent["cutoffs"] = invalid_cutoffs

    def test_setitem_cutoffs_wrong_order(self, make_mechanical_vent):
        """Test that __setitem__ rejects cutoffs where second < first."""
        vent = make_mechanical_vent()
        with pytest.raises(ValueError, match="Zero flow pressure must be greater"):
            vent["cutoffs"] = [300, 100]

    @pytest.mark.parametrize(
        ("key", "value"),
        [
            pytest.param("time", [0.0, 100.0, 200.0], id="time-longer-than-fraction"),
            pytest.param("fraction", [1.0], id="fraction-shorter-than-time"),
        ],
    )
    def test_setitem_mismatched_time_fraction(self, make_mechanical_vent, key, value):
        """Test that __setitem__ rejects mismatched time/fraction list lengths."""
        vent = make_mechanical_vent(time=[0.0, 100.0], fraction=[1.0, 0.5])
        with pytest.raises(
            ValueError, match="Time and fraction lists must be of equal length"
        ):
            vent[key] = value

    def test_setitem_valid_flow_change(self, make_mechanical_vent):
        """Test that __setitem__ accepts valid property changes."""
        vent = make_mechanical_vent()
        vent["flow"] = 2.5
        assert vent.flow == 2.5

    def test_setitem_invalid_does_not_mutate_state(self, make_mechanical_vent):
        """Test that a failed __setitem__ rolls back to the previous value."""
        vent = make_mechanical_vent(cutoffs=[100, 200])
        before = vent.cutoffs.copy()

        with pytest.raises(ValueError):
            vent["cutoffs"] = [-1, 300]

        assert vent.cutoffs == before
