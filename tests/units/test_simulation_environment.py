from __future__ import annotations

import pytest

from pycfast.simulation_environment import SimulationEnvironment

"""
Tests for the SimulationEnvironment class.
"""


class TestSimulationEnvironment:
    """Test class for SimulationEnvironment."""

    def test_init_basic(self):
        """Test basic initialization with required parameters."""
        sim_env = SimulationEnvironment(title="Test Simulation")
        assert sim_env.title == "Test Simulation"
        assert sim_env.time_simulation == 900
        assert sim_env.print == 60
        assert sim_env.smokeview == 15
        assert sim_env.spreadsheet == 15
        assert sim_env.init_pressure == 101325
        assert sim_env.relative_humidity == 50
        assert sim_env.interior_temperature == 20
        assert sim_env.exterior_temperature == 20
        assert sim_env.adiabatic is None
        assert sim_env.max_time_step is None
        assert sim_env.lower_oxygen_limit is None
        assert sim_env.extra_custom is None

    def test_init_with_all_parameters(self):
        """Test initialization with all parameters."""
        sim_env = SimulationEnvironment(
            title="Complete Simulation",
            time_simulation=1800,
            print=10,
            smokeview=5,
            spreadsheet=5,
            init_pressure=101000,
            relative_humidity=60,
            interior_temperature=25,
            exterior_temperature=15,
            adiabatic=True,
            max_time_step=1.0,
            lower_oxygen_limit=12.0,
            extra_custom="&DIAG CFAST = 1 /",
        )
        assert sim_env.title == "Complete Simulation"
        assert sim_env.time_simulation == 1800
        assert sim_env.print == 10
        assert sim_env.smokeview == 5
        assert sim_env.spreadsheet == 5
        assert sim_env.init_pressure == 101000
        assert sim_env.relative_humidity == 60
        assert sim_env.interior_temperature == 25
        assert sim_env.exterior_temperature == 15
        assert sim_env.adiabatic is True
        assert sim_env.max_time_step == 1.0
        assert sim_env.lower_oxygen_limit == 12.0
        assert sim_env.extra_custom == "&DIAG CFAST = 1 /"

    def test_to_input_string_basic(self):
        """Test basic input string generation."""
        sim_env = SimulationEnvironment(
            title="Test Simulation",
            time_simulation=1800,
            print=30,
            smokeview=10,
            spreadsheet=10,
        )
        result = sim_env.to_input_string()

        # Check HEAD section
        assert "&HEAD VERSION = 7700 TITLE = 'Test Simulation' /\n" in result

        # Check TIME section
        assert (
            "&TIME SIMULATION = 1800 PRINT = 30 SMOKEVIEW = 10 SPREADSHEET = 10 /\n"
            in result
        )

        # Check INIT section with defaults
        assert (
            "&INIT PRESSURE = 101325 RELATIVE_HUMIDITY = 50 INTERIOR_TEMPERATURE = 20 EXTERIOR_TEMPERATURE = 20 /\n"
            in result
        )

        # Check comment
        assert "!! Scenario Configuration" in result

    def test_to_input_string_with_custom_conditions(self):
        """Test input string generation with custom initial conditions."""
        sim_env = SimulationEnvironment(
            title="Custom Conditions",
            time_simulation=600,
            print=5,
            smokeview=1,
            spreadsheet=1,
            init_pressure=102000,
            relative_humidity=70,
            interior_temperature=30,
            exterior_temperature=10,
        )
        result = sim_env.to_input_string()

        assert (
            "&INIT PRESSURE = 102000 RELATIVE_HUMIDITY = 70 INTERIOR_TEMPERATURE = 30 EXTERIOR_TEMPERATURE = 10 /\n"
            in result
        )

    @pytest.mark.parametrize(
        ("misc_kwargs", "expected_token"),
        [
            pytest.param(
                {"adiabatic": True},
                "ADIABATIC = .TRUE.",
                id="adiabatic-true",
            ),
            pytest.param(
                {"max_time_step": 0.5},
                "MAX_TIME_STEP = 0.5",
                id="max-time-step",
            ),
            pytest.param(
                {"lower_oxygen_limit": 10.0},
                "LOWER_OXYGEN_LIMIT = 10.0",
                id="lower-oxygen-limit",
            ),
        ],
    )
    def test_to_input_string_with_single_misc_option(
        self, misc_kwargs: dict, expected_token: str
    ):
        """Test input string generation with individual MISC parameters."""
        sim_env = SimulationEnvironment(
            title="MISC Test",
            time_simulation=300,
            **misc_kwargs,  # type: ignore[arg-type]
        )
        result = sim_env.to_input_string()
        assert "&MISC" in result
        assert expected_token in result

    def test_to_input_string_with_misc_adiabatic_false(self):
        """Test input string generation with adiabatic walls explicitly disabled."""
        sim_env = SimulationEnvironment(
            title="Non-Adiabatic Test",
            time_simulation=300,
            adiabatic=False,
            max_time_step=0.1,  # Add another MISC option to force MISC section
        )
        result = sim_env.to_input_string()

        assert "&MISC" in result
        assert "ADIABATIC = .FALSE." in result

    def test_to_input_string_with_all_misc_options(self):
        """Test input string generation with all MISC parameters."""
        sim_env = SimulationEnvironment(
            title="All MISC Options",
            time_simulation=300,
            adiabatic=True,
            max_time_step=1.0,
            lower_oxygen_limit=12.5,
        )
        result = sim_env.to_input_string()

        assert (
            "&MISC ADIABATIC = .TRUE. MAX_TIME_STEP = 1.0 LOWER_OXYGEN_LIMIT = 12.5 /\n"
            in result
        )

    def test_to_input_string_without_misc_section(self):
        """Test input string generation without MISC section when not needed."""
        sim_env = SimulationEnvironment(
            title="No MISC Test",
            time_simulation=300,
        )
        result = sim_env.to_input_string()

        assert "&MISC" not in result

    def test_to_input_string_with_extra_custom(self):
        """Test input string generation with extra custom parameters."""
        sim_env = SimulationEnvironment(
            title="Custom Extra",
            time_simulation=300,
            extra_custom="&DIAG CFAST = 1 /\n&DUMP MASS_BUDGET = .TRUE. /",
        )
        result = sim_env.to_input_string()

        assert "&DIAG CFAST = 1 /\n&DUMP MASS_BUDGET = .TRUE. /" in result

    def test_to_input_string_title_with_special_characters(self):
        """Test input string generation with special characters in title."""
        sim_env = SimulationEnvironment(
            title="Test-123 (Version A)",
            time_simulation=300,
        )
        result = sim_env.to_input_string()

        assert "TITLE = 'Test-123 (Version A)'" in result

    def test_to_input_string_zero_output_intervals(self):
        """Test input string generation with zero output intervals."""
        sim_env = SimulationEnvironment(
            title="Zero Outputs",
            time_simulation=300,
            print=0,
            smokeview=0,
            spreadsheet=0,
        )
        result = sim_env.to_input_string()

        assert "PRINT = 0" in result
        assert "SMOKEVIEW = 0" in result
        assert "SPREADSHEET = 0" in result

    def test_to_input_string_structure(self):
        """Test the overall structure of the input string."""
        sim_env = SimulationEnvironment(
            title="Structure Test",
            time_simulation=300,
        )
        result = sim_env.to_input_string()

        lines = result.strip().split("\n")
        # Should have HEAD, comment, TIME, INIT lines at minimum
        assert len(lines) >= 4
        assert lines[0].startswith("&HEAD")
        assert "!! Scenario Configuration" in lines[2]
        assert lines[3].startswith("&TIME")
        assert lines[4].startswith("&INIT")

    def test_to_input_string_version_number(self):
        """Test that the correct CFAST version is specified."""
        sim_env = SimulationEnvironment(title="Version Test", time_simulation=300)
        result = sim_env.to_input_string()

        assert "VERSION = 7700" in result

    def test_init_time_simulation_zero_or_negative(self):
        """Test that initialization fails with zero or negative time_simulation."""
        with pytest.raises(ValueError, match="time_simulation must be positive"):
            SimulationEnvironment(title="Test", time_simulation=0)

    def test_init_time_simulation_exceeds_max_warning(self):
        """Test that a warning is raised when time_simulation exceeds 86400 s."""
        with pytest.warns(UserWarning, match="exceeds 86400 s"):
            SimulationEnvironment(title="Test", time_simulation=90000)

    def test_init_invalid_relative_humidity_warning(self):
        """Test that a warning is raised for relative_humidity outside [0, 100]."""
        with pytest.warns(UserWarning, match="relative_humidity.*is outside"):
            SimulationEnvironment(title="Test", relative_humidity=110)

    @pytest.mark.parametrize(
        "param",
        ["interior_temperature", "exterior_temperature"],
    )
    def test_init_temperature_below_absolute_zero_warning(self, param: str):
        """Test that a warning is raised for temperatures below absolute zero."""
        with pytest.warns(UserWarning, match="below absolute zero"):
            SimulationEnvironment(title="Test", **{param: -300.0})  # type: ignore[arg-type]

    def test_long_title_handling(self):
        """Test handling of titles approaching 50 character limit."""
        # Test 50 character title (at limit)
        long_title = "A" * 50
        sim_env = SimulationEnvironment(title=long_title, time_simulation=300)
        assert sim_env.title == long_title

        # Test longer than 50 characters issues a warning (CFAST truncates to 50)
        very_long_title = "A" * 100
        with pytest.warns(UserWarning, match="CFAST truncates titles to 50 characters"):
            sim_env = SimulationEnvironment(title=very_long_title, time_simulation=300)
        assert sim_env.title == very_long_title

    def test_parameter_types(self):
        """Test that parameters accept appropriate types."""
        # Integer time values
        sim_env = SimulationEnvironment(title="Test", time_simulation=1800)
        assert isinstance(sim_env.time_simulation, int)

        # Float pressure and temperature values
        sim_env = SimulationEnvironment(
            title="Test",
            time_simulation=300,
            init_pressure=101325.5,
            interior_temperature=20.5,
        )
        assert isinstance(sim_env.init_pressure, float)
        assert isinstance(sim_env.interior_temperature, float)

    def test_none_values_in_misc_section(self):
        """Test that None values don't appear in MISC section."""
        sim_env = SimulationEnvironment(
            title="Test",
            time_simulation=300,
            adiabatic=None,
            max_time_step=None,
            lower_oxygen_limit=None,
        )
        result = sim_env.to_input_string()

        assert "&MISC" not in result

    # Tests for dunder methods
    def test_repr(self) -> None:
        """Test __repr__ method."""
        sim_env = SimulationEnvironment(
            title="Fire Test Simulation",
            time_simulation=1800,
            print=30,
            smokeview=10,
            init_pressure=101000,
            relative_humidity=65,
            interior_temperature=22,
            exterior_temperature=18,
        )

        repr_str = repr(sim_env)
        assert "SimulationEnvironment(" in repr_str
        assert "title='Fire Test Simulation'" in repr_str
        assert "time_simulation=1800" in repr_str
        assert "print=30" in repr_str
        assert "smokeview=10" in repr_str

    def test_str(self) -> None:
        """Test __str__ method."""
        sim_env = SimulationEnvironment(
            title="Building Fire Simulation",
            time_simulation=2400,
            print=60,
            smokeview=15,
            init_pressure=101325,
            relative_humidity=45,
            interior_temperature=20,
            exterior_temperature=15,
            adiabatic=False,
            max_time_step=0.5,
        )

        str_repr = str(sim_env)
        assert "Simulation Environment 'Building Fire Simulation'" in str_repr
        assert "duration=2400s" in str_repr
        assert "temp_in=20°C" in str_repr
        assert "temp_out=15°C" in str_repr

    def test_str_with_optional_parameters(self) -> None:
        """Test __str__ method with optional parameters."""
        sim_env = SimulationEnvironment(
            title="Advanced Test",
            time_simulation=3600,
            adiabatic=True,
            max_time_step=1.0,
            lower_oxygen_limit=15.0,
        )

        str_repr = str(sim_env)
        assert "Simulation Environment 'Advanced Test'" in str_repr
        assert "duration=3600s" in str_repr
        assert "temp_in=20°C" in str_repr
        assert "temp_out=20°C" in str_repr

    def test_getitem(self) -> None:
        """Test __getitem__ method."""
        sim_env = SimulationEnvironment(
            title="Test Environment",
            time_simulation=1200,
            print=45,
            smokeview=20,
            spreadsheet=10,
            init_pressure=101500,
            relative_humidity=55,
            interior_temperature=25,
            exterior_temperature=10,
            adiabatic=True,
            max_time_step=0.8,
            lower_oxygen_limit=13.0,
        )

        assert sim_env["title"] == "Test Environment"
        assert sim_env["time_simulation"] == 1200
        assert sim_env["print"] == 45
        assert sim_env["smokeview"] == 20
        assert sim_env["spreadsheet"] == 10
        assert sim_env["init_pressure"] == 101500
        assert sim_env["relative_humidity"] == 55
        assert sim_env["interior_temperature"] == 25
        assert sim_env["exterior_temperature"] == 10
        assert sim_env["adiabatic"] is True
        assert sim_env["max_time_step"] == 0.8
        assert sim_env["lower_oxygen_limit"] == 13.0

    def test_getitem_invalid_key(self) -> None:
        """Test __getitem__ method with invalid key."""
        sim_env = SimulationEnvironment(title="Test")

        with pytest.raises(
            KeyError, match="Property 'invalid_key' not found in SimulationEnvironment"
        ):
            sim_env["invalid_key"]

    def test_setitem(self) -> None:
        """Test __setitem__ method."""
        sim_env = SimulationEnvironment(title="Test")

        # Test setting various properties
        sim_env["title"] = "New Title"
        assert sim_env.title == "New Title"

        sim_env["time_simulation"] = 2400
        assert sim_env.time_simulation == 2400

        sim_env["print"] = 30
        assert sim_env.print == 30

        sim_env["smokeview"] = 5
        assert sim_env.smokeview == 5

        sim_env["spreadsheet"] = 10
        assert sim_env.spreadsheet == 10

        sim_env["init_pressure"] = 102000
        assert sim_env.init_pressure == 102000

        sim_env["relative_humidity"] = 70
        assert sim_env.relative_humidity == 70

        sim_env["interior_temperature"] = 30
        assert sim_env.interior_temperature == 30

        sim_env["exterior_temperature"] = 5
        assert sim_env.exterior_temperature == 5

    def test_setitem_optional_parameters(self) -> None:
        """Test __setitem__ method with optional parameters."""
        sim_env = SimulationEnvironment(title="Test")

        sim_env["adiabatic"] = True
        assert sim_env.adiabatic is True

        sim_env["max_time_step"] = 0.5
        assert sim_env.max_time_step == 0.5

        sim_env["lower_oxygen_limit"] = 16.0
        assert sim_env.lower_oxygen_limit == 16.0

        sim_env["extra_custom"] = "&DIAG RESIDUE = 1 /"
        assert sim_env.extra_custom == "&DIAG RESIDUE = 1 /"

    def test_setitem_invalid_key(self) -> None:
        """Test __setitem__ method with invalid key."""
        sim_env = SimulationEnvironment(title="Test")

        with pytest.raises(KeyError, match="Cannot set 'invalid_key'"):
            sim_env["invalid_key"] = "value"

    def test_setitem_invalid_does_not_mutate_state(self) -> None:
        """Test that a failed __setitem__ rolls back to the previous value."""
        sim_env = SimulationEnvironment(title="Test", time_simulation=600)

        with pytest.raises(ValueError):
            sim_env["time_simulation"] = -100

        assert sim_env.time_simulation == 600
