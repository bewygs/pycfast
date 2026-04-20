from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from pycfast.fire import Fire

"""
Tests for the Fire class.
"""


@pytest.fixture()
def make_fire():
    """Create a Fire instance with sensible defaults."""

    def _make(**kwargs: object) -> Fire:
        defaults: dict[str, object] = {
            "id": "FIRE1",
            "comp_id": "ROOM1",
            "fire_id": "POLYURETHANE",
            "location": [2.0, 3.0],
        }
        defaults.update(kwargs)
        return Fire(**defaults)  # type: ignore[arg-type]

    return _make


class TestFire:
    """Test class for Fire."""

    def test_init_basic(self):
        """Test basic initialization with required parameters."""
        fire = Fire(
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
        fire = Fire(
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

    def test_init_invalid_location_type(self):
        """Test that initialization fails when location is not a list."""
        with pytest.raises(TypeError, match="location must be a list"):
            Fire(
                id="FIRE1",
                comp_id="ROOM1",
                fire_id="POLYURETHANE",
                location=(2.0, 3.0),  # type: ignore[arg-type]
            )

    @pytest.mark.parametrize(
        "location",
        [
            pytest.param([2.0], id="too-few"),
            pytest.param([2.0, 3.0, 1.0], id="too-many"),
        ],
    )
    def test_init_invalid_location_length(self, location: list[float]):
        """Test that initialization fails with wrong location dimensions."""
        with pytest.raises(ValueError, match="location must be a list of two floats"):
            Fire(
                id="FIRE1",
                comp_id="ROOM1",
                fire_id="POLYURETHANE",
                location=location,
            )

    @pytest.mark.parametrize("criterion", ["TEMPERATURE", "FLUX"])
    def test_init_missing_device_id(self, make_fire, criterion: str):
        """Test that initialization fails when device_id is missing for sensor-based ignition."""
        with pytest.raises(ValueError, match="device_id must be specified"):
            make_fire(ignition_criterion=criterion, set_point=100.0, device_id=None)

    def test_init_invalide_heat_of_combustion(self, make_fire):
        """Test that initialization fails with negative heat of combustion."""
        with pytest.raises(ValueError, match="heat_of_combustion must be positive"):
            make_fire(heat_of_combustion=-1000)

    @pytest.mark.parametrize(
        "param",
        ["carbon", "chlorine", "hydrogen", "nitrogen", "oxygen"],
    )
    def test_init_negative_atomic_values(self, make_fire, param: str):
        """Test that initialization fails with negative atomic values."""
        with pytest.raises(ValueError, match="must be non-negative"):
            make_fire(**{param: -1})  # type: ignore[arg-type]

    def test_carbon_and_hydrogen_zero_warning(self, make_fire):
        """Test that a warning is raised when both carbon and hydrogen are zero."""
        with pytest.warns(UserWarning, match="fuel contains no hydrocarbon"):
            make_fire(fire_id="INERT_GAS", carbon=0, hydrogen=0)

    def test_invalid_radiative_fraction_warning(self, make_fire):
        """Test that initialization fails with invalid radiative fraction."""
        with pytest.warns(UserWarning, match="This may cause inaccurate results"):
            make_fire(radiative_fraction=1.5)

    def test_init_invalid_data_table_columns(self):
        """Test that initialization fails with wrong number of columns in data table."""
        invalid_data_table = [
            [0, 100, 0.5],  # Only 3 columns instead of 9
        ]
        with pytest.raises(ValueError, match="data_table must have exactly 9 columns"):
            Fire(
                id="FIRE1",
                comp_id="ROOM1",
                fire_id="POLYURETHANE",
                location=[2.0, 3.0],
                data_table=invalid_data_table,
            )

    def test_to_input_string_basic(self):
        """Test basic input string generation."""
        fire = Fire(
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
                None,
                ["IGNITION_CRITERION = 'TIME'", "SETPOINT = 30.0"],
                ["DEVC_ID"],
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
        fire = Fire(
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
        fire = Fire(
            id="FIRE1",
            comp_id="ROOM1",
            fire_id="METHANE",
            location=[2.0, 3.0],
            carbon=2,
            chlorine=0,
            hydrogen=6,
            nitrogen=0,
            oxygen=0,
            heat_of_combustion=55000,
            radiative_fraction=0.30,
        )
        result = fire.to_input_string()
        assert "&CHEM" in result
        assert "ID = 'METHANE'" in result
        assert "CARBON = 2" in result
        assert "HYDROGEN = 6" in result
        assert "HEAT_OF_COMBUSTION = 55000" in result
        assert "RADIATIVE_FRACTION = 0.3" in result

    def test_to_input_string_empty_data_table(self):
        """Test input string generation with empty data table."""
        with pytest.raises(
            ValueError, match="data_table must contain at least one row"
        ):
            Fire(
                id="FIRE1",
                comp_id="ROOM1",
                fire_id="POLYURETHANE",
                location=[2.0, 3.0],
                data_table=[],
            )

    def test_init_no_ignition_criterion_with_setpoint(self):
        """Test initialization with setpoint but no ignition criterion."""
        fire = Fire(
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
        fire = Fire(
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
        fire = Fire(
            id="FIRE1",
            comp_id="ROOM1",
            fire_id="POLYURETHANE",
            location=[2.0, 3.0],
            heat_of_combustion=25000,
            radiative_fraction=0.4,
            data_table=data_table,
        )

        repr_str = repr(fire)
        assert "Fire(" in repr_str
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
        fire = Fire(
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
        fire = Fire(id="FIRE1", comp_id="ROOM1", fire_id="WOOD", location=[1.0, 2.0])

        with pytest.raises(KeyError, match="Property 'invalid_key' not found in Fire"):
            fire["invalid_key"]

    def test_setitem(self) -> None:
        """Test __setitem__ method."""
        fire = Fire(id="FIRE1", comp_id="ROOM1", fire_id="WOOD", location=[1.0, 2.0])

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
        fire = Fire(id="FIRE1", comp_id="ROOM1", fire_id="WOOD", location=[1.0, 2.0])

        with pytest.raises(KeyError, match="Cannot set 'invalid_key'"):
            fire["invalid_key"] = "value"


class TestFireDataTableFormats:
    """Test class for Fire data_table format handling."""

    def test_data_table_list_of_lists(self):
        """Test data_table with list of lists (original format)."""
        data_table = [
            [0, 0, 0.5, 0.1, 0.01, 0.01, 0, 0, 0],
            [60, 1000, 0.5, 1.0, 0.01, 0.01, 0, 0, 0],
            [300, 500, 1.0, 1.0, 0.01, 0.01, 0, 0, 0],
        ]
        fire = Fire(
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
        fire = Fire(
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
        fire = Fire(
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
        fire = Fire(
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
            Fire(
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
            Fire(
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
            Fire(
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
            match="data_table must be a list of lists, dict, NumPy array, pandas DataFrame, or None",
        ):
            Fire(
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
            Fire(
                id="FIRE1",
                comp_id="ROOM1",
                fire_id="WOOD",
                location=[1.0, 2.0],
                data_table=data_array,
            )

    def test_to_dataframe(self):
        """Test conversion to pandas DataFrame."""
        data_table = [
            [0, 0, 0.5, 0.1, 0.01, 0.01, 0, 0, 0],
            [60, 1000, 0.5, 1.0, 0.01, 0.01, 0, 0, 0],
            [300, 500, 1.0, 1.0, 0.01, 0.01, 0, 0, 0],
        ]
        fire = Fire(
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
        assert list(df.columns) == Fire.LABELS

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
        fire = Fire(
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
        fire = Fire(
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


class TestFireDictDataTable:
    """Test dict-format data_table support."""

    def test_dict_data_table_basic(self, make_fire):
        """Test basic dict data_table with lists and scalars."""
        fire = make_fire(
            data_table={
                "TIME": [0, 60, 120],
                "HRR": [0, 500, 1000],
                "HEIGHT": 0.5,
                "AREA": 0.1,
                "CO_YIELD": 0.01,
                "SOOT_YIELD": 0.02,
                "HCN_YIELD": 0,
                "HCL_YIELD": 0,
                "TRACE_YIELD": 0,
            }
        )
        assert len(fire.data_table) == 3
        assert fire.data_table[0] == [0, 0, 0.5, 0.1, 0.01, 0.02, 0, 0, 0]
        assert fire.data_table[2] == [120, 1000, 0.5, 0.1, 0.01, 0.02, 0, 0, 0]

    def test_dict_data_table_all_lists(self, make_fire):
        """Test dict data_table where all values are lists."""
        fire = make_fire(
            data_table={
                "TIME": [0, 60],
                "HRR": [0, 500],
                "HEIGHT": [0.5, 1.0],
                "AREA": [0.1, 0.2],
                "CO_YIELD": [0.01, 0.02],
                "SOOT_YIELD": [0.01, 0.02],
                "HCN_YIELD": [0, 0],
                "HCL_YIELD": [0, 0],
                "TRACE_YIELD": [0, 0],
            }
        )
        assert len(fire.data_table) == 2
        assert fire.data_table[1] == [60, 500, 1.0, 0.2, 0.02, 0.02, 0, 0, 0]

    def test_dict_data_table_all_scalars_raises(self, make_fire):
        """Test that dict with only scalar values raises an error."""
        with pytest.raises(ValueError, match="at least one list-valued column"):
            make_fire(
                data_table={
                    "TIME": 0,
                    "HRR": 0,
                    "HEIGHT": 0.5,
                    "AREA": 0.1,
                    "CO_YIELD": 0.01,
                    "SOOT_YIELD": 0.02,
                    "HCN_YIELD": 0,
                    "HCL_YIELD": 0,
                    "TRACE_YIELD": 0,
                }
            )

    def test_dict_data_table_mismatched_lengths(self, make_fire):
        """Test that lists with different lengths raise an error."""
        with pytest.raises(ValueError, match="same length"):
            make_fire(
                data_table={
                    "TIME": [0, 60, 120],  # 3 elements
                    "HRR": [0, 500],  # 2 elements
                    "HEIGHT": 0.5,
                    "AREA": 0.1,
                    "CO_YIELD": 0.01,
                    "SOOT_YIELD": 0.02,
                    "HCN_YIELD": 0,
                    "HCL_YIELD": 0,
                    "TRACE_YIELD": 0,
                }
            )

    def test_dict_data_table_invalid_key(self, make_fire):
        """Test that an invalid column name raises an error."""
        with pytest.raises(ValueError, match="Invalid data_table keys"):
            make_fire(
                data_table={
                    "TIME": [0],
                    "HRR": [0],
                    "HEIGHT": 0,
                    "AREA": 0,
                    "CO_YIELD": 0,
                    "SOOT_YIELD": 0,
                    "HCN_YIELD": 0,
                    "HCL_YIELD": 0,
                    "INVALID_COL": 0,
                }
            )

    def test_dict_data_table_missing_key(self, make_fire):
        """Test that a missing column raises an error."""
        with pytest.raises(ValueError, match="Missing required data_table keys"):
            make_fire(
                data_table={
                    "TIME": [0],
                    "HRR": [0],
                    "HEIGHT": 0,
                }
            )

    def test_dict_data_table_non_numeric_value(self, make_fire):
        """Test that non-numeric values raise an error."""
        with pytest.raises(ValueError, match="non-numeric value"):
            make_fire(
                data_table={
                    "TIME": [0],
                    "HRR": [0],
                    "HEIGHT": "invalid",
                    "AREA": 0,
                    "CO_YIELD": 0,
                    "SOOT_YIELD": 0,
                    "HCN_YIELD": 0,
                    "HCL_YIELD": 0,
                    "TRACE_YIELD": 0,
                }
            )

    def test_dict_data_table_empty_list_value(self, make_fire):
        """Test that an empty list value raises an error."""
        with pytest.raises(ValueError, match="at least one element"):
            make_fire(
                data_table={
                    "TIME": [],
                    "HRR": [],
                    "HEIGHT": 0,
                    "AREA": 0,
                    "CO_YIELD": 0,
                    "SOOT_YIELD": 0,
                    "HCN_YIELD": 0,
                    "HCL_YIELD": 0,
                    "TRACE_YIELD": 0,
                }
            )


class TestFireSetItemValidation:
    """Test validation in __setitem__ to ensure data integrity."""

    @pytest.mark.parametrize(
        "location",
        [
            pytest.param([1.0], id="too-few"),
            pytest.param([1.0, 2.0, 3.0], id="too-many"),
        ],
    )
    def test_setitem_invalid_location_length(self, make_fire, location: list[float]):
        """Test that __setitem__ rejects location with wrong length."""
        fire = make_fire()
        with pytest.raises(ValueError, match="location must be a list of two floats"):
            fire["location"] = location

    def test_setitem_invalid_does_not_mutate_state(self, make_fire):
        """Test that a failed __setitem__ rolls back to the previous value."""
        fire = make_fire(location=[1.0, 2.0])
        before = fire.location.copy()

        with pytest.raises(ValueError):
            fire["location"] = [1.0, 2.0, 3.0]

        assert fire.location == before
