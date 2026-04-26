from __future__ import annotations

import os
import subprocess
import tempfile
from unittest.mock import Mock, patch

import numpy as np
import pandas as pd
import pytest

from pycfast.ceiling_floor_vent import CeilingFloorVent
from pycfast.compartment import Compartment
from pycfast.device import Device
from pycfast.fire import Fire
from pycfast.material import Material
from pycfast.mechanical_vent import MechanicalVent
from pycfast.model import CFASTModel, _resolve_cfast_exe
from pycfast.simulation_environment import SimulationEnvironment
from pycfast.surface_connection import SurfaceConnection
from pycfast.wall_vent import WallVent

"""
Tests for the CFASTModel class.
"""


class TestCFASTModel:
    """Test class for CFASTModel."""

    def create_minimal_model(self) -> CFASTModel:
        """Create a minimal valid CFASTModel for testing."""
        simulation_env = SimulationEnvironment(title="Test Simulation")
        compartment = Compartment(id="ROOM1", width=3.0, depth=4.0, height=2.4)

        return CFASTModel(
            simulation_environment=simulation_env,
            compartments=[compartment],
            file_name="test.in",
        )

    def create_full_model(self) -> CFASTModel:
        """Create a fully configured CFASTModel for testing."""
        simulation_env = SimulationEnvironment(title="Full Test Simulation")

        compartment1 = Compartment(id="ROOM1", width=3.0, depth=4.0, height=2.4)
        compartment2 = Compartment(id="ROOM2", width=4.0, depth=4.0, height=2.4)

        material = Material(
            id="GYPSUM",
            material="Gypsum Board",
            conductivity=0.17,
            density=790,
            specific_heat=0.9,
            thickness=0.016,
        )

        wall_vent = WallVent(
            id="DOOR1",
            comps_ids=["ROOM1", "ROOM2"],
            bottom=0.0,
            height=2.0,
            width=0.9,
            face="RIGHT",
        )

        ceiling_vent = CeilingFloorVent(
            id="CEILING1",
            comps_ids=["ROOM1", "ROOM2"],
            area=1.0,
        )

        mechanical_vent = MechanicalVent(
            id="FAN1",
            comps_ids=["OUTSIDE", "ROOM1"],
            offsets=[0.0, 1.0],
        )

        fire = Fire(
            id="FIRE1",
            comp_id="ROOM1",
            fire_id="POLYURETHANE",
            location=[2.0, 2.0],
        )

        device = Device(
            id="TEMP1",
            comp_id="ROOM1",
            location=[1.0, 2.0, 1.5],
            type="HEAT_DETECTOR",
            material_id="",
            setpoint=70.0,
            rti=50.0,
        )

        surface_conn = SurfaceConnection.wall_connection(
            comp_id="ROOM1",
            comp_ids="ROOM2",
            fraction=0.5,
        )

        return CFASTModel(
            simulation_environment=simulation_env,
            compartments=[compartment1, compartment2],
            material_properties=[material],
            wall_vents=[wall_vent],
            ceiling_floor_vents=[ceiling_vent],
            mechanical_vents=[mechanical_vent],
            fires=[fire],
            devices=[device],
            surface_connections=[surface_conn],
            file_name="full_test.in",
        )

    def test_init_minimal(self):
        """Test minimal initialization with required parameters only."""
        model = self.create_minimal_model()

        assert model.simulation_environment.title == "Test Simulation"
        assert len(model.compartments) == 1
        assert model.compartments[0].id == "ROOM1"
        assert model.material_properties == []
        assert model.wall_vents == []
        assert model.ceiling_floor_vents == []
        assert model.mechanical_vents == []
        assert model.fires == []
        assert model.devices == []
        assert model.surface_connections == []
        assert model.file_name == "test.in"
        assert model.extra_arguments == []

    def test_init_full(self):
        """Test initialization with all parameters."""
        model = self.create_full_model()

        assert model.simulation_environment.title == "Full Test Simulation"
        assert len(model.compartments) == 2
        assert len(model.material_properties) == 1
        assert len(model.wall_vents) == 1
        assert len(model.ceiling_floor_vents) == 1
        assert len(model.mechanical_vents) == 1
        assert len(model.fires) == 1
        assert len(model.devices) == 1
        assert len(model.surface_connections) == 1
        assert model.file_name == "full_test.in"

    def test_init_with_extra_arguments(self):
        """Test initialization with extra command-line arguments."""
        model = self.create_minimal_model()
        model.extra_arguments = ["-v", "--debug"]

        assert model.extra_arguments == ["-v", "--debug"]

    def test_init_with_custom_cfast_exe(self):
        """Test initialization with custom CFAST executable path."""
        simulation_env = SimulationEnvironment(title="Test")
        compartment = Compartment(id="ROOM1")

        model = CFASTModel(
            simulation_environment=simulation_env,
            compartments=[compartment],
            cfast_exe="/custom/path/to/cfast",
        )

        assert model.cfast_exe == "/custom/path/to/cfast"

    def test_init_cfast_exe_none_by_default(self):
        """Test that cfast_exe is stored as None when not provided."""
        simulation_env = SimulationEnvironment(title="Test")
        compartment = Compartment(id="ROOM1")

        model = CFASTModel(
            simulation_environment=simulation_env,
            compartments=[compartment],
        )

        assert model.cfast_exe is None

    def test_write_input_content_minimal(self):
        """Test that input file is written with correct content for minimal model."""
        model = self.create_minimal_model()

        with tempfile.TemporaryDirectory() as temp_dir:
            model.file_name = os.path.join(temp_dir, "test_input.in")
            input_path = model._write_input()

            assert os.path.exists(input_path)

            # Check file content
            with open(input_path) as f:
                content = f.read()
                assert "&HEAD VERSION = 7700" in content
                assert "&COMP ID = 'ROOM1'" in content
                assert "&TAIL /" in content

    def test_write_input_content_full(self):
        """Test that input file is written with correct content for full model."""
        model = self.create_full_model()

        with tempfile.TemporaryDirectory() as temp_dir:
            model.file_name = os.path.join(temp_dir, "full_test.in")
            input_path = model._write_input()

            # Check file content
            with open(input_path) as f:
                content = f.read()

                # Check all sections are present
                assert "&HEAD VERSION = 7700" in content
                assert "&MATL ID = 'GYPSUM'" in content
                assert "&COMP ID = 'ROOM1'" in content
                assert "&COMP ID = 'ROOM2'" in content
                assert "&VENT TYPE = 'WALL' ID = 'DOOR1'" in content
                assert "&VENT TYPE = 'FLOOR' ID = 'CEILING1'" in content
                assert "&VENT TYPE = 'MECHANICAL' ID = 'FAN1'" in content
                assert "&FIRE ID = 'FIRE1'" in content
                assert "&DEVC ID = 'TEMP1'" in content
                assert "&CONN TYPE = 'WALL'" in content
                assert "&TAIL /" in content

    def test_write_input_section_order(self):
        """Test that input file sections are written in correct order."""
        model = self.create_full_model()

        with tempfile.TemporaryDirectory() as temp_dir:
            model.file_name = os.path.join(temp_dir, "order_test.in")
            input_path = model._write_input()

            with open(input_path) as f:
                content = f.read()

                # Find positions of key sections
                head_pos = content.find("&HEAD")
                matl_pos = content.find("&MATL")
                comp_pos = content.find("&COMP")
                fire_pos = content.find("&FIRE")
                tail_pos = content.find("&TAIL")

                # Check order (all should be >= 0 and in ascending order)
                assert 0 <= head_pos < matl_pos < comp_pos < fire_pos < tail_pos

    def test_write_input_file(self):
        """Test writing input file to disk."""
        model = self.create_minimal_model()

        with tempfile.TemporaryDirectory() as temp_dir:
            model.file_name = os.path.join(temp_dir, "test_input.in")
            input_path = model._write_input()

            assert os.path.exists(input_path)
            assert input_path == model.file_name

            # Check file content
            with open(input_path) as f:
                content = f.read()
                assert "&HEAD VERSION = 7700" in content
                assert "&COMP ID = 'ROOM1'" in content

    @patch("subprocess.run")
    @patch("pandas.read_csv")
    @patch("os.path.exists")
    def test_run_successful(self, mock_exists, mock_read_csv, mock_subprocess):
        """Test successful CFAST execution."""
        model = self.create_minimal_model()

        # Mock successful subprocess run
        mock_subprocess.return_value = Mock(
            returncode=0, stdout="CFAST execution completed", stderr=""
        )

        # Mock CSV file existence
        mock_exists.return_value = True

        # Mock CSV reading
        mock_df = pd.DataFrame({"Time": [0, 10, 20], "CEILT": [20, 25, 30]})
        mock_read_csv.return_value = mock_df

        with tempfile.TemporaryDirectory() as temp_dir:
            model.file_name = os.path.join(temp_dir, "test.in")

            with patch.object(model, "_get_log", return_value="Log content"):
                results = model.run()

            assert results is not None
            for csv_file in [
                "compartments",
                "devices",
                "diagnostics",
                "masses",
            ]:
                assert (
                    csv_file in results or os.path.join(temp_dir, csv_file) in results
                )
            assert isinstance(list(results.values())[0], pd.DataFrame)
            mock_subprocess.assert_called_once()

    @patch("subprocess.run")
    def test_run_subprocess_failure(self, mock_subprocess):
        """Test CFAST execution failure."""
        model = self.create_minimal_model()

        # Mock failed subprocess run
        mock_subprocess.side_effect = FileNotFoundError("CFAST executable not found")

        with tempfile.TemporaryDirectory() as temp_dir:
            model.file_name = os.path.join(temp_dir, "test.in")

            with pytest.raises(FileNotFoundError):
                model.run()

    @patch("subprocess.run")
    def test_run_cfast_error(self, mock_subprocess):
        """Test CFAST execution returning error code."""
        model = self.create_minimal_model()

        # Mock subprocess run with non-zero return code
        error = subprocess.CalledProcessError(
            1, ["cfast"], stderr="CFAST error occurred"
        )
        mock_subprocess.side_effect = error

        with tempfile.TemporaryDirectory() as temp_dir:
            model.file_name = os.path.join(temp_dir, "test.in")
            # Create a log file to avoid FileNotFoundError in _get_log()
            log_path = os.path.join(temp_dir, "test.log")
            with open(log_path, "w") as f:
                f.write("CFAST execution failed\n")

            with pytest.raises(subprocess.CalledProcessError):
                model.run()

    @patch("subprocess.run")
    @patch("pandas.read_csv")
    @patch("os.path.exists")
    def test_run_verbose_true(
        self, mock_exists, mock_read_csv, mock_subprocess, caplog
    ):
        """Test CFAST execution with verbose=True logs stdout and stderr at DEBUG level."""
        import logging

        model = self.create_minimal_model()

        # Mock successful subprocess run with stdout and stderr
        mock_subprocess.return_value = Mock(
            returncode=0,
            stdout="CFAST simulation started\nSimulation completed successfully",
            stderr="Warning: some minor issue detected",
        )

        # Mock CSV file existence
        mock_exists.return_value = True

        # Mock CSV reading
        mock_df = pd.DataFrame({"Time": [0, 10, 20], "CEILT": [20, 25, 30]})
        mock_read_csv.return_value = mock_df

        with tempfile.TemporaryDirectory() as temp_dir:
            model.file_name = os.path.join(temp_dir, "test.in")

            with caplog.at_level(logging.DEBUG, logger="pycfast"):
                results = model.run(verbose=True)

            assert "CFAST stdout:" in caplog.text
            assert "CFAST stderr:" in caplog.text
            assert results is not None

    @patch("subprocess.run")
    @patch("pandas.read_csv")
    @patch("os.path.exists")
    def test_run_verbose_false(
        self, mock_exists, mock_read_csv, mock_subprocess, caplog
    ):
        """Test CFAST execution with verbose=False does not log stdout and stderr."""
        import logging

        model = self.create_minimal_model()

        # Mock successful subprocess run with stdout and stderr
        mock_subprocess.return_value = Mock(
            returncode=0,
            stdout="CFAST simulation started\nSimulation completed successfully",
            stderr="Warning: some minor issue detected",
        )

        # Mock CSV file existence
        mock_exists.return_value = True

        # Mock CSV reading
        mock_df = pd.DataFrame({"Time": [0, 10, 20], "CEILT": [20, 25, 30]})
        mock_read_csv.return_value = mock_df

        with tempfile.TemporaryDirectory() as temp_dir:
            model.file_name = os.path.join(temp_dir, "test.in")

            with caplog.at_level(logging.DEBUG, logger="pycfast"):
                results = model.run(verbose=False)

            assert "CFAST stdout:" not in caplog.text
            assert "CFAST stderr:" not in caplog.text
            assert results is not None

    @patch("subprocess.run")
    @patch("pandas.read_csv")
    @patch("os.path.exists")
    def test_run_verbose_default(
        self, mock_exists, mock_read_csv, mock_subprocess, caplog
    ):
        """Test CFAST execution with default verbose=False does not log output."""
        import logging

        model = self.create_minimal_model()

        # Mock successful subprocess run with stdout and stderr
        mock_subprocess.return_value = Mock(
            returncode=0, stdout="CFAST simulation started", stderr="Some warning"
        )

        # Mock CSV file existence
        mock_exists.return_value = True

        # Mock CSV reading
        mock_df = pd.DataFrame({"Time": [0, 10], "CEILT": [20, 25]})
        mock_read_csv.return_value = mock_df

        with tempfile.TemporaryDirectory() as temp_dir:
            model.file_name = os.path.join(temp_dir, "test.in")

            with caplog.at_level(logging.DEBUG, logger="pycfast"):
                results = model.run()  # No verbose argument, should default to False

            assert "CFAST stdout:" not in caplog.text
            assert "CFAST stderr:" not in caplog.text
            assert results is not None

    @patch("subprocess.run")
    def test_run_verbose_with_error(self, mock_subprocess):
        """Test CFAST execution failure with verbose=True still raises error."""
        model = self.create_minimal_model()

        # Create a mock result object with stdout and stderr
        mock_result = Mock()
        mock_result.stdout = "CFAST started\nProcessing input..."
        mock_result.stderr = "Error: Invalid input detected"

        # Mock subprocess run that fails but first returns the result for verbose output
        error = subprocess.CalledProcessError(1, ["cfast"])
        error.stdout = "CFAST started\nProcessing input..."
        error.stderr = "Error: Invalid input detected"

        # Configure the mock to first set the result, then raise the error
        mock_subprocess.side_effect = error

        with tempfile.TemporaryDirectory() as temp_dir:
            model.file_name = os.path.join(temp_dir, "test.in")
            # Create a log file to avoid FileNotFoundError in _get_log()
            log_path = os.path.join(temp_dir, "test.log")
            with open(log_path, "w") as f:
                f.write("CFAST execution failed\n")

            with pytest.raises(subprocess.CalledProcessError):
                model.run(verbose=True)

            # Since the subprocess call fails immediately, verbose output won't be printed
            # This test verifies that the error is still properly raised with verbose=True
            mock_subprocess.assert_called_once()

    def test_get_log_content(self):
        """Test log file reading."""
        model = self.create_minimal_model()

        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = os.path.join(temp_dir, "test.log")
            with open(log_file, "w") as f:
                f.write("CFAST log content")

            model.file_name = os.path.join(temp_dir, "test.in")
            log_content = model._get_log()

            assert "CFAST log content" in log_content

    def test_get_log_content_no_file(self):
        """Test log file reading when file doesn't exist."""
        model = self.create_minimal_model()
        model.file_name = "/nonexistent/path/test.in"

        with pytest.raises(FileNotFoundError):
            model._get_log()

    def test_get_log_resolves_relative_filename(self):
        """A relative file_name must be resolved to the absolute log path."""
        model = self.create_minimal_model()

        with tempfile.TemporaryDirectory() as temp_dir:
            cwd = os.getcwd()
            try:
                os.chdir(temp_dir)
                with open("test.log", "w") as f:
                    f.write("CFAST log content")
                model.file_name = "test.in"  # relative on purpose
                assert "CFAST log content" in model._get_log()
            finally:
                os.chdir(cwd)

    def test_validate_dependencies_success(self):
        """Test dependency validation with valid model."""
        model = self.create_full_model()
        # Should not raise any exceptions
        model._validate_dependencies()

    def test_empty_lists_initialization(self):
        """Test that None values are converted to empty lists."""
        simulation_env = SimulationEnvironment(title="Test")
        compartment = Compartment(id="ROOM1")

        model = CFASTModel(
            simulation_environment=simulation_env,
            compartments=[compartment],
            material_properties=None,
            wall_vents=None,
            ceiling_floor_vents=None,
            mechanical_vents=None,
            fires=None,
            devices=None,
            surface_connections=None,
            extra_arguments=None,
        )

        assert model.material_properties == []
        assert model.wall_vents == []
        assert model.ceiling_floor_vents == []
        assert model.mechanical_vents == []
        assert model.fires == []
        assert model.devices == []
        assert model.surface_connections == []
        assert model.extra_arguments == []

    @patch.dict(os.environ, {"CFAST": "/env/path/to/cfast"})
    @patch("pycfast.model.shutil.which", return_value="/env/path/to/cfast")
    def test_resolve_cfast_exe_from_environment(self, mock_which):
        """Test _resolve_cfast_exe picks up the CFAST environment variable."""
        assert _resolve_cfast_exe(None) == "/env/path/to/cfast"
        mock_which.assert_called_once_with("/env/path/to/cfast")

    @patch.dict(os.environ, {}, clear=False)
    @patch("pycfast.model.shutil.which", return_value="/some/path/to/cfast")
    def test_resolve_cfast_exe_from_path(self, mock_which):
        """Test _resolve_cfast_exe finds cfast on system PATH."""
        os.environ.pop("CFAST", None)
        assert _resolve_cfast_exe(None) == "/some/path/to/cfast"
        mock_which.assert_called_once_with("cfast")

    @patch.dict(os.environ, {}, clear=False)
    @patch("pycfast.model.shutil.which", return_value=None)
    def test_resolve_cfast_exe_not_found(self, mock_which):
        """Test _resolve_cfast_exe raises FileNotFoundError when cfast is not found."""
        os.environ.pop("CFAST", None)
        with pytest.raises(FileNotFoundError, match="CFAST executable not found"):
            _resolve_cfast_exe(None)

    @patch("pycfast.model.shutil.which", return_value="/custom/path/to/cfast")
    def test_resolve_cfast_exe_explicit_path(self, mock_which):
        """Test _resolve_cfast_exe returns explicit path as-is."""
        assert _resolve_cfast_exe("/custom/path/to/cfast") == "/custom/path/to/cfast"
        mock_which.assert_called_once_with("/custom/path/to/cfast")

    @patch("pycfast.model.shutil.which", return_value=None)
    def test_resolve_cfast_exe_explicit_path_invalid(self, mock_which):
        """Test _resolve_cfast_exe raises FileNotFoundError for invalid explicit path."""
        with pytest.raises(FileNotFoundError, match="not found or not executable"):
            _resolve_cfast_exe("/bad/path/to/cfast")

    @patch.dict(os.environ, {"CFAST": "/bad/env/path"})
    @patch("pycfast.model.shutil.which", return_value=None)
    def test_resolve_cfast_exe_env_var_invalid(self, mock_which):
        """Test _resolve_cfast_exe raises FileNotFoundError for invalid $CFAST path."""
        with pytest.raises(FileNotFoundError, match="not found or not executable"):
            _resolve_cfast_exe(None)

    def test_save_writes_input_and_returns_path(self):
        """Test that save() writes the input file and returns its absolute path."""
        model = self.create_minimal_model()
        with tempfile.TemporaryDirectory() as temp_dir:
            model.file_name = os.path.join(temp_dir, "test_save.in")
            abs_path = model.save()
            assert os.path.exists(abs_path)
            assert abs_path == os.path.abspath(model.file_name)
            # The file should contain the expected CFAST header
            with open(abs_path) as f:
                content = f.read()
                assert "&HEAD VERSION = 7700" in content

    def test_view_cfast_input_file_pretty_print(self):
        """Test view_cfast_input_file returns pretty-printed content with line numbers and bold headers."""
        model = self.create_minimal_model()
        with tempfile.TemporaryDirectory() as temp_dir:
            model.file_name = os.path.join(temp_dir, "test_view.in")
            model.save()
            output = model.view_cfast_input_file(pretty_print=True)
            # Should contain line numbers and ANSI bold codes for headers
            assert "1:" in output
            assert "\033[1m" in output  # ANSI bold
            assert "&HEAD" in output
            assert "&COMP" in output
            assert "&TAIL" in output

    def test_view_cfast_input_file_raw(self):
        """Test view_cfast_input_file returns raw file content when pretty_print is False."""
        model = self.create_minimal_model()
        with tempfile.TemporaryDirectory() as temp_dir:
            model.file_name = os.path.join(temp_dir, "test_view_raw.in")
            model.save()
            output = model.view_cfast_input_file(pretty_print=False)
            # Should not contain line numbers or ANSI codes
            assert "&HEAD" in output
            assert "&COMP" in output
            assert "&TAIL" in output
            assert "\033[1m" not in output
            assert output == model._written_content

    def test_view_cfast_input_file_raises_if_not_written(self):
        """Test view_cfast_input_file raises RuntimeError if input file not generated yet."""
        model = self.create_minimal_model()
        model._input_written = False
        with pytest.raises(
            RuntimeError, match="CFAST input file has not been generated yet"
        ):
            model.view_cfast_input_file()

    def test_repr(self):
        """Test __repr__ method."""
        model = self.create_full_model()

        repr_str = repr(model)
        assert "CFASTModel(" in repr_str
        assert "file_name='full_test.in'" in repr_str
        assert "compartments=2" in repr_str
        assert "fires=1" in repr_str
        assert "wall_vents=1" in repr_str
        assert "devices=1" in repr_str
        assert "material_properties=1" in repr_str

    def test_str(self):
        """Test __str__ method delegates to summary()."""
        model = self.create_full_model()

        str_repr = str(model)
        assert "full_test.in" in str_repr
        assert "Compartment (2):" in str_repr
        assert "Fire (1):" in str_repr
        assert "Wall Vents (1):" in str_repr
        assert "Device (1):" in str_repr
        assert "Material Properties (1):" in str_repr

    # Note: __len__, __bool__, __eq__, __hash__, __contains__ methods not implemented in current version
    # These tests are removed to match actual implementation

    def test_iter(self) -> None:
        """Test __iter__ method."""
        model = self.create_full_model()

        components = list(model)
        component_types = [comp_type for comp_type, _ in components]

        # Should include all non-empty component types
        assert "compartments" in component_types
        assert "fires" in component_types
        assert "wall_vents" in component_types
        assert (
            "ceiling_floor_vents" in component_types
        )  # This is included in the full model
        assert (
            "mechanical_vents" in component_types
        )  # This is included in the full model
        assert "devices" in component_types
        assert "material_properties" in component_types

    def test_iter_minimal(self) -> None:
        """Test __iter__ method with minimal model."""
        model = self.create_minimal_model()

        components = list(model)
        assert len(components) == 1
        assert components[0][0] == "compartments"

    def test_summary(self) -> None:
        """Test summary method output."""
        model = self.create_minimal_model()

        result = model.summary()

        # Check that key information is in the output
        assert "Model: test.in" in result
        assert "Test Simulation" in result
        assert "Compartment (1):" in result
        assert "28.80 m³" in result  # Volume calculation: 3.0 * 4.0 * 2.4

    def test_summary_with_full_model(self) -> None:
        """Test summary method with a full model containing all components."""
        model = self.create_full_model()

        result = model.summary()

        # Check that all component types are shown
        assert "Compartment (2):" in result
        assert "Fire (1):" in result
        assert "Wall Vents (1):" in result
        assert "Device (1):" in result

    # Tests for update methods
    def test_update_fire_params(self) -> None:
        """Test update_fire_params method."""
        model = self.create_full_model()
        original_fire = model.fires[0]

        # Test updating fire parameters by index
        updated_model = model.update_fire_params(
            fire=0, heat_of_combustion=25000, radiative_fraction=0.4
        )

        # Check that original model is unchanged
        assert model.fires[0].heat_of_combustion == original_fire.heat_of_combustion
        assert model.fires[0].radiative_fraction == original_fire.radiative_fraction

        # Check that new model has updated values
        assert updated_model.fires[0].heat_of_combustion == 25000
        assert updated_model.fires[0].radiative_fraction == 0.4

        # Test updating by fire ID
        updated_model2 = model.update_fire_params(
            fire="FIRE1", heat_of_combustion=30000
        )
        assert updated_model2.fires[0].heat_of_combustion == 30000

        # Test with data_table
        fire_data = pd.DataFrame(
            {
                "time": [0, 60, 120],
                "heat_release_rate": [0, 1000, 2000],
                "height": [0.5, 0.5, 0.5],
                "area": [0.1, 0.2, 0.3],
                "co_yield": [0.01, 0.01, 0.01],
                "soot_yield": [0.01, 0.01, 0.01],
                "hcn_yield": [0, 0, 0],
                "hcl_yield": [0, 0, 0],
                "trace_yield": [0, 0, 0],
            }
        )

        updated_model3 = model.update_fire_params(data_table=fire_data)
        assert len(updated_model3.fires[0].data_table) == 3
        assert updated_model3.fires[0].data_table[0][1] == 0  # HRR at t=0
        assert updated_model3.fires[0].data_table[1][1] == 1000  # HRR at t=60

    def test_update_fire_params_with_numpy_array(self) -> None:
        """Test update_fire_params with numpy array data_table."""
        model = self.create_full_model()

        # Test with numpy array
        fire_array = np.array(
            [
                [0, 0, 0.5, 0.1, 0.01, 0.01, 0, 0, 0],
                [60, 1000, 0.5, 0.2, 0.01, 0.01, 0, 0, 0],
                [120, 2000, 0.5, 0.3, 0.01, 0.01, 0, 0, 0],
            ]
        )

        updated_model = model.update_fire_params(data_table=fire_array)
        assert len(updated_model.fires[0].data_table) == 3
        assert updated_model.fires[0].data_table[0][1] == 0  # HRR at t=0
        assert updated_model.fires[0].data_table[1][1] == 1000  # HRR at t=60
        assert updated_model.fires[0].data_table[2][1] == 2000  # HRR at t=120

        # Test with 2D numpy array of different types
        fire_array_float = np.array(
            [
                [0.0, 0.0, 0.5, 0.1, 0.01, 0.01, 0.0, 0.0, 0.0],
                [60.0, 1000.0, 0.5, 0.2, 0.01, 0.01, 0.0, 0.0, 0.0],
            ]
        )

        updated_model2 = model.update_fire_params(data_table=fire_array_float)
        assert len(updated_model2.fires[0].data_table) == 2
        assert updated_model2.fires[0].data_table[0][1] == 0.0
        assert updated_model2.fires[0].data_table[1][1] == 1000.0

    def test_update_fire_params_with_list(self) -> None:
        """Test update_fire_params with list of lists data_table."""
        model = self.create_full_model()

        # Test with list of lists
        fire_list = [
            [0, 0, 0.5, 0.1, 0.01, 0.01, 0, 0, 0],
            [60, 1000, 0.5, 0.2, 0.01, 0.01, 0, 0, 0],
            [120, 2000, 0.5, 0.3, 0.01, 0.01, 0, 0, 0],
        ]

        updated_model = model.update_fire_params(data_table=fire_list)
        assert len(updated_model.fires[0].data_table) == 3
        assert updated_model.fires[0].data_table[0][1] == 0  # HRR at t=0
        assert updated_model.fires[0].data_table[1][1] == 1000  # HRR at t=60
        assert updated_model.fires[0].data_table[2][1] == 2000  # HRR at t=120

        # Test with mixed types in list
        fire_list_mixed = [
            [0.0, 0, 0.5, 0.1, 0.01, 0.01, 0, 0, 0],
            [60.5, 1000.5, 0.5, 0.2, 0.01, 0.01, 0, 0, 0],
        ]

        updated_model2 = model.update_fire_params(data_table=fire_list_mixed)
        assert len(updated_model2.fires[0].data_table) == 2
        assert updated_model2.fires[0].data_table[0][1] == 0
        assert updated_model2.fires[0].data_table[1][1] == 1000.5

    def test_update_fire_params_errors(self) -> None:
        """Test update_fire_params error handling."""
        model = self.create_minimal_model()  # No fires

        # Test with no fires
        with pytest.raises(ValueError, match="Model has no Fire to update"):
            model.update_fire_params(heat_of_combustion=20000)

        # Test with invalid fire index
        model_with_fire = self.create_full_model()
        with pytest.raises(IndexError, match="Fire index 5 is out of range"):
            model_with_fire.update_fire_params(fire=5, heat_of_combustion=20000)

        # Test with invalid fire ID
        with pytest.raises(ValueError, match="No Fire found with id/fire_id 'INVALID'"):
            model_with_fire.update_fire_params(fire="INVALID", heat_of_combustion=20000)

        # Test with invalid parameter
        with pytest.raises(ValueError, match="Fire has no parameter 'invalid_param'"):
            model_with_fire.update_fire_params(invalid_param=123)

        # Test with invalid data_table type
        with pytest.raises(
            TypeError,
            match="data_table must be a list of lists, dict, NumPy array, pandas DataFrame, or None",
        ):
            model_with_fire.update_fire_params(data_table="invalid")  # type: ignore[arg-type]

    def test_update_simulation_params(self) -> None:
        """Test update_simulation_params method."""
        model = self.create_full_model()
        original_time = model.simulation_environment.time_simulation

        # Test updating simulation parameters
        updated_model = model.update_simulation_params(
            time_simulation=1800, interior_temperature=25.0, print=5
        )

        # Check that original model is unchanged
        assert model.simulation_environment.time_simulation == original_time

        # Check that new model has updated values
        assert updated_model.simulation_environment.time_simulation == 1800
        assert updated_model.simulation_environment.interior_temperature == 25.0
        assert updated_model.simulation_environment.print == 5

    def test_update_simulation_params_errors(self) -> None:
        """Test update_simulation_params error handling."""
        model = self.create_full_model()

        # Test with invalid parameter
        with pytest.raises(
            ValueError, match="Simulation environment has no parameter 'invalid_param'"
        ):
            model.update_simulation_params(invalid_param=123)

    def test_update_compartment_params(self) -> None:
        """Test update_compartment_params method."""
        model = self.create_full_model()
        original_width = model.compartments[0].width

        # Test updating compartment parameters by index
        updated_model = model.update_compartment_params(
            compartment=0, width=5.0, height=3.0
        )

        # Check that original model is unchanged
        assert model.compartments[0].width == original_width

        # Check that new model has updated values
        assert updated_model.compartments[0].width == 5.0
        assert updated_model.compartments[0].height == 3.0

        # Test updating by compartment ID
        updated_model2 = model.update_compartment_params(compartment="ROOM1", depth=6.0)
        assert updated_model2.compartments[0].depth == 6.0

    def test_update_compartment_params_errors(self) -> None:
        """Test update_compartment_params error handling."""
        model = self.create_minimal_model()

        # Test with invalid compartment index
        with pytest.raises(IndexError, match="Compartment index 5 is out of range"):
            model.update_compartment_params(compartment=5, width=5.0)

        # Test with invalid compartment ID
        with pytest.raises(ValueError, match="No Compartment found with id 'INVALID'"):
            model.update_compartment_params(compartment="INVALID", width=5.0)

        # Test with invalid parameter
        with pytest.raises(
            ValueError, match="Compartment has no parameter 'invalid_param'"
        ):
            model.update_compartment_params(invalid_param=123)

    def test_update_material_params(self) -> None:
        """Test update_material_params method."""
        model = self.create_full_model()

        # Test updating material parameters by index
        updated_model = model.update_material_params(material=0, conductivity=1.5)

        # Check that new model has updated values
        assert updated_model.material_properties[0].conductivity == 1.5

        # Test updating by material ID
        updated_model2 = model.update_material_params(material="GYPSUM", density=800)
        assert updated_model2.material_properties[0].density == 800

    def test_update_material_params_errors(self) -> None:
        """Test update_material_params error handling."""
        model = self.create_minimal_model()  # No materials

        # Test with no materials
        with pytest.raises(ValueError, match="Model has no Material to update"):
            model.update_material_params(conductivity=1.5)

    def test_update_wall_vent_params(self) -> None:
        """Test update_wall_vent_params method."""
        model = self.create_full_model()
        original_width = model.wall_vents[0].width

        # Test updating wall vent parameters
        updated_model = model.update_wall_vent_params(vent=0, width=1.5, height=2.2)

        # Check that original model is unchanged
        assert model.wall_vents[0].width == original_width

        # Check that new model has updated values
        assert updated_model.wall_vents[0].width == 1.5
        assert updated_model.wall_vents[0].height == 2.2

    def test_update_ceiling_floor_vent_params(self) -> None:
        """Test update_ceiling_floor_vent_params method."""
        model = self.create_full_model()
        original_area = model.ceiling_floor_vents[0].area

        # Test updating ceiling/floor vent parameters
        updated_model = model.update_ceiling_floor_vent_params(vent=0, area=1.5)

        # Check that original model is unchanged
        assert model.ceiling_floor_vents[0].area == original_area

        # Check that new model has updated values
        assert updated_model.ceiling_floor_vents[0].area == 1.5

    def test_update_mechanical_vent_params(self) -> None:
        """Test update_mechanical_vent_params method."""
        model = self.create_full_model()

        # Test updating mechanical vent parameters
        updated_model = model.update_mechanical_vent_params(vent=0, flow=0.8)

        # Check that new model has updated values
        assert updated_model.mechanical_vents[0].flow == 0.8

    def test_update_device_params(self) -> None:
        """Test update_device_params method."""
        model = self.create_full_model()
        original_setpoint = model.devices[0].setpoint

        # Test updating device parameters
        updated_model = model.update_device_params(device=0, setpoint=80.0)

        # Check that original model is unchanged
        assert model.devices[0].setpoint == original_setpoint

        # Check that new model has updated values
        assert updated_model.devices[0].setpoint == 80.0

    def test_update_surface_connection_params(self) -> None:
        """Test update_surface_connection_params method."""
        model = self.create_full_model()
        original_fraction = model.surface_connections[0].fraction

        # Test updating surface connection parameters (only supports index)
        updated_model = model.update_surface_connection_params(
            connection=0, fraction=0.8
        )

        # Check that original model is unchanged
        assert model.surface_connections[0].fraction == original_fraction

        # Check that new model has updated values
        assert updated_model.surface_connections[0].fraction == 0.8

    def test_method_chaining(self) -> None:
        """Test that update methods can be chained."""
        model = self.create_full_model()

        # Chain multiple updates
        updated_model = (
            model.update_fire_params(heat_of_combustion=25000)
            .update_simulation_params(time_simulation=1800)
            .update_compartment_params(width=5.0)
        )

        # Check all updates were applied
        assert updated_model.fires[0].heat_of_combustion == 25000
        assert updated_model.simulation_environment.time_simulation == 1800
        assert updated_model.compartments[0].width == 5.0

        # Check original model is unchanged
        assert model.fires[0].heat_of_combustion != 25000
        assert model.simulation_environment.time_simulation != 1800
        assert model.compartments[0].width != 5.0

    def test_backward_compatibility(self) -> None:
        """Test that int identifier works as index."""
        model = self.create_full_model()

        updated_model = model.update_fire_params(fire=0, heat_of_combustion=25000)
        assert updated_model.fires[0].heat_of_combustion == 25000

        updated_model2 = model.update_compartment_params(compartment=0, width=5.0)
        assert updated_model2.compartments[0].width == 5.0

    def test_default_selection(self) -> None:
        """Test that methods default to first element when no identifier is provided."""
        model = self.create_full_model()

        # Test fire params default to first fire
        updated_model = model.update_fire_params(heat_of_combustion=25000)
        assert updated_model.fires[0].heat_of_combustion == 25000

        # Test compartment params default to first compartment
        updated_model2 = model.update_compartment_params(width=5.0)
        assert updated_model2.compartments[0].width == 5.0

    def test_add_fire(self) -> None:
        """Test adding a fire to the model."""
        model = self.create_full_model()
        original_fire_count = len(model.fires)

        new_fire = Fire(
            id="FIRE2", comp_id="ROOM1", fire_id="FIRE2", location=[3.0, 3.0]
        )
        updated_model = model.add_fire(new_fire)

        # Check that original model is unchanged
        assert len(model.fires) == original_fire_count

        # Check that new model has additional fire
        assert len(updated_model.fires) == original_fire_count + 1
        assert updated_model.fires[-1].id == "FIRE2"
        assert updated_model.fires[-1].comp_id == "ROOM1"
        assert updated_model.fires[-1].location == [3.0, 3.0]

    def test_add_fire_to_empty_list(self) -> None:
        """Test adding fire when fires list starts empty."""
        model = self.create_full_model()
        # Clear the fires list
        import copy

        new_model = copy.deepcopy(model)
        new_model.fires = []

        new_fire = Fire(
            id="FIRE1", comp_id="ROOM1", fire_id="FIRE1", location=[2.0, 2.0]
        )
        updated_model = new_model.add_fire(new_fire)

        assert len(updated_model.fires) == 1
        assert updated_model.fires[0].id == "FIRE1"

    def test_add_compartment(self) -> None:
        """Test adding a compartment to the model."""
        model = self.create_full_model()
        original_comp_count = len(model.compartments)

        new_room = Compartment(id="ROOM3", width=5.0, depth=4.0, height=3.0)
        updated_model = model.add_compartment(new_room)

        # Check that original model is unchanged
        assert len(model.compartments) == original_comp_count

        # Check that new model has additional compartment
        assert len(updated_model.compartments) == original_comp_count + 1
        assert updated_model.compartments[-1].id == "ROOM3"
        assert updated_model.compartments[-1].width == 5.0

    def test_add_material(self) -> None:
        """Test adding a material to the model."""
        model = self.create_full_model()
        original_mat_count = len(model.material_properties)

        steel = Material(
            id="STEEL",
            material="Steel",
            conductivity=45.0,
            density=7850,
            specific_heat=0.465,
            thickness=0.0015,
        )
        updated_model = model.add_material(steel)

        # Check that original model is unchanged
        assert len(model.material_properties) == original_mat_count

        # Check that new model has additional material
        assert len(updated_model.material_properties) == original_mat_count + 1
        assert updated_model.material_properties[-1].id == "STEEL"
        assert updated_model.material_properties[-1].conductivity == 45.0

    def test_add_wall_vent(self) -> None:
        """Test adding a wall vent to the model."""
        model = self.create_full_model()
        original_vent_count = len(model.wall_vents)

        door = WallVent(id="DOOR2", comps_ids=["ROOM1", "ROOM2"], width=1.0, height=2.0)
        updated_model = model.add_wall_vent(door)

        # Check that original model is unchanged
        assert len(model.wall_vents) == original_vent_count

        # Check that new model has additional wall vent
        assert len(updated_model.wall_vents) == original_vent_count + 1
        assert updated_model.wall_vents[-1].comps_ids == ["ROOM1", "ROOM2"]
        assert updated_model.wall_vents[-1].width == 1.0

    def test_add_ceiling_floor_vent(self) -> None:
        """Test adding a ceiling/floor vent to the model."""
        model = self.create_full_model()
        original_vent_count = len(model.ceiling_floor_vents)

        hatch = CeilingFloorVent(id="HATCH2", comps_ids=["ROOM1", "ROOM2"], area=0.5)
        updated_model = model.add_ceiling_floor_vent(hatch)

        # Check that original model is unchanged
        assert len(model.ceiling_floor_vents) == original_vent_count

        # Check that new model has additional ceiling/floor vent
        assert len(updated_model.ceiling_floor_vents) == original_vent_count + 1
        assert updated_model.ceiling_floor_vents[-1].comps_ids == ["ROOM1", "ROOM2"]
        assert updated_model.ceiling_floor_vents[-1].area == 0.5

    def test_add_mechanical_vent(self) -> None:
        """Test adding a mechanical vent to the model."""
        model = self.create_full_model()
        original_vent_count = len(model.mechanical_vents)

        hvac = MechanicalVent(id="HVAC2", comps_ids=["ROOM1", "OUTSIDE"], flow=0.5)
        updated_model = model.add_mechanical_vent(hvac)

        # Check that original model is unchanged
        assert len(model.mechanical_vents) == original_vent_count

        # Check that new model has additional mechanical vent
        assert len(updated_model.mechanical_vents) == original_vent_count + 1
        assert updated_model.mechanical_vents[-1].comps_ids == ["ROOM1", "OUTSIDE"]
        assert updated_model.mechanical_vents[-1].flow == 0.5

    def test_add_device(self) -> None:
        """Test adding a device to the model."""
        model = self.create_full_model()
        original_device_count = len(model.devices)

        sensor = Device.create_heat_detector(
            id="SENSOR2",
            comp_id="ROOM1",
            location=[2.0, 2.0, 2.4],
            setpoint=68.0,
            rti=50.0,
        )
        updated_model = model.add_device(sensor)

        # Check that original model is unchanged
        assert len(model.devices) == original_device_count

        # Check that new model has additional device
        assert len(updated_model.devices) == original_device_count + 1
        assert updated_model.devices[-1].comp_id == "ROOM1"
        assert updated_model.devices[-1].location == [2.0, 2.0, 2.4]

    def test_add_surface_connection(self) -> None:
        """Test adding a surface connection to the model."""
        model = self.create_full_model()
        original_conn_count = len(model.surface_connections)

        wall_conn = SurfaceConnection.wall_connection(
            comp_id="ROOM1", comp_ids="ROOM2", fraction=0.5
        )
        updated_model = model.add_surface_connection(wall_conn)

        # Check that original model is unchanged
        assert len(model.surface_connections) == original_conn_count

        # Check that new model has additional surface connection
        assert len(updated_model.surface_connections) == original_conn_count + 1
        # Note: comp_ids is stored as a string in SurfaceConnection, not a list
        assert updated_model.surface_connections[-1].comp_id == "ROOM1"
        assert updated_model.surface_connections[-1].comp_ids == "ROOM2"
        assert updated_model.surface_connections[-1].fraction == 0.5

    def test_add_methods_chaining(self) -> None:
        """Test that add methods can be chained together."""
        model = self.create_full_model()

        # Chain multiple add operations
        updated_model = (
            model.add_fire(
                Fire(id="FIRE2", comp_id="ROOM1", fire_id="FIRE2", location=[3.0, 3.0])
            )
            .add_compartment(Compartment(id="ROOM3", width=5.0, depth=4.0, height=3.0))
            .add_material(
                Material(
                    id="STEEL",
                    material="Steel",
                    conductivity=45.0,
                    density=7850,
                    specific_heat=0.465,
                    thickness=0.0015,
                )
            )
        )

        # Verify all components were added
        assert len(updated_model.fires) == len(model.fires) + 1
        assert len(updated_model.compartments) == len(model.compartments) + 1
        assert (
            len(updated_model.material_properties) == len(model.material_properties) + 1
        )

        # Verify original model unchanged
        assert len(model.fires) == 1  # Original count
        assert len(model.compartments) == 2  # Original count
        assert (
            len(model.material_properties) == 1
        )  # Original count from create_full_model

    def test_add_methods_with_none_lists(self) -> None:
        """Test add methods when component lists are None."""
        # Create minimal model with only required components
        simulation_env = SimulationEnvironment(title="Test", time_simulation=1000)
        room = Compartment(id="ROOM1", width=3.0, depth=3.0, height=2.5)

        model = CFASTModel(
            simulation_environment=simulation_env,
            compartments=[room],
            fires=None,
            devices=None,
            material_properties=None,
            surface_connections=None,
        )

        # Test adding to None lists
        fire = Fire(id="FIRE1", comp_id="ROOM1", fire_id="FIRE1", location=[1.0, 1.0])
        device = Device.create_heat_detector(
            id="SENSOR1",
            comp_id="ROOM1",
            location=[2.0, 2.0, 2.4],
            setpoint=68.0,
            rti=50.0,
        )
        material = Material(
            id="CONCRETE",
            material="Concrete",
            conductivity=1.4,
            density=2300,
            specific_heat=0.88,
            thickness=0.15,
        )

        updated_model = model.add_fire(fire).add_device(device).add_material(material)

        assert len(updated_model.fires) == 1
        assert len(updated_model.devices) == 1
        assert len(updated_model.material_properties) == 1

    def test_update_fire_params_default_first_fire(self) -> None:
        """Test update_fire_params with no fire identifier (should update first fire)."""
        model = self.create_full_model()

        # Test default behavior (updates first fire)
        updated_model = model.update_fire_params(heat_of_combustion=23000)
        assert updated_model.fires[0].heat_of_combustion == 23000

    def test_update_simulation_params_missing_environment(self) -> None:
        """Test update_simulation_params with missing simulation environment."""
        model = self.create_minimal_model()
        # Simulate missing simulation environment by deleting it
        delattr(model, "simulation_environment")

        with pytest.raises(
            ValueError, match="Model has no simulation_environment object"
        ):
            model.update_simulation_params(time_simulation=1000)

    def test_update_compartment_params_default_first_compartment(self) -> None:
        """Test update_compartment_params with no compartment identifier."""
        model = self.create_full_model()

        # Test default behavior (updates first compartment)
        updated_model = model.update_compartment_params(height=3.5)
        assert updated_model.compartments[0].height == 3.5

    def test_update_material_params_default_first_material(self) -> None:
        """Test update_material_params with no material identifier."""
        model = self.create_full_model()

        # Test default behavior (updates first material)
        updated_model = model.update_material_params(density=2500)
        assert updated_model.material_properties[0].density == 2500

    def test_update_wall_vent_params_default_first_vent(self) -> None:
        """Test update_wall_vent_params with no vent identifier."""
        model = self.create_full_model()

        # Test default behavior (updates first vent)
        updated_model = model.update_wall_vent_params(height=2.3)
        assert updated_model.wall_vents[0].height == 2.3

    def test_update_ceiling_floor_vent_params_default_first_vent(self) -> None:
        """Test update_ceiling_floor_vent_params with no vent identifier."""
        model = self.create_full_model()

        # Test default behavior (updates first vent)
        updated_model = model.update_ceiling_floor_vent_params(area=1.4)
        assert updated_model.ceiling_floor_vents[0].area == 1.4

    def test_update_mechanical_vent_params_default_first_vent(self) -> None:
        """Test update_mechanical_vent_params with no vent identifier."""
        model = self.create_full_model()

        # Test default behavior (updates first vent)
        updated_model = model.update_mechanical_vent_params(flow=0.9)
        assert updated_model.mechanical_vents[0].flow == 0.9

    def test_update_device_params_default_first_device(self) -> None:
        """Test update_device_params with no device identifier."""
        model = self.create_full_model()

        # Test default behavior (updates first device)
        updated_model = model.update_device_params(setpoint=85.0)
        assert updated_model.devices[0].setpoint == 85.0

    def test_update_methods_with_empty_lists(self) -> None:
        """Test update methods error handling when component lists are empty."""
        model = self.create_minimal_model()

        # Test updating non-existent components
        with pytest.raises(ValueError, match="Model has no Wall vent to update"):
            model.update_wall_vent_params(width=1.0)

        with pytest.raises(
            ValueError, match="Model has no Ceiling/floor vent to update"
        ):
            model.update_ceiling_floor_vent_params(area=1.0)

        with pytest.raises(ValueError, match="Model has no Mechanical vent to update"):
            model.update_mechanical_vent_params(flow=1.0)

        with pytest.raises(ValueError, match="Model has no Device to update"):
            model.update_device_params(setpoint=70.0)

        with pytest.raises(
            ValueError, match="Model has no Surface connection to update"
        ):
            model.update_surface_connection_params(fraction=0.5)

    def test_update_methods_invalid_parameters(self) -> None:
        """Test update methods with invalid parameter names."""
        model = self.create_full_model()

        # Test invalid parameters for each update method
        with pytest.raises(
            ValueError, match="Compartment has no parameter 'invalid_attribute'"
        ):
            model.update_compartment_params(invalid_attribute=123)

        with pytest.raises(
            ValueError, match="Material has no parameter 'invalid_attribute'"
        ):
            model.update_material_params(invalid_attribute=123)

        with pytest.raises(
            ValueError, match="Wall vent has no parameter 'invalid_attribute'"
        ):
            model.update_wall_vent_params(invalid_attribute=123)

        with pytest.raises(
            ValueError, match="Ceiling/floor vent has no parameter 'invalid_attribute'"
        ):
            model.update_ceiling_floor_vent_params(invalid_attribute=123)

        with pytest.raises(
            ValueError, match="Mechanical vent has no parameter 'invalid_attribute'"
        ):
            model.update_mechanical_vent_params(invalid_attribute=123)

        with pytest.raises(
            ValueError, match="Device has no parameter 'invalid_attribute'"
        ):
            model.update_device_params(invalid_attribute=123)

        with pytest.raises(
            ValueError, match="Surface connection has no parameter 'invalid_attribute'"
        ):
            model.update_surface_connection_params(invalid_attribute=123)

    def test_identifier_resolution(self) -> None:
        """Test identifier resolution (int index and string id) via public methods."""
        model = self.create_full_model()

        # Index and string id both resolve to the same component (verified via id)
        assert model.update_fire_params(fire=0).fires[0].id == model.fires[0].id
        assert model.update_fire_params(fire="FIRE1").fires[0].id == model.fires[0].id
        assert (
            model.update_compartment_params(compartment="ROOM1").compartments[0].id
            == model.compartments[0].id
        )
        assert (
            model.update_material_params(material="GYPSUM").material_properties[0].id
            == model.material_properties[0].id
        )
        assert (
            model.update_wall_vent_params(vent="DOOR1").wall_vents[0].id
            == model.wall_vents[0].id
        )
        assert (
            model.update_ceiling_floor_vent_params(vent="CEILING1")
            .ceiling_floor_vents[0]
            .id
            == model.ceiling_floor_vents[0].id
        )
        assert (
            model.update_mechanical_vent_params(vent="FAN1").mechanical_vents[0].id
            == model.mechanical_vents[0].id
        )
        assert (
            model.update_device_params(device="TEMP1").devices[0].id
            == model.devices[0].id
        )

        # Unknown string id raises ValueError
        with pytest.raises(
            ValueError, match="No Fire found with id/fire_id 'NONEXISTENT'"
        ):
            model.update_fire_params(fire="NONEXISTENT", heat_of_combustion=1)
        with pytest.raises(
            ValueError, match="No Compartment found with id 'NONEXISTENT'"
        ):
            model.update_compartment_params(compartment="NONEXISTENT", width=1.0)
        with pytest.raises(ValueError, match="No Material found with id"):
            model.update_material_params(material="NONEXISTENT", conductivity=1.0)
        with pytest.raises(
            ValueError, match="No Wall vent found with id 'NONEXISTENT'"
        ):
            model.update_wall_vent_params(vent="NONEXISTENT", width=1.0)
        with pytest.raises(
            ValueError, match="No Ceiling/floor vent found with id 'NONEXISTENT'"
        ):
            model.update_ceiling_floor_vent_params(vent="NONEXISTENT", area=1.0)
        with pytest.raises(
            ValueError, match="No Mechanical vent found with id 'NONEXISTENT'"
        ):
            model.update_mechanical_vent_params(vent="NONEXISTENT", flow=1.0)
        with pytest.raises(ValueError, match="No Device found with id 'NONEXISTENT'"):
            model.update_device_params(device="NONEXISTENT", setpoint=70.0)

        # Wrong type raises TypeError
        with pytest.raises(TypeError, match="Fire identifier must be int or str"):
            model.update_fire_params(fire=3.14, heat_of_combustion=1)  # type: ignore
        with pytest.raises(
            TypeError, match="Compartment identifier must be int or str"
        ):
            model.update_compartment_params(compartment=3.14, width=1.0)  # type: ignore

    def test_save_method_with_custom_filename(self) -> None:
        """Test save method with custom filename."""
        model = self.create_minimal_model()

        with tempfile.TemporaryDirectory() as temp_dir:
            custom_path = os.path.join(temp_dir, "custom_model.in")
            result_path = model.save(custom_path)

            # Verify file was created
            assert os.path.exists(custom_path)
            assert result_path == os.path.abspath(custom_path)

            # Verify file has content
            with open(custom_path) as f:
                content = f.read()
                assert "Test Simulation" in content  # Title should be in the file


