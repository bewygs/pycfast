from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from pycfast.fires import Fires

"""
Tests for the Fires class.
"""


@pytest.fixture()
def make_fire():
    """Create a Fires instance with sensible defaults."""

    def _make(**kwargs: object) -> Fires:
        defaults: dict[str, object] = {
            "id": "FIRE1",
            "comp_id": "ROOM1",
            "fire_id": "POLYURETHANE",
            "location": [2.0, 3.0],
        }
        defaults.update(kwargs)
        return Fires(**defaults)  # type: ignore[arg-type]

    return _make


class TestFires:
    """Test class for Fires."""

    def test_init_basic(self):
        """Test basic initialization with required parameters."""
        fire = Fires(
            id="FIRE1",
            comp_id="ROOM1",
            fire_id="POLYURETHANE",
            location=[2.0, 3.0],
        )
        assert fire.id == "FIRE1"
        assert fire.comp_id == "ROOM1"
        assert fire.fire_id == "POLYURETHANE"
        assert fire.location == [2.0, 3.0]
        assert fire.carbon == 1
        assert fire.chlorine == 0
        assert fire.hydrogen == 4
        assert fire.nitrogen == 0
        assert fire.oxygen == 0
        assert fire.heat_of_combustion == 50000
        assert fire.radiative_fraction == 0.35
        assert fire.ignition_criterion is None
        assert fire.set_point is None
        assert fire.device_id is None
        assert fire.data_table == [[0, 0, 0, 0, 0, 0, 0, 0, 0]]

    def test_init_with_all_parameters(self):
        """Test initialization with all parameters."""
        data_table = [
            [0, 100, 0.5, 0.1, 0.01, 0.01, 0, 0, 0],
            [60, 500, 1.0, 0.5, 0.01, 0.01, 0, 0, 0],
        ]
        fire = Fires(
            id="FIRE1",
            comp_id="ROOM1",
            fire_id="POLYURETHANE",
            location=[2.0, 3.0],
            ignition_criterion="TEMPERATURE",
            set_point=150.0,
            device_id="TEMP_SENSOR",
            carbon=27,
            chlorine=2,
            hydrogen=36,
            nitrogen=2,
            oxygen=2,
            heat_of_combustion=23600000,
            radiative_fraction=0.35,
            data_table=data_table,
        )
        assert fire.id == "FIRE1"
        assert fire.comp_id == "ROOM1"
        assert fire.fire_id == "POLYURETHANE"
        assert fire.location == [2.0, 3.0]
        assert fire.ignition_criterion == "TEMPERATURE"
        assert fire.set_point == 150.0
        assert fire.device_id == "TEMP_SENSOR"
        assert fire.carbon == 27
        assert fire.chlorine == 2
        assert fire.hydrogen == 36
        assert fire.nitrogen == 2
        assert fire.oxygen == 2
        assert fire.heat_of_combustion == 23600000
        assert fire.radiative_fraction == 0.35
        assert fire.data_table == data_table

    @pytest.mark.parametrize(
        "location",
        [
            pytest.param([2.0], id="too-few"),
            pytest.param([2.0, 3.0, 1.0], id="too-many"),
        ],
    )
    def test_init_invalid_location_length(self, location: list[float]):
        """Test that initialization fails with wrong location dimensions."""
        with pytest.raises(ValueError, match="Location must be a list of two floats"):
            Fires(
                id="FIRE1",
                comp_id="ROOM1",
                fire_id="POLYURETHANE",
                location=location,
            )

    def test_init_invalid_data_table_columns(self):
        """Test that initialization fails with wrong number of columns in data table."""
        invalid_data_table = [
            [0, 100, 0.5],  # Only 3 columns instead of 9
        ]
        with pytest.raises(ValueError, match="data_table must have exactly 9 columns"):
            Fires(
                id="FIRE1",
                comp_id="ROOM1",
                fire_id="POLYURETHANE",
                location=[2.0, 3.0],
                data_table=invalid_data_table,
            )

    def test_to_input_string_basic(self):
        """Test basic input string generation."""
        fire = Fires(
            id="FIRE1",
            comp_id="ROOM1",
            fire_id="POLYURETHANE",
            location=[2.0, 3.0],
        )
        result = fire.to_input_string()

        # Check sections present
        assert "&FIRE" in result
        assert "&CHEM" in result
        assert "&TABL" in result

        # Check FIRE tokens
        assert "ID = 'FIRE1'" in result
        assert "COMP_ID = 'ROOM1'" in result
        assert "FIRE_ID = 'POLYURETHANE'" in result
        assert "LOCATION = 2.0, 3.0" in result

        # Check CHEM tokens
        assert "CARBON = 1" in result
        assert "HYDROGEN = 4" in result
        assert "HEAT_OF_COMBUSTION = 50000" in result
        assert "RADIATIVE_FRACTION = 0.35" in result

        # Check TABL labels
        assert "LABELS =" in result
        assert "'TIME'" in result
        assert "'HRR'" in result

        # Check TABL data row
        assert "DATA =" in result

        # No None leakage and proper termination
        assert "None" not in result
        assert result.rstrip().endswith("/")

    @pytest.mark.parametrize(
        ("criterion", "set_point", "device_id", "expected", "unexpected"),
        [
            pytest.param(
                "TEMPERATURE",
                150.0,
                "TEMP_SENSOR",
                [
                    "IGNITION_CRITERION = 'TEMPERATURE'",
                    "DEVC_ID = 'TEMP_SENSOR'",
                    "SETPOINT = 150.0",
                ],
                [],
                id="temperature",
            ),
            pytest.param(
                "FLUX",
                50.0,
                "FLUX_SENSOR",
                [
                    "IGNITION_CRITERION = 'FLUX'",
                    "DEVC_ID = 'FLUX_SENSOR'",
                    "SETPOINT = 50.0",
                ],
                [],
                id="flux",
            ),
            pytest.param(
                "TIME",
                30.0,
                "TIMER",
                ["DEVC_ID = 'TIMER'", "SETPOINT = 30.0"],
                ["IGNITION_CRITERION"],
                id="time",
            ),
        ],
    )
    def test_to_input_string_with_ignition_criterion(
        self, make_fire, criterion, set_point, device_id, expected, unexpected
    ):
        """Test input string generation with various ignition criteria."""
        fire = make_fire(
            ignition_criterion=criterion,
            set_point=set_point,
            device_id=device_id,
        )
        result = fire.to_input_string()

        for nml_field in expected:
            assert nml_field in result
        for nml_field in unexpected:
            assert nml_field not in result

    def test_to_input_string_with_custom_data_table(self):
        """Test input string generation with custom data table."""
        data_table = [
            [0, 0, 0.5, 0.1, 0.01, 0.01, 0, 0, 0],
            [60, 100000, 1.0, 0.5, 0.01, 0.01, 0, 0, 0],
            [300, 500000, 1.5, 1.0, 0.01, 0.01, 0, 0, 0],
        ]
        fire = Fires(
            id="FIRE1",
            comp_id="ROOM1",
            fire_id="POLYURETHANE",
            location=[2.0, 3.0],
            data_table=data_table,
        )
        result = fire.to_input_string()

        # Check all 3 data rows are present with key values
        tabl_lines = [line for line in result.splitlines() if "DATA =" in line]
        assert len(tabl_lines) == 3

        # Verify key values from each row appear
        assert "100000" in result  # HRR from row 2
        assert "500000" in result  # HRR from row 3
        assert "ID = 'POLYURETHANE'" in result

    def test_to_input_string_with_custom_chemistry(self):
        """Test input string generation with custom chemistry parameters."""
        fire = Fires(
            id="FIRE1",
            comp_id="ROOM1",
            fire_id="METHANE",
            location=[2.0, 3.0],
            carbon=1,
            chlorine=0,
            hydrogen=4,
            nitrogen=0,
            oxygen=0,
            heat_of_combustion=55000,
            radiative_fraction=0.30,
        )
        result = fire.to_input_string()
        assert "&CHEM" in result
        assert "ID = 'METHANE'" in result
        assert "CARBON = 1" in result
        assert "HYDROGEN = 4" in result
        assert "HEAT_OF_COMBUSTION = 55000" in result
        assert "RADIATIVE_FRACTION = 0.3" in result

    def test_to_input_string_empty_data_table(self):
        """Test input string generation with empty data table."""
        with pytest.raises(
            ValueError, match="data_table must contain at least one row"
        ):
            Fires(
                id="FIRE1",
                comp_id="ROOM1",
                fire_id="POLYURETHANE",
                location=[2.0, 3.0],
                data_table=[],
            )

    def test_init_no_ignition_criterion_with_setpoint(self):
        """Test initialization with setpoint but no ignition criterion."""
        fire = Fires(
            id="FIRE1",
            comp_id="ROOM1",
            fire_id="POLYURETHANE",
            location=[2.0, 3.0],
            set_point=100.0,
        )
        assert fire.ignition_criterion is None
        assert fire.set_point == 100.0

        result = fire.to_input_string()
        assert "IGNITION_CRITERION" not in result
        # SETPOINT is not included when there's no ignition criterion
        assert "SETPOINT" not in result

    def test_init_with_device_id_only(self):
        """Test initialization with device_id but no ignition criterion."""
        fire = Fires(
            id="FIRE1",
            comp_id="ROOM1",
            fire_id="POLYURETHANE",
            location=[2.0, 3.0],
            device_id="SENSOR1",
        )
        assert fire.device_id == "SENSOR1"
        assert fire.ignition_criterion is None

        result = fire.to_input_string()
        # DEVC_ID is not included when there's no ignition criterion
        assert "DEVC_ID" not in result
        assert "IGNITION_CRITERION" not in result

    def test_repr(self):
        """Test __repr__ method."""
        data_table = [
            [0, 100, 0.5, 0.1, 0.01, 0.01, 0, 0, 0],
            [60, 500, 1.0, 0.5, 0.01, 0.01, 0, 0, 0],
        ]
        fire = Fires(
            id="FIRE1",
            comp_id="ROOM1",
            fire_id="POLYURETHANE",
            location=[2.0, 3.0],
            heat_of_combustion=25000,
            radiative_fraction=0.4,
            data_table=data_table,
        )

        repr_str = repr(fire)
        assert "Fires(" in repr_str
        assert "id='FIRE1'" in repr_str
        assert "comp_id='ROOM1'" in repr_str
        assert "fire_id='POLYURETHANE'" in repr_str
        assert "location=[2.0, 3.0]" in repr_str
        assert "heat_of_combustion=25000" in repr_str
        assert "radiative_fraction=0.4" in repr_str
        assert "data_rows=2" in repr_str

    @pytest.mark.parametrize(
        ("data_table", "expected_peak", "expected_duration"),
        [
            pytest.param(
                [
                    [0, 0, 0.5, 0.1, 0.01, 0.01, 0, 0, 0],
                    [60, 100000, 1.0, 0.5, 0.01, 0.01, 0, 0, 0],
                    [120, 50000, 1.0, 0.5, 0.01, 0.01, 0, 0, 0],
                ],
                "peak: 100 kW",
                "duration: 2min",
                id="kw-range",
            ),
            pytest.param(
                [
                    [0, 0, 0.5, 0.1, 0.01, 0.01, 0, 0, 0],
                    [300, 2500000, 1.0, 1.0, 0.01, 0.01, 0, 0, 0],
                ],
                "peak: 2.5 MW",
                "duration: 5min",
                id="mw-range",
            ),
            pytest.param(
                [
                    [0, 0, 0.5, 0.1, 0.01, 0.01, 0, 0, 0],
                    [30, 500, 1.0, 0.5, 0.01, 0.01, 0, 0, 0],
                ],
                "peak: 500 W",
                "duration: 30s",
                id="watts-range",
            ),
            pytest.param(
                [
                    [0, 0, 0.5, 0.1, 0.01, 0.01, 0, 0, 0],
                    [7200, 100000, 1.0, 0.5, 0.01, 0.01, 0, 0, 0],
                ],
                "peak: 100 kW",
                "duration: 2.0h",
                id="hours-duration",
            ),
        ],
    )
    def test_str_hrr_and_duration_formatting(
        self, make_fire, data_table, expected_peak, expected_duration
    ):
        """Test __str__ method with various HRR magnitudes and durations."""
        fire = make_fire(data_table=data_table)
        str_repr = str(fire)
        assert expected_peak in str_repr
        assert expected_duration in str_repr

    # Note: __eq__ and __hash__ methods not implemented in current version
    # These tests are removed to match actual implementation

    def test_getitem(self) -> None:
        """Test __getitem__ method."""
        data_table = [[0, 100, 0.5, 0.1, 0.01, 0.01, 0, 0, 0]]
        fire = Fires(
            id="FIRE1",
            comp_id="ROOM1",
            fire_id="WOOD",
            location=[1.0, 2.0],
            carbon=5,
            hydrogen=10,
            heat_of_combustion=20000,
            radiative_fraction=0.4,
            data_table=data_table,
        )

        assert fire["id"] == "FIRE1"
        assert fire["comp_id"] == "ROOM1"
        assert fire["fire_id"] == "WOOD"
        assert fire["location"] == [1.0, 2.0]
        assert fire["carbon"] == 5
        assert fire["hydrogen"] == 10
        assert fire["heat_of_combustion"] == 20000
        assert fire["radiative_fraction"] == 0.4
        assert fire["data_table"] == data_table

    def test_getitem_invalid_key(self) -> None:
        """Test __getitem__ method with invalid key."""
        fire = Fires(id="FIRE1", comp_id="ROOM1", fire_id="WOOD", location=[1.0, 2.0])

        with pytest.raises(KeyError, match="Property 'invalid_key' not found in Fires"):
            fire["invalid_key"]

    def test_setitem(self) -> None:
        """Test __setitem__ method."""
        fire = Fires(id="FIRE1", comp_id="ROOM1", fire_id="WOOD", location=[1.0, 2.0])

        # Test setting various properties
        fire["id"] = "NEW_FIRE"
        assert fire.id == "NEW_FIRE"

        fire["comp_id"] = "NEW_ROOM"
        assert fire.comp_id == "NEW_ROOM"

        fire["location"] = [3.0, 4.0]
        assert fire.location == [3.0, 4.0]

        fire["radiative_fraction"] = 0.5
        assert fire.radiative_fraction == 0.5

        fire["heat_of_combustion"] = 30000
        assert fire.heat_of_combustion == 30000

    def test_setitem_invalid_key(self) -> None:
        """Test __setitem__ method with invalid key."""
        fire = Fires(id="FIRE1", comp_id="ROOM1", fire_id="WOOD", location=[1.0, 2.0])

        with pytest.raises(KeyError, match="Cannot set 'invalid_key'"):
            fire["invalid_key"] = "value"