class TestCFASTModelValidateDependencies:
    """Test _validate_dependencies cross-component constraints."""

    @pytest.fixture()
    def sim_env(self):
        return SimulationEnvironment(title="Test")

    @pytest.fixture()
    def room1(self):
        return Compartment(id="ROOM1", width=3.0, depth=4.0, height=2.4)

    @pytest.fixture()
    def room2(self):
        return Compartment(id="ROOM2", width=3.0, depth=4.0, height=2.4)

    def _make(self, sim_env, compartments, **kwargs):
        return CFASTModel(
            simulation_environment=sim_env,
            compartments=compartments,
            **kwargs,
        )

    def test_too_many_compartments(self, sim_env):
        """Test that more than 100 compartments raises ValueError."""
        compartments = [Compartment(id=f"ROOM{i}") for i in range(101)]
        with pytest.raises(ValueError, match="maximum of 100 compartments"):
            self._make(sim_env, compartments)

    def test_duplicate_compartment_ids(self, sim_env):
        """Test that duplicate compartment IDs raises ValueError."""
        with pytest.raises(ValueError, match="Duplicate id 'ROOM1'"):
            self._make(sim_env, [Compartment(id="ROOM1"), Compartment(id="ROOM1")])

    def test_duplicate_fire_ids(self, sim_env, room1):
        """Test that duplicate fire IDs raises ValueError."""
        fire = Fire(id="FIRE1", comp_id="ROOM1", fire_id="PU", location=[1.0, 1.0])
        fire_dup = Fire(id="FIRE1", comp_id="ROOM1", fire_id="PU", location=[2.0, 2.0])
        with pytest.raises(ValueError, match="Duplicate id 'FIRE1'"):
            self._make(sim_env, [room1], fires=[fire, fire_dup])

    def test_duplicate_device_ids(self, sim_env, room1):
        """Test that duplicate device IDs raises ValueError."""
        dev1 = Device.create_heat_detector("HD1", "ROOM1", [1.0, 2.0, 1.5], 70.0, 50.0)
        dev2 = Device.create_heat_detector("HD1", "ROOM1", [2.0, 2.0, 1.5], 70.0, 50.0)
        with pytest.raises(ValueError, match="Duplicate id 'HD1'"):
            self._make(sim_env, [room1], devices=[dev1, dev2])

    def test_duplicate_material_ids(self, sim_env, room1):
        """Test that duplicate material IDs raises ValueError."""
        mat = Material(
            id="GYPSUM",
            material="Gypsum Board",
            conductivity=0.17,
            density=790,
            specific_heat=0.9,
            thickness=0.016,
        )
        mat_dup = Material(
            id="GYPSUM",
            material="Gypsum Board",
            conductivity=0.17,
            density=790,
            specific_heat=0.9,
            thickness=0.016,
        )
        with pytest.raises(ValueError, match="Duplicate id 'GYPSUM'"):
            self._make(sim_env, [room1], material_properties=[mat, mat_dup])

    @pytest.mark.parametrize(
        ("component_type", "component"),
        [
            pytest.param(
                "fires",
                Fire(id="F1", comp_id="UNKNOWN", fire_id="PU", location=[1.0, 1.0]),
                id="fire",
            ),
            pytest.param(
                "devices",
                Device.create_heat_detector(
                    "HD1", "UNKNOWN", [1.0, 2.0, 1.5], 70.0, 50.0
                ),
                id="device",
            ),
        ],
    )
    def test_undefined_comp_id(self, sim_env, room1, component_type, component):
        """Test that a fire or device referencing an undefined compartment raises ValueError."""
        with pytest.raises(ValueError, match="comp_id='UNKNOWN' does not match"):
            self._make(sim_env, [room1], **{component_type: [component]})

    def test_wall_vent_undefined_first_comp(self, sim_env, room1):
        """Test that WallVent with undefined first compartment raises ValueError."""
        vent = WallVent(
            id="V1",
            comps_ids=["UNKNOWN", "ROOM1"],
            bottom=0,
            height=2,
            width=1,
            face="RIGHT",
            offset=0,
        )
        with pytest.raises(
            ValueError, match=r"comps_ids\[0\]='UNKNOWN' does not match"
        ):
            self._make(sim_env, [room1], wall_vents=[vent])

    def test_wall_vent_undefined_second_comp(self, sim_env, room1):
        """Test that WallVent with undefined second compartment raises ValueError."""
        vent = WallVent(
            id="V1",
            comps_ids=["ROOM1", "UNKNOWN"],
            bottom=0,
            height=2,
            width=1,
            face="RIGHT",
            offset=0,
        )
        with pytest.raises(
            ValueError, match=r"comps_ids\[1\]='UNKNOWN' does not match"
        ):
            self._make(sim_env, [room1], wall_vents=[vent])

    def test_wall_vent_outside_second_comp_is_valid(self, sim_env, room1):
        """Test that OUTSIDE as second compartment in WallVent is accepted."""
        vent = WallVent(
            id="V1",
            comps_ids=["ROOM1", "OUTSIDE"],
            bottom=0,
            height=2,
            width=1,
            face="RIGHT",
            offset=0,
        )
        model = self._make(sim_env, [room1], wall_vents=[vent])
        assert len(model.wall_vents) == 1

    @pytest.mark.parametrize(
        ("vent_type", "vent"),
        [
            pytest.param(
                "ceiling_floor_vents",
                CeilingFloorVent(id="V1", comps_ids=["ROOM1", "UNKNOWN"], area=1.0),
                id="ceiling-floor-vent",
            ),
            pytest.param(
                "mechanical_vents",
                MechanicalVent(
                    id="V1", comps_ids=["ROOM1", "UNKNOWN"], offsets=[0.0, 0.0]
                ),
                id="mechanical-vent",
            ),
        ],
    )
    def test_vent_undefined_comp_ids(self, sim_env, room1, vent_type, vent):
        """Test that ceiling/floor and mechanical vents with undefined compartment raise ValueError."""
        with pytest.raises(ValueError, match="does not match any defined compartment"):
            self._make(sim_env, [room1], **{vent_type: [vent]})

    def test_surface_connection_undefined_comp_id(self, sim_env, room1):
        """Test that SurfaceConnection with undefined comp_id raises ValueError."""
        sc = SurfaceConnection.wall_connection("UNKNOWN", "ROOM1", fraction=0.5)
        with pytest.raises(ValueError, match="comp_id='UNKNOWN' does not match"):
            self._make(sim_env, [room1], surface_connections=[sc])

    def test_surface_connection_undefined_comp_ids(self, sim_env, room1):
        """Test that SurfaceConnection with undefined comp_ids raises ValueError."""
        sc = SurfaceConnection.wall_connection("ROOM1", "UNKNOWN", fraction=0.5)
        with pytest.raises(ValueError, match="comp_ids='UNKNOWN' does not match"):
            self._make(sim_env, [room1], surface_connections=[sc])

    def test_device_undefined_material_id(self, sim_env, room1):
        """Test that a device referencing an undefined material raises ValueError."""
        device = Device(
            id="T1",
            comp_id="ROOM1",
            location=[1.0, 2.0, 1.5],
            type="PLATE",
            material_id="UNKNOWN",
            surface_orientation="CEILING",
        )
        with pytest.raises(ValueError, match="material_id='UNKNOWN' does not match"):
            self._make(sim_env, [room1], devices=[device])

    def test_device_temperature_depth_exceeds_material_thickness(self, sim_env, room1):
        """Test that temperature_depth >= material thickness raises ValueError."""
        mat = Material(
            id="STEEL",
            material="Steel",
            conductivity=45.8,
            density=7850,
            specific_heat=0.46,
            thickness=0.01,
        )
        device = Device(
            id="T1",
            comp_id="ROOM1",
            location=[1.0, 2.0, 1.5],
            type="PLATE",
            material_id="STEEL",
            surface_orientation="CEILING",
            depth_units="M",
            temperature_depth=0.02,
        )
        with pytest.raises(
            ValueError, match="temperature_depth=0.02 m must be less than"
        ):
            self._make(sim_env, [room1], devices=[device], material_properties=[mat])

    def test_device_temperature_depth_valid_meters(self, sim_env, room1):
        """Test that temperature_depth < material thickness is valid."""
        mat = Material(
            id="STEEL",
            material="Steel",
            conductivity=45.8,
            density=7850,
            specific_heat=0.46,
            thickness=0.01,
        )
        device = Device(
            id="T1",
            comp_id="ROOM1",
            location=[1.0, 2.0, 1.5],
            type="PLATE",
            material_id="STEEL",
            surface_orientation="CEILING",
            depth_units="M",
            temperature_depth=0.005,
        )
        model = self._make(
            sim_env, [room1], devices=[device], material_properties=[mat]
        )
        assert model.devices[0].temperature_depth == 0.005

    @pytest.mark.parametrize(
        "mat_attr", ["ceiling_mat_id", "wall_mat_id", "floor_mat_id"]
    )
    def test_compartment_undefined_material_id(self, sim_env, mat_attr):
        """Test that a compartment referencing an undefined material raises ValueError."""
        comp = Compartment(id="ROOM1", **{mat_attr: "UNKNOWN"})  # type: ignore
        with pytest.raises(ValueError, match=f"{mat_attr}='UNKNOWN' does not match"):
            self._make(sim_env, [comp])

    def test_fire_undefined_device_id(self, sim_env, room1):
        """Test that a fire referencing an undefined device raises ValueError."""
        fire = Fire(
            id="F1",
            comp_id="ROOM1",
            fire_id="PU",
            location=[1.0, 1.0],
            device_id="UNKNOWN",
        )
        with pytest.raises(ValueError, match="device_id='UNKNOWN' does not match"):
            self._make(sim_env, [room1], fires=[fire])

    @pytest.mark.parametrize(
        ("vent_type", "vent"),
        [
            pytest.param(
                "wall_vents",
                WallVent(
                    id="V1",
                    comps_ids=["ROOM1", "ROOM2"],
                    bottom=0,
                    height=2,
                    width=1,
                    face="RIGHT",
                    offset=0,
                    open_close_criterion="TEMPERATURE",
                    set_point=100.0,
                    device_id="UNKNOWN",
                ),
                id="wall-vent",
            ),
            pytest.param(
                "ceiling_floor_vents",
                CeilingFloorVent(
                    id="V1",
                    comps_ids=["ROOM1", "ROOM2"],
                    area=1.0,
                    open_close_criterion="TEMPERATURE",
                    set_point=70.0,
                    device_id="UNKNOWN",
                ),
                id="ceiling-floor-vent",
            ),
            pytest.param(
                "mechanical_vents",
                MechanicalVent(
                    id="V1",
                    comps_ids=["ROOM1", "ROOM2"],
                    offsets=[0.0, 0.0],
                    open_close_criterion="TEMPERATURE",
                    device_id="UNKNOWN",
                ),
                id="mechanical-vent",
            ),
        ],
    )
    def test_vent_undefined_device_id(self, sim_env, room1, room2, vent_type, vent):
        """Test that a vent referencing an undefined device raises ValueError."""
        with pytest.raises(ValueError, match="device_id='UNKNOWN' does not match"):
            self._make(sim_env, [room1, room2], **{vent_type: [vent]})

    def test_fire_location_outside_compartment_warning(self, sim_env, room1):
        """Test that a fire outside compartment bounds raises UserWarning."""
        fire = Fire(
            id="F1",
            comp_id="ROOM1",
            fire_id="PU",
            location=[10.0, 10.0],  # ROOM1 is 3x4
        )
        with pytest.warns(UserWarning, match="location=.* is outside compartment"):
            self._make(sim_env, [room1], fires=[fire])

    def test_device_location_outside_compartment_warning(self, sim_env, room1):
        """Test that a device outside compartment bounds raises UserWarning."""
        device = Device.create_heat_detector(
            "HD1",
            "ROOM1",
            [10.0, 10.0, 10.0],
            70.0,
            50.0,  # ROOM1 is 3x4x2.4
        )
        with pytest.warns(UserWarning, match="location=.* is outside compartment"):
            self._make(sim_env, [room1], devices=[device])