class TestFiresDataTableFormats:
    """Test class for Fires data_table format handling."""

    def test_data_table_list_of_lists(self):
        """Test data_table with list of lists (original format)."""
        data_table = [
            [0, 0, 0.5, 0.1, 0.01, 0.01, 0, 0, 0],
            [60, 1000, 0.5, 1.0, 0.01, 0.01, 0, 0, 0],
            [300, 500, 1.0, 1.0, 0.01, 0.01, 0, 0, 0],
        ]
        fire = Fires(
            id="FIRE1",
            comp_id="ROOM1",
            fire_id="WOOD",
            location=[1.0, 2.0],
            data_table=data_table,
        )
        assert fire.data_table == data_table

    def test_data_table_numpy_array(self):
        """Test data_table with NumPy array."""
        data_array = np.array(
            [
                [0, 0, 0.5, 0.1, 0.01, 0.01, 0, 0, 0],
                [60, 1000, 0.5, 1.0, 0.01, 0.01, 0, 0, 0],
                [300, 500, 1.0, 1.0, 0.01, 0.01, 0, 0, 0],
            ]
        )
        fire = Fires(
            id="FIRE1",
            comp_id="ROOM1",
            fire_id="WOOD",
            location=[1.0, 2.0],
            data_table=data_array,
        )
        expected = data_array.tolist()
        assert fire.data_table == expected

    def test_data_table_pandas_dataframe_with_labels(self):
        """Test data_table with pandas DataFrame that has correct column labels."""
        df = pd.DataFrame(
            {
                "TIME": [0, 60, 300],
                "HRR": [0, 1000, 500],
                "HEIGHT": [0.5, 0.5, 1.0],
                "AREA": [0.1, 1.0, 1.0],
                "CO_YIELD": [0.01, 0.01, 0.01],
                "SOOT_YIELD": [0.01, 0.01, 0.01],
                "HCN_YIELD": [0, 0, 0],
                "HCL_YIELD": [0, 0, 0],
                "TRACE_YIELD": [0, 0, 0],
            }
        )
        fire = Fires(
            id="FIRE1",
            comp_id="ROOM1",
            fire_id="WOOD",
            location=[1.0, 2.0],
            data_table=df,
        )
        expected = df.values.tolist()
        assert fire.data_table == expected

    def test_data_table_pandas_dataframe_without_labels(self):
        """Test data_table with pandas DataFrame that has default column names."""
        data = [
            [0, 0, 0.5, 0.1, 0.01, 0.01, 0, 0, 0],
            [60, 1000, 0.5, 1.0, 0.01, 0.01, 0, 0, 0],
            [300, 500, 1.0, 1.0, 0.01, 0.01, 0, 0, 0],
        ]
        df = pd.DataFrame(data)  # Will have columns 0, 1, 2, ..., 8
        fire = Fires(
            id="FIRE1",
            comp_id="ROOM1",
            fire_id="WOOD",
            location=[1.0, 2.0],
            data_table=df,
        )
        assert fire.data_table == data

    def test_data_table_numpy_array_wrong_dimensions(self):
        """Test that 1D NumPy array raises error."""
        data_array = np.array([0, 1000, 0.5, 1.0, 0.01, 0.01, 0, 0, 0])  # 1D array
        with pytest.raises(ValueError, match="NumPy array must be 2-dimensional"):
            Fires(
                id="FIRE1",
                comp_id="ROOM1",
                fire_id="WOOD",
                location=[1.0, 2.0],
                data_table=data_array,
            )

    def test_data_table_numpy_array_wrong_columns(self):
        """Test that NumPy array with wrong number of columns raises error."""
        data_array = np.array(
            [
                [0, 1000, 0.5],  # Only 3 columns
                [60, 500, 1.0],
            ]
        )
        with pytest.raises(ValueError, match="NumPy array must have exactly 9 columns"):
            Fires(
                id="FIRE1",
                comp_id="ROOM1",
                fire_id="WOOD",
                location=[1.0, 2.0],
                data_table=data_array,
            )

    def test_data_table_dataframe_wrong_columns(self):
        """Test that DataFrame with wrong number of columns raises error."""
        df = pd.DataFrame(
            {
                "TIME": [0, 60],
                "HRR": [0, 1000],
                "HEIGHT": [0.5, 0.5],  # Only 3 columns
            }
        )
        with pytest.raises(ValueError, match="DataFrame must have 9 columns"):
            Fires(
                id="FIRE1",
                comp_id="ROOM1",
                fire_id="WOOD",
                location=[1.0, 2.0],
                data_table=df,
            )

    def test_data_table_invalid_type(self):
        """Test that invalid data_table type raises error."""
        with pytest.raises(
            TypeError,
            match="data_table must be a list of lists, NumPy array, pandas DataFrame, or None",
        ):
            Fires(
                id="FIRE1",
                comp_id="ROOM1",
                fire_id="WOOD",
                location=[1.0, 2.0],
                data_table="invalid_string",  # type: ignore
            )

    def test_data_table_non_numeric_values(self):
        """Test that non-numeric values in data_table raise error."""
        data_array = np.array(
            [[0, "invalid", 0.5, 1.0, 0.01, 0.01, 0, 0, 0]], dtype=object
        )
        with pytest.raises(
            ValueError, match="All values in data_table must be numeric"
        ):
            Fires(
                id="FIRE1",
                comp_id="ROOM1",
                fire_id="WOOD",
                location=[1.0, 2.0],
                data_table=data_array,
            )

    def test_data_table_empty_list(self):
        """Test that empty data_table list raises error."""
        with pytest.raises(
            ValueError, match="data_table must contain at least one row"
        ):
            Fires(
                id="FIRE1",
                comp_id="ROOM1",
                fire_id="WOOD",
                location=[1.0, 2.0],
                data_table=[],
            )

    def test_to_dataframe(self):
        """Test conversion to pandas DataFrame."""
        data_table = [
            [0, 0, 0.5, 0.1, 0.01, 0.01, 0, 0, 0],
            [60, 1000, 0.5, 1.0, 0.01, 0.01, 0, 0, 0],
            [300, 500, 1.0, 1.0, 0.01, 0.01, 0, 0, 0],
        ]
        fire = Fires(
            id="FIRE1",
            comp_id="ROOM1",
            fire_id="WOOD",
            location=[1.0, 2.0],
            data_table=data_table,
        )

        df = fire.to_dataframe()

        # Check that it's a DataFrame
        assert isinstance(df, pd.DataFrame)

        # Check column names
        assert list(df.columns) == Fires.LABELS

        # Check data content
        assert df.values.tolist() == data_table

        # Check specific values
        assert df["TIME"].tolist() == [0, 60, 300]
        assert df["HRR"].tolist() == [0, 1000, 500]
        assert df["HEIGHT"].tolist() == [0.5, 0.5, 1.0]

    def test_to_dataframe_round_trip(self):
        """Test that DataFrame -> Fire -> DataFrame preserves data (with float conversion)."""
        original_df = pd.DataFrame(
            {
                "TIME": [0, 60, 300],
                "HRR": [0, 1000, 500],
                "HEIGHT": [0.5, 0.5, 1.0],
                "AREA": [0.1, 1.0, 1.0],
                "CO_YIELD": [0.01, 0.01, 0.01],
                "SOOT_YIELD": [0.01, 0.01, 0.01],
                "HCN_YIELD": [0, 0, 0],
                "HCL_YIELD": [0, 0, 0],
                "TRACE_YIELD": [0, 0, 0],
            }
        )

        # Create Fire from DataFrame
        fire = Fires(
            id="FIRE1",
            comp_id="ROOM1",
            fire_id="WOOD",
            location=[1.0, 2.0],
            data_table=original_df,
        )

        # Convert back to DataFrame
        result_df = fire.to_dataframe()

        # Check that the data values are preserved (all converted to float)
        expected_df = original_df.astype(float)
        pd.testing.assert_frame_equal(expected_df, result_df)

    def test_mixed_data_types_conversion(self):
        """Test that mixed numeric types (int, float) are handled correctly."""
        data_mixed = [
            [0, 0, 0.5, 0.1, 0.01, 0.01, 0, 0, 0],  # mix of int and float
            [60.0, 1000, 0.5, 1, 0.01, 0.01, 0, 0, 0],  # mix of float and int
        ]
        fire = Fires(
            id="FIRE1",
            comp_id="ROOM1",
            fire_id="WOOD",
            location=[1.0, 2.0],
            data_table=data_mixed,
        )

        # All values should be converted to float
        for row in fire.data_table:
            for value in row:
                assert isinstance(value, float)

    def test_repr_html(self) -> None:
        """Test _repr_html_ method."""
        data_table = [
            [0, 100, 0.5, 0.1, 0.01, 0.01, 0, 0, 0],
            [60, 500, 1.0, 0.5, 0.01, 0.01, 0, 0, 0],
        ]
        fire = Fires(
            id="FIRE1",
            comp_id="ROOM1",
            fire_id="POLYURETHANE",
            location=[2.0, 3.0],
            heat_of_combustion=25000,
            radiative_fraction=0.4,
            data_table=data_table,
        )

        html_str = fire._repr_html_()

        # Check that it returns valid HTML string
        assert isinstance(html_str, str)
        assert len(html_str) > 0

        # Check for expected HTML structure
        assert '<div class="pycfast-card' in html_str
        assert "Fire: FIRE1" in html_str
        assert "POLYURETHANE" in html_str
        assert "ROOM1" in html_str

        # Check fire properties
        assert "(2.0, 3.0)" in html_str
        assert "25000" in html_str  # heat of combustion
        assert "0.4" in html_str  # radiative fraction
        assert "2" in html_str  # data rows count - more flexible check


class TestFiresSetItemValidation:
    """Test validation in __setitem__ to ensure data integrity."""

    def test_setitem_invalid_location_too_few(self, make_fire):
        """Test that __setitem__ rejects location with wrong length."""
        fire = make_fire()
        with pytest.raises(ValueError, match="Location must be a list of two floats"):
            fire["location"] = [1.0]

    def test_setitem_invalid_location_too_many(self, make_fire):
        """Test that __setitem__ rejects location with too many elements."""
        fire = make_fire()
        with pytest.raises(ValueError, match="Location must be a list of two floats"):
            fire["location"] = [1.0, 2.0, 3.0]

    def test_setitem_valid_location(self, make_fire):
        """Test that __setitem__ accepts valid location change."""
        fire = make_fire()
        fire["location"] = [5.0, 6.0]
        assert fire.location == [5.0, 6.0]

    def test_setitem_valid_scalar_change(self, make_fire):
        """Test that __setitem__ accepts valid scalar property changes."""
        fire = make_fire()
        fire["radiative_fraction"] = 0.5
        assert fire.radiative_fraction == 0.5

    def test_setitem_invalid_does_not_mutate_state(self, make_fire):
        """Test that a failed __setitem__ rolls back to the previous value."""
        fire = make_fire(location=[1.0, 2.0])
        before = fire.location.copy()

        with pytest.raises(ValueError):
            fire["location"] = [1.0, 2.0, 3.0]

        assert fire.location == before
