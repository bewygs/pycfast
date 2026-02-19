from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, mock_open, patch

import pytest

from pycfast.parsers import (
    CFASTParser,
    parse_cfast_file,
    sanitize_cfast_title_and_material,
)

"""
Tests for the CFAST parser module.
"""


class TestCFASTParser:
    """Test class for CFASTParser."""

    def test_init(self):
        """Test parser initialization."""
        parser = CFASTParser()
        assert parser.simulation_environment.title == ""
        assert parser.material_properties == []
        assert parser.compartments == []
        assert parser.wall_vents == []
        assert parser.ceiling_floor_vents == []
        assert parser.mechanical_vents == []
        assert parser.fires == []
        assert parser.devices == []
        assert parser.surface_connections == []
        assert parser._fire_hash_map == {}

    def test_reset(self):
        """Test parser reset functionality."""
        parser = CFASTParser()
        # Modify some parser state
        parser.simulation_environment.title = "Test"
        parser.material_properties.append(Mock())
        parser._fire_hash_map["test"] = Mock()

        # Reset should clear everything
        parser.reset()
        assert parser.simulation_environment.title == ""
        assert parser.material_properties == []
        assert parser.compartments == []
        assert parser.wall_vents == []
        assert parser.ceiling_floor_vents == []
        assert parser.mechanical_vents == []
        assert parser.fires == []
        assert parser.devices == []
        assert parser.surface_connections == []
        assert parser._fire_hash_map == {}

    def test_parse_file_not_found(self):
        """Test parsing a non-existent file."""
        parser = CFASTParser()
        with pytest.raises(FileNotFoundError, match="Input file not found"):
            parser.parse_file("nonexistent_file.in")

    def test_parse_file_minimal(self):
        """Test parsing a minimal CFAST file."""
        minimal_content = """&HEAD VERSION = 7600, TITLE = 'Test Simulation' /
                             &TIME SIMULATION = 900 /
                             &COMP ID = 'Room1', DEPTH = 5, HEIGHT = 3, WIDTH = 4, ORIGIN = 0, 0, 0 /
                             &TAIL /"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".in", delete=False) as f:
            f.write(minimal_content)
            temp_file = f.name

        try:
            parser = CFASTParser()
            model = parser.parse_file(temp_file)

            assert model.simulation_environment.title == "Test Simulation"
            assert model.simulation_environment.time_simulation == 900
            assert len(model.compartments) == 1
            assert model.compartments[0].id == "Room1"
            assert model.compartments[0].width == 4.0
            assert model.compartments[0].depth == 5.0
            assert model.compartments[0].height == 3.0
            assert model.file_name == Path(temp_file).stem + "_parsed" + ".in"
        finally:
            os.unlink(temp_file)

    def test_parse_file_with_materials(self):
        """Test parsing a file with material properties."""
        content_with_materials = """&HEAD VERSION = 7600, TITLE = 'Material Test' /
                                    &TIME SIMULATION = 900 /
                                    &MATL ID = 'GYPSUM', MATERIAL = 'Gypsum Board', CONDUCTIVITY = 0.17, DENSITY = 930, SPECIFIC_HEAT = 1.09, THICKNESS = 0.016, EMISSIVITY = 0.9 /
                                    &COMP ID = 'Room1', DEPTH = 5, HEIGHT = 3, WIDTH = 4, ORIGIN = 0, 0, 0 /
                                    &TAIL /"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".in", delete=False) as f:
            f.write(content_with_materials)
            temp_file = f.name

        try:
            parser = CFASTParser()
            model = parser.parse_file(temp_file)

            assert len(model.material_properties) == 1
            mat = model.material_properties[0]
            assert mat.id == "GYPSUM"
            assert mat.material == "Gypsum Board"
            assert mat.conductivity == 0.17
            assert mat.density == 930
            assert mat.specific_heat == 1.09
            assert mat.thickness == 0.016
            assert mat.emissivity == 0.9
        finally:
            os.unlink(temp_file)

    def test_parse_file_with_fire(self):
        """Test parsing a file with fire data."""
        content_with_fire = """&HEAD VERSION = 7600, TITLE = 'Fire Test' /
                               &TIME SIMULATION = 900 /
                               &COMP ID = 'Room1', DEPTH = 5, HEIGHT = 3, WIDTH = 4, ORIGIN = 0, 0, 0 /
                               &FIRE ID = 'Fire1', COMP_ID = 'Room1', FIRE_ID = 'TestFire', LOCATION = 2.5, 2.5 /
                               &CHEM ID = 'TestFire' CARBON = 1 HYDROGEN = 4 OXYGEN = 0 NITROGEN = 0 CHLORINE = 0 HEAT_OF_COMBUSTION = 50000 RADIATIVE_FRACTION = 0.35 /
                               &TABL ID = 'TestFire' LABELS = 'TIME', 'HRR' /
                               &TABL ID = 'TestFire', DATA = 0, 100 /
                               &TAIL /"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".in", delete=False) as f:
            f.write(content_with_fire)
            temp_file = f.name

        try:
            parser = CFASTParser()
            model = parser.parse_file(temp_file)

            assert len(model.fires) == 1
            fire = model.fires[0]
            assert fire.id == "Fire1"
            assert fire.comp_id == "Room1"
            assert fire.fire_id == "TestFire"
            assert fire.location == [2.5, 2.5]
            assert fire.carbon == 1
            assert fire.hydrogen == 4
            assert fire.oxygen == 0
            assert fire.heat_of_combustion == 50000
        finally:
            os.unlink(temp_file)

    def test_parse_file_with_diag_block(self):
        """Test parsing a file with DIAG block."""
        content_with_diag = """&HEAD VERSION = 7600, TITLE = 'DIAG Test' /
                               &TIME SIMULATION = 900 /
                               &DIAG RESIDUE = .TRUE. /
                               &COMP ID = 'Room1', DEPTH = 5, HEIGHT = 3, WIDTH = 4, ORIGIN = 0, 0, 0 /
                               &TAIL /"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".in", delete=False) as f:
            f.write(content_with_diag)
            temp_file = f.name

        try:
            parser = CFASTParser()
            model = parser.parse_file(temp_file)

            assert model.simulation_environment.extra_custom is not None
            assert "&DIAG RESIDUE = .TRUE." in model.simulation_environment.extra_custom
        finally:
            os.unlink(temp_file)

    def test_parse_file_with_unknown_block(self):
        """Test parsing a file with unknown block type (should warn but not fail)."""
        content_with_unknown = """&HEAD VERSION = 7600, TITLE = 'Unknown Block Test' /
                                  &TIME SIMULATION = 900 /
                                  &UNKNOWN_BLOCK PARAM = 'value' /
                                  &COMP ID = 'Room1', DEPTH = 5, HEIGHT = 3, WIDTH = 4, ORIGIN = 0, 0, 0 /
                                  &TAIL /"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".in", delete=False) as f:
            f.write(content_with_unknown)
            temp_file = f.name

        try:
            parser = CFASTParser()
            # This should not raise an exception, just print a warning
            model = parser.parse_file(temp_file)
            assert model.simulation_environment.title == "Unknown Block Test"
        finally:
            os.unlink(temp_file)

    def test_clean_content(self):
        """Test content cleaning functionality."""
        parser = CFASTParser()
        content = """!! This is a comment
                     &HEAD VERSION = 7600, TITLE = 'Test' /

                     !! Another comment
                     &TIME SIMULATION = 900 PRINT = 50 /"""

        cleaned = parser._clean_content(content)

        # Should have removed comments and joined multiline blocks
        assert "!! This is a comment" not in cleaned
        assert "&HEAD VERSION = 7600, TITLE = 'Test' /" in cleaned
        assert "&TIME SIMULATION = 900 PRINT = 50 /" in cleaned

    def test_clean_content_file_ends_in_block(self):
        """Test content cleaning when file ends inside a block."""
        parser = CFASTParser()
        content = """&HEAD VERSION = 7600,
                     TITLE = 'Test'"""  # No closing /

        cleaned = parser._clean_content(content)
        assert "&HEAD VERSION = 7600, TITLE = 'Test'" in cleaned

    def test_clean_content_complex_multiline(self):
        """Test content cleaning with complex multiline scenarios."""
        parser = CFASTParser()
        content = """&COMP ID = 'Room1',
                     WIDTH = 4.0,
                     HEIGHT = 3.0,
                     DEPTH = 5.0 /
                     !! Comment between blocks
                     &MATL ID = 'STEEL',
                     CONDUCTIVITY = 45.0 /"""

        cleaned = parser._clean_content(content)
        lines = cleaned.split("\n")

        # Should have two joined blocks
        comp_line = next(
            (line for line in lines if line.strip().startswith("&COMP")), None
        )
        matl_line = next(
            (line for line in lines if line.strip().startswith("&MATL")), None
        )

        assert comp_line is not None
        assert matl_line is not None
        assert "WIDTH = 4.0" in comp_line
        assert "CONDUCTIVITY = 45.0" in matl_line

    def test_get_param(self):
        """Test parameter retrieval helper."""
        parser = CFASTParser()
        params = {"EXISTING": "value", "NUMBER": 42}

        # Test existing parameter
        assert parser._get_param(params, "EXISTING") == "value"

        # Test default value
        assert parser._get_param(params, "MISSING", "default") == "default"

        # Test required parameter that exists
        assert parser._get_param(params, "EXISTING", required=True) == "value"

        # Test required parameter that's missing
        with pytest.raises(ValueError, match="Missing required parameter"):
            parser._get_param(params, "MISSING", required=True)

        # Test type conversion
        assert parser._get_param(params, "NUMBER", param_type=str) == "42"

    def test_get_param_type_conversion_error(self):
        """Test parameter type conversion errors."""
        parser = CFASTParser()
        params = {"INVALID": "not_a_number"}

        with pytest.raises(
            ValueError, match="Parameter INVALID could not be converted"
        ):
            parser._get_param(params, "INVALID", param_type=int)

    def test_normalize_comp_ids(self):
        """Test compartment ID normalization."""
        # Test string input
        result = CFASTParser._normalize_comp_ids("COMP1")
        assert result == ["COMP1"]

        # Test list input
        result = CFASTParser._normalize_comp_ids(["COMP1", "COMP2"])
        assert result == ["COMP1", "COMP2"]

        # Test None input
        result = CFASTParser._normalize_comp_ids(None)
        assert result == []

        # Test tuple input
        result = CFASTParser._normalize_comp_ids(("COMP1", "COMP2"))
        assert result == ["COMP1", "COMP2"]

    def test_extract_params(self):
        """Test parameter extraction with mapping."""
        parser = CFASTParser()
        params = {"ID": "test", "WIDTH": "1.5", "ACTIVE": ".TRUE."}

        param_map = {
            "id": {"source": "ID", "required": True, "type": str},
            "width": {"source": "WIDTH", "required": True, "type": float},
            "active": {"source": "ACTIVE", "default": False, "type": bool},
        }

        result = parser._extract_params(params, param_map)

        assert result["id"] == "test"
        assert result["width"] == 1.5
        assert result["active"] is True

    def test_extract_params_with_transform(self):
        """Test parameter extraction with transformation function."""
        parser = CFASTParser()
        params = {"COORDS": [1, 2, 3]}

        def transform_coords(coords):
            return tuple(coords)

        param_map = {"coordinates": {"source": "COORDS", "transform": transform_coords}}

        result = parser._extract_params(params, param_map)
        assert result["coordinates"] == (1, 2, 3)

    def test_extract_params_transform_error(self):
        """Test parameter extraction with transform function that fails."""
        parser = CFASTParser()
        params = {"VALUE": "invalid"}

        def failing_transform(value):
            raise ValueError("Transform failed")

        param_map = {"value": {"source": "VALUE", "transform": failing_transform}}

        with pytest.raises(ValueError, match="Failed to transform parameter VALUE"):
            parser._extract_params(params, param_map)

    def test_extract_params_default_source(self):
        """Test parameter extraction with default source name."""
        parser = CFASTParser()
        params = {"WIDTH": 1.5}

        param_map = {
            "width": {"type": float}  # No source specified, should default to 'WIDTH'
        }

        result = parser._extract_params(params, param_map)
        assert result["width"] == 1.5

    def test_parse_head_block(self):
        """Test HEAD block parsing."""
        parser = CFASTParser()
        params = {"TITLE": "Test Simulation"}

        parser._parse_head_block(params)

        assert parser.simulation_environment.title == "Test Simulation"

    def test_parse_head_block_no_title(self):
        """Test HEAD block parsing without TITLE."""
        parser = CFASTParser()
        params = {"VERSION": 7600}

        parser._parse_head_block(params)

        # Title should remain empty string
        assert parser.simulation_environment.title == ""

    def test_parse_time_block(self):
        """Test TIME block parsing."""
        parser = CFASTParser()
        params = {"SIMULATION": 900, "PRINT": 50, "SMOKEVIEW": 10, "SPREADSHEET": 20}

        parser._parse_time_block(params)

        assert parser.simulation_environment.time_simulation == 900
        assert parser.simulation_environment.print == 50
        assert parser.simulation_environment.smokeview == 10
        assert parser.simulation_environment.spreadsheet == 20

    def test_parse_init_block(self):
        """Test INIT block parsing."""
        parser = CFASTParser()
        params = {
            "PRESSURE": 101325,
            "RELATIVE_HUMIDITY": 50,
            "INTERIOR_TEMPERATURE": 20,
            "EXTERIOR_TEMPERATURE": 15,
        }

        parser._parse_init_block(params)

        assert parser.simulation_environment.init_pressure == 101325
        assert parser.simulation_environment.relative_humidity == 50
        assert parser.simulation_environment.interior_temperature == 20
        assert parser.simulation_environment.exterior_temperature == 15

    def test_parse_misc_block(self):
        """Test MISC block parsing."""
        parser = CFASTParser()
        params = {"ADIABATIC": True, "MAX_TIME_STEP": 0.1, "LOWER_OXYGEN_LIMIT": 0.15}

        parser._parse_misc_block(params)

        assert parser.simulation_environment.adiabatic is True
        assert parser.simulation_environment.max_time_step == 0.1
        assert parser.simulation_environment.lower_oxygen_limit == 0.15

    def test_parse_material_block(self):
        """Test MATL block parsing."""
        parser = CFASTParser()
        params = {
            "ID": "GYPSUM",
            "MATERIAL": "Gypsum Board",
            "CONDUCTIVITY": 0.17,
            "DENSITY": 930,
            "SPECIFIC_HEAT": 1.09,
            "THICKNESS": 0.016,
            "EMISSIVITY": 0.9,
        }

        parser._parse_material_block(params)

        assert len(parser.material_properties) == 1
        mat = parser.material_properties[0]
        assert mat.id == "GYPSUM"
        assert mat.material == "Gypsum Board"
        assert mat.conductivity == 0.17
        assert mat.density == 930
        assert mat.specific_heat == 1.09
        assert mat.thickness == 0.016
        assert mat.emissivity == 0.9

    def test_parse_compartment_block(self):
        """Test COMP block parsing."""
        parser = CFASTParser()
        params = {
            "ID": "Room1",
            "WIDTH": 4.0,
            "DEPTH": 5.0,
            "HEIGHT": 3.0,
            "ORIGIN": [1.0, 2.0, 0.0],
            "CEILING_MATL_ID": "GYPSUM",
            "WALL_MATL_ID": "CONCRETE",
            "FLOOR_MATL_ID": "STEEL",
        }

        parser._parse_compartment_block(params)

        assert len(parser.compartments) == 1
        comp = parser.compartments[0]
        assert comp.id == "Room1"
        assert comp.width == 4.0
        assert comp.depth == 5.0
        assert comp.height == 3.0
        assert comp.origin_x == 1.0
        assert comp.origin_y == 2.0
        assert comp.origin_z == 0.0
        assert comp.ceiling_mat_id == "GYPSUM"
        assert comp.wall_mat_id == "CONCRETE"
        assert comp.floor_mat_id == "STEEL"

    def test_parse_compartment_block_invalid_origin(self):
        """Test COMP block parsing with invalid origin coordinates."""
        parser = CFASTParser()
        params = {
            "ID": "Room1",
            "WIDTH": 4.0,
            "DEPTH": 5.0,
            "HEIGHT": 3.0,
            "ORIGIN": [1.0, 2.0],  # Missing Z coordinate
        }

        with pytest.raises(
            ValueError, match="ORIGIN must contain at least 3 coordinates"
        ):
            parser._parse_compartment_block(params)

    def test_parse_wall_vent(self):
        """Test wall vent parsing."""
        parser = CFASTParser()
        params = {
            "ID": "DOOR1",
            "COMP_IDS": ["Room1", "Room2"],
            "BOTTOM": 0.0,
            "HEIGHT": 2.0,
            "WIDTH": 0.8,
            "FACE": "FRONT",
            "OFFSET": 1.0,
        }

        parser._parse_wall_vent(params)

        assert len(parser.wall_vents) == 1
        vent = parser.wall_vents[0]
        assert vent.id == "DOOR1"
        assert vent.comps_ids == ["Room1", "Room2"]
        assert vent.bottom == 0.0
        assert vent.height == 2.0
        assert vent.width == 0.8
        assert vent.face == "FRONT"
        assert vent.offset == 1.0

    def test_parse_ceiling_floor_vent(self):
        """Test ceiling/floor vent parsing."""
        parser = CFASTParser()
        params = {
            "ID": "CEILING_VENT1",
            "COMP_IDS": ["Room1", "Room2"],
            "AREA": 0.5,
            "SHAPE": "ROUND",
            "OFFSETS": [1.0, 2.0],
        }

        parser._parse_ceiling_floor_vent(params)

        assert len(parser.ceiling_floor_vents) == 1
        vent = parser.ceiling_floor_vents[0]
        assert vent.id == "CEILING_VENT1"
        assert vent.comps_ids == ["Room1", "Room2"]
        assert vent.area == 0.5
        assert vent.shape == "ROUND"
        assert vent.offsets == [1.0, 2.0]

    def test_parse_mechanical_vent(self):
        """Test mechanical vent parsing."""
        parser = CFASTParser()
        params = {
            "ID": "MECH_VENT1",
            "COMP_IDS": ["Room1", "Room2"],
            "AREAS": [0.1, 0.1],
            "HEIGHTS": [2.0, 2.0],
            "ORIENTATIONS": ["VERTICAL", "VERTICAL"],
            "FLOW": 0.5,
            "CUTOFFS": [200, 300],
            "OFFSETS": [0.0, 0.0],
        }

        parser._parse_mechanical_vent(params)

        assert len(parser.mechanical_vents) == 1
        vent = parser.mechanical_vents[0]
        assert vent.id == "MECH_VENT1"
        assert vent.comps_ids == ["Room1", "Room2"]
        assert vent.area == [0.1, 0.1]
        assert vent.heights == [2.0, 2.0]
        assert vent.flow == 0.5

    def test_parse_fire_block(self):
        """Test FIRE block parsing."""
        parser = CFASTParser()
        params = {
            "ID": "Fire1",
            "COMP_ID": "Room1",
            "FIRE_ID": "TestFire",
            "LOCATION": [2.5, 2.5],
        }

        parser._parse_fire_block(params)

        assert len(parser._fire_hash_map) == 1
        assert "TestFire" in parser._fire_hash_map
        fire = parser._fire_hash_map["TestFire"]
        assert fire.id == "Fire1"
        assert fire.comp_id == "Room1"
        assert fire.fire_id == "TestFire"
        assert fire.location == [2.5, 2.5]

    def test_parse_chemistry_block(self):
        """Test CHEM block parsing."""
        parser = CFASTParser()
        # First create a fire
        parser._fire_hash_map["TestFire"] = Mock()
        parser._fire_hash_map["TestFire"].fire_id = "TestFire"

        params = {
            "ID": "TestFire",
            "CARBON": 1,
            "HYDROGEN": 4,
            "OXYGEN": 0,
            "NITROGEN": 0,
            "CHLORINE": 0,
            "HEAT_OF_COMBUSTION": 50000,
            "RADIATIVE_FRACTION": 0.35,
        }

        parser._parse_chemistry_block(params)

        fire = parser._fire_hash_map["TestFire"]
        assert fire.carbon == 1
        assert fire.hydrogen == 4
        assert fire.oxygen == 0
        assert fire.heat_of_combustion == 50000

    def test_parse_chemistry_block_missing_fire(self):
        """Test CHEM block parsing with missing fire ID."""
        parser = CFASTParser()
        params = {
            "ID": "NonExistentFire",
            "CARBON": 1,
            "HYDROGEN": 4,
        }

        with pytest.raises(
            ValueError, match="FIRE_ID NonExistentFire in CHEM block not found"
        ):
            parser._parse_chemistry_block(params)

    def test_parse_table_block_labels(self):
        """Test TABL block parsing with LABELS (should be skipped)."""
        parser = CFASTParser()
        params = {"LABELS": ["TIME", "HRR"]}

        # Should not raise any errors and should not modify anything
        parser._parse_table_block(params)

    def test_parse_table_block_data(self):
        """Test TABL block parsing with DATA."""
        parser = CFASTParser()
        # First create a fire
        mock_fire = Mock()
        mock_fire.data_table = []  # Initialize as empty list
        parser._fire_hash_map["TestFire"] = mock_fire

        params = {"ID": "TestFire", "DATA": [0, 100]}

        parser._parse_table_block(params)

        # Should have added data to the fire
        assert mock_fire.data_table == [[0, 100]]

    def test_parse_table_block_data_missing_fire(self):
        """Test TABL block parsing with DATA but missing fire."""
        parser = CFASTParser()
        params = {"ID": "NonExistentFire", "DATA": [0, 100]}

        with pytest.raises(
            ValueError, match="FIRE_ID NonExistentFire in TABL block not found"
        ):
            parser._parse_table_block(params)

    def test_parse_device_block_cylinder(self):
        """Test DEVC block parsing for CYLINDER device."""
        parser = CFASTParser()
        params = {
            "TYPE": "CYLINDER",
            "ID": "Target1",
            "COMP_ID": "Room1",
            "LOCATION": [1.0, 2.0, 1.5],
            "MATL_ID": "STEEL",
            "THICKNESS": 0.01,
            "TEMPERATURE_DEPTH": 0.005,
            "SURFACE_ORIENTATION": "HORIZONTAL",
        }

        parser._parse_device_block(params)

        assert len(parser.devices) == 1
        device = parser.devices[0]
        assert device.id == "Target1"
        assert device.comp_id == "Room1"
        assert device.location == [1.0, 2.0, 1.5]

    def test_parse_device_block_heat_detector(self):
        """Test DEVC block parsing for HEAT_DETECTOR."""
        parser = CFASTParser()
        params = {
            "TYPE": "HEAT_DETECTOR",
            "ID": "HD1",
            "COMP_ID": "Room1",
            "LOCATION": [2.0, 2.0, 2.5],
            "SETPOINT": 68.0,
            "RTI": 165.0,
        }

        parser._parse_device_block(params)

        assert len(parser.devices) == 1

    def test_parse_device_block_smoke_detector(self):
        """Test DEVC block parsing for SMOKE_DETECTOR."""
        parser = CFASTParser()
        params = {
            "TYPE": "SMOKE_DETECTOR",
            "ID": "SD1",
            "COMP_ID": "Room1",
            "LOCATION": [2.0, 2.0, 2.5],
            "SETPOINT": 3.0,
            "OBSCURATION": 0.1,
        }

        parser._parse_device_block(params)

        assert len(parser.devices) == 1

    def test_parse_device_block_sprinkler(self):
        """Test DEVC block parsing for SPRINKLER."""
        parser = CFASTParser()
        params = {
            "TYPE": "SPRINKLER",
            "ID": "SPR1",
            "COMP_ID": "Room1",
            "LOCATION": [2.0, 2.0, 2.5],
            "SETPOINT": 68.0,
            "RTI": 165.0,
            "SPRAY_DENSITY": 0.05,
        }

        parser._parse_device_block(params)

        assert len(parser.devices) == 1

    def test_parse_device_block_unknown_type(self):
        """Test DEVC block parsing with unknown device type."""
        parser = CFASTParser()
        params = {
            "TYPE": "UNKNOWN_DEVICE",
            "ID": "Unknown1",
        }

        with pytest.raises(ValueError, match="Unknown device type: UNKNOWN_DEVICE"):
            parser._parse_device_block(params)

    def test_parse_connection_block_wall(self) -> None:
        """Test CONN block parsing for wall connections."""
        parser = CFASTParser()
        params = {
            "TYPE": "WALL",
            "COMP_ID": "ROOM1",
            "COMP_IDS": "ROOM2",
            "F": 0.6,
        }

        parser._parse_connection_block(params)

        assert len(parser.surface_connections) == 1
        connection = parser.surface_connections[0]
        assert connection.conn_type == "WALL"
        assert connection.comp_id == "ROOM1"
        assert connection.comp_ids == "ROOM2"
        assert connection.fraction == 0.6

    def test_parse_connection_block_floor(self) -> None:
        """Test CONN block parsing for floor connections."""
        parser = CFASTParser()
        params = {
            "TYPE": "FLOOR",
            "COMP_ID": "UPPER_ROOM",
            "COMP_IDS": "LOWER_ROOM",
        }

        parser._parse_connection_block(params)

        assert len(parser.surface_connections) == 1
        connection = parser.surface_connections[0]
        assert connection.conn_type == "FLOOR"
        assert connection.comp_id == "UPPER_ROOM"
        assert connection.comp_ids == "LOWER_ROOM"
        assert connection.fraction is None  # Floor connections don't use fraction

    def test_parse_connection_block_missing_type(self) -> None:
        """Test CONN block parsing with missing TYPE parameter."""
        parser = CFASTParser()
        params = {
            "COMP_ID": "ROOM1",
            "COMP_IDS": "ROOM2",
            "F": 0.5,
        }

        with pytest.raises(ValueError, match="Missing required parameter: TYPE"):
            parser._parse_connection_block(params)

    def test_parse_connection_block_unknown_type(self) -> None:
        """Test CONN block parsing with unknown connection type."""
        parser = CFASTParser()
        params = {
            "TYPE": "CEILING",  # Not a valid connection type
            "COMP_ID": "ROOM1",
            "COMP_IDS": "ROOM2",
        }

        with pytest.raises(
            ValueError, match="Unknown Surface Connections type: CEILING"
        ):
            parser._parse_connection_block(params)

    def test_parse_connection_block_wall_missing_required_params(self) -> None:
        """Test CONN wall block parsing with missing required parameters."""
        parser = CFASTParser()

        # Missing COMP_ID
        params = {
            "TYPE": "WALL",
            "COMP_IDS": "ROOM2",
            "F": 0.5,
        }
        with pytest.raises(ValueError, match="Missing required parameter: COMP_ID"):
            parser._parse_connection_block(params)

        # Missing COMP_IDS
        params = {
            "TYPE": "WALL",
            "COMP_ID": "ROOM1",
            "F": 0.5,
        }
        with pytest.raises(ValueError, match="Missing required parameter: COMP_IDS"):
            parser._parse_connection_block(params)

        # Missing F (fraction)
        params = {
            "TYPE": "WALL",
            "COMP_ID": "ROOM1",
            "COMP_IDS": "ROOM2",
        }
        with pytest.raises(ValueError, match="Missing required parameter: F"):
            parser._parse_connection_block(params)

    def test_parse_connection_block_floor_missing_required_params(self) -> None:
        """Test CONN floor block parsing with missing required parameters."""
        parser = CFASTParser()

        # Missing COMP_ID
        params = {
            "TYPE": "FLOOR",
            "COMP_IDS": "LOWER_ROOM",
        }
        with pytest.raises(ValueError, match="Missing required parameter: COMP_ID"):
            parser._parse_connection_block(params)

        # Missing COMP_IDS
        params = {
            "TYPE": "FLOOR",
            "COMP_ID": "UPPER_ROOM",
        }
        with pytest.raises(ValueError, match="Missing required parameter: COMP_IDS"):
            parser._parse_connection_block(params)

    def test_parse_connection_block_wall_with_invalid_fraction_type(self) -> None:
        """Test CONN wall block parsing with invalid fraction type."""
        parser = CFASTParser()
        params = {
            "TYPE": "WALL",
            "COMP_ID": "ROOM1",
            "COMP_IDS": "ROOM2",
            "F": "invalid_float",  # Should be float
        }

        with pytest.raises(ValueError, match="Parameter F could not be converted to"):
            parser._parse_connection_block(params)

    def test_parse_connection_block_multiple_connections(self) -> None:
        """Test parsing multiple connection blocks."""
        parser = CFASTParser()

        # Add wall connection
        wall_params = {
            "TYPE": "WALL",
            "COMP_ID": "LIVING_ROOM",
            "COMP_IDS": "KITCHEN",
            "F": 0.8,
        }
        parser._parse_connection_block(wall_params)

        # Add floor connection
        floor_params = {
            "TYPE": "FLOOR",
            "COMP_ID": "SECOND_FLOOR",
            "COMP_IDS": "FIRST_FLOOR",
        }
        parser._parse_connection_block(floor_params)

        assert len(parser.surface_connections) == 2

        # Check wall connection
        wall_conn = parser.surface_connections[0]
        assert wall_conn.conn_type == "WALL"
        assert wall_conn.comp_id == "LIVING_ROOM"
        assert wall_conn.comp_ids == "KITCHEN"
        assert wall_conn.fraction == 0.8

        # Check floor connection
        floor_conn = parser.surface_connections[1]
        assert floor_conn.conn_type == "FLOOR"
        assert floor_conn.comp_id == "SECOND_FLOOR"
        assert floor_conn.comp_ids == "FIRST_FLOOR"
        assert floor_conn.fraction is None

    def test_parse_vent_block_unknown_type(self):
        """Test VENT block parsing with unknown vent type."""
        parser = CFASTParser()
        params = {
            "TYPE": "UNKNOWN_VENT",
            "ID": "Unknown1",
        }

        with pytest.raises(ValueError, match="Unknown vent type: UNKNOWN_VENT"):
            parser._parse_vent_block(params)

    def test_vent_block_routing(self):
        """Test that VENT blocks are routed to correct parsers."""
        parser = CFASTParser()

        # Test wall vent routing
        wall_params = {
            "TYPE": "WALL",
            "ID": "DOOR1",
            "COMP_IDS": ["R1", "R2"],
            "BOTTOM": 0.0,
            "HEIGHT": 2.0,
            "WIDTH": 0.8,
            "OFFSET": 1.0,
        }
        parser._parse_vent_block(wall_params)
        assert len(parser.wall_vents) == 1

        # Test ceiling vent routing
        ceiling_params = {
            "TYPE": "CEILING",
            "ID": "CEIL1",
            "COMP_IDS": ["R1", "R2"],
            "AREA": 0.5,
        }
        parser._parse_vent_block(ceiling_params)
        assert len(parser.ceiling_floor_vents) == 1

        # Test mechanical vent routing
        mech_params = {"TYPE": "MECHANICAL", "ID": "MECH1", "COMP_IDS": ["R1", "R2"]}
        parser._parse_vent_block(mech_params)
        assert len(parser.mechanical_vents) == 1


class TestSanitizeCFASTTitleAndMaterial:
    """Test class for sanitize_cfast_title_and_material function."""

    def test_sanitize_title_with_quotes(self):
        """Test sanitizing TITLE with quotes."""
        content = "&HEAD TITLE = 'Test, Title/With \"Special\" Chars' /"
        result = sanitize_cfast_title_and_material(content)
        assert "TITLE = 'Test Title With Special Chars'" in result

    def test_sanitize_material_with_special_chars(self):
        """Test sanitizing MATERIAL with special characters."""
        content = "&MATL MATERIAL = 'Gypsum, Board/Wall \"Material\"' /"
        result = sanitize_cfast_title_and_material(content)
        assert "MATERIAL = 'Gypsum Board Wall Material'" in result

    def test_sanitize_double_quotes(self):
        """Test sanitizing with double quotes."""
        content = '&HEAD TITLE = "Test, Title/With Special Chars" /'
        result = sanitize_cfast_title_and_material(content)
        assert "TITLE = 'Test Title With Special Chars'" in result

    def test_sanitize_no_quotes(self):
        """Test sanitizing unquoted values."""
        content = "&HEAD TITLE = TestTitle /"
        result = sanitize_cfast_title_and_material(content)
        assert "TITLE = 'TestTitle'" in result

    def test_sanitize_multiple_values(self):
        """Test sanitizing multiple TITLE/MATERIAL values."""
        content = """&HEAD TITLE = 'Test, Title' /
                     &MATL MATERIAL = 'Steel/Plate' /"""
        result = sanitize_cfast_title_and_material(content)
        assert "TITLE = 'Test Title'" in result
        assert "MATERIAL = 'Steel Plate'" in result

    def test_sanitize_leaves_other_params_unchanged(self):
        """Test that other parameters are left unchanged."""
        content = (
            "&HEAD TITLE = 'Test, Title' VERSION = 7600, OTHER = 'value, with/chars' /"
        )
        result = sanitize_cfast_title_and_material(content)
        assert "TITLE = 'Test Title'" in result
        assert "VERSION = 7600" in result
        assert "OTHER = 'value, with/chars'" in result  # Should be unchanged

    def test_sanitize_collapsed_whitespace(self):
        """Test that multiple whitespaces are collapsed."""
        content = "&HEAD TITLE = 'Test    Multiple   Spaces' /"
        result = sanitize_cfast_title_and_material(content)
        assert "TITLE = 'Test Multiple Spaces'" in result

    def test_sanitize_doubled_apostrophes(self):
        """Test handling of doubled apostrophes."""
        content = "&HEAD TITLE = 'Test''s Title' /"
        result = sanitize_cfast_title_and_material(content)
        assert "TITLE = 'Tests Title'" in result


class TestParseCFASTFile:
    """Test class for parse_cfast_file function."""

    def test_parse_cfast_file_success(self):
        """Test successful parsing using convenience function."""
        content = """&HEAD VERSION = 7600, TITLE = 'Test Simulation' /
                     &TIME SIMULATION = 900 /
                     &COMP ID = 'Room1', DEPTH = 5, HEIGHT = 3, WIDTH = 4, ORIGIN = 0, 0, 0 /
                     &TAIL /"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".in", delete=False) as f:
            f.write(content)
            temp_file = f.name

        try:
            model = parse_cfast_file(temp_file)

            assert model.simulation_environment.title == "Test Simulation"
            assert len(model.compartments) == 1
            assert model.compartments[0].id == "Room1"
        finally:
            os.unlink(temp_file)

    def test_parse_cfast_file_not_found(self):
        """Test parsing non-existent file with convenience function."""
        with pytest.raises(FileNotFoundError):
            parse_cfast_file("nonexistent.in")

    def test_parse_cfast_file_with_path_object(self):
        """Test parsing with Path object."""
        content = """&HEAD VERSION = 7600, TITLE = 'Path Test' /
                     &TIME SIMULATION = 600 /
                     &COMP ID = 'Room1', DEPTH = 3, HEIGHT = 3, WIDTH = 3, ORIGIN = 0, 0, 0 /
                     &TAIL /"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".in", delete=False) as f:
            f.write(content)
            temp_file = Path(f.name)

        try:
            model = parse_cfast_file(temp_file)

            assert model.simulation_environment.title == "Path Test"
            assert model.simulation_environment.time_simulation == 600
        finally:
            os.unlink(temp_file)


class TestCFASTParserAdditionalCoverage(unittest.TestCase):
    """Additional test cases to improve coverage."""

    def test_parse_file_no_diag_block(self):
        """Test parsing a file without a DIAG block (StopIteration case)."""
        content = "&HEAD TITLE='Test Model' /\n&TIME SIMULATION=300 /"

        with patch("builtins.open", mock_open(read_data=content)):
            with patch("pathlib.Path.exists", return_value=True):
                parser = CFASTParser()
                model = parser.parse_file("test.in")

                # Should parse successfully without DIAG block
                self.assertEqual(model.simulation_environment.title, "Test Model")
                self.assertEqual(model.simulation_environment.time_simulation, 300)

    def test_clean_content_file_ends_in_block_without_closing(self):
        """Test cleaning content when file ends inside a block without proper closing."""
        parser = CFASTParser()
        # Content ends inside a block without closing /
        content = "&HEAD TITLE='Test'\nTITLE='Continued'"

        result = parser._clean_content(content)

        # Should join the block lines even without closing /
        self.assertIn("&HEAD TITLE='Test' TITLE='Continued'", result)

    def test_clean_content_standalone_slash(self):
        """Test cleaning content with standalone slash outside of block."""
        parser = CFASTParser()
        content = "&HEAD TITLE='Test' /\n/\n&TIME SIMULATION=300 /"

        result = parser._clean_content(content)

        # Result should contain the processed content
        self.assertTrue(len(result) > 0)
        self.assertIn("&HEAD TITLE='Test'", result)
        self.assertIn("&TIME SIMULATION=300", result)

    def test_parse_time_block_empty_params(self):
        """Test parsing TIME block with empty parameters."""
        parser = CFASTParser()
        parser.simulation_environment = Mock()

        # Empty params should not raise errors
        parser._parse_time_block({})

        # Should complete without setting attributes

    def test_parse_init_block_partial_params(self):
        """Test parsing INIT block with only some parameters."""
        parser = CFASTParser()
        parser.simulation_environment = Mock()

        params = {"PRESSURE": 101325}
        parser._parse_init_block(params)

        # Only pressure should be set
        self.assertEqual(parser.simulation_environment.init_pressure, 101325)

    def test_parse_misc_block_boolean_conversion(self):
        """Test parsing MISC block with boolean conversion."""
        parser = CFASTParser()
        parser.simulation_environment = Mock()

        params = {"ADIABATIC": 1, "MAX_TIME_STEP": 0.1}
        parser._parse_misc_block(params)

        # ADIABATIC should be converted to boolean
        self.assertEqual(parser.simulation_environment.adiabatic, True)
        self.assertEqual(parser.simulation_environment.max_time_step, 0.1)

    def test_parse_table_block_invalid_fire_id(self):
        """Test parsing TABLE block with invalid fire ID."""
        parser = CFASTParser()
        parser._fire_hash_map = {}  # Empty fire map

        params = {"ID": "invalid_fire", "DATA": [1, 2, 3]}

        # Should raise ValueError for missing fire ID
        with self.assertRaises(ValueError):
            parser._parse_table_block(params)

    def test_parse_device_block_missing_required_params(self):
        """Test parsing DEVICE block missing required parameters."""
        parser = CFASTParser()
        parser.devices = Mock()

        # Missing TYPE parameter should raise ValueError
        params = {"ID": "device1", "COMP_ID": "comp1"}

        # Should raise ValueError for missing TYPE
        with self.assertRaises(ValueError):
            parser._parse_device_block(params)

    def test_parse_time_block_all_params(self):
        """Test parsing TIME block with all possible parameters."""
        parser = CFASTParser()
        parser.simulation_environment = Mock()

        params = {"SIMULATION": 1800, "PRINT": 60, "SMOKEVIEW": 30, "SPREADSHEET": 120}
        parser._parse_time_block(params)

        # All parameters should be set
        self.assertEqual(parser.simulation_environment.time_simulation, 1800)
        self.assertEqual(parser.simulation_environment.print, 60)
        self.assertEqual(parser.simulation_environment.smokeview, 30)
        self.assertEqual(parser.simulation_environment.spreadsheet, 120)

    def test_parse_init_block_all_params(self):
        """Test parsing INIT block with all possible parameters."""
        parser = CFASTParser()
        parser.simulation_environment = Mock()

        params = {
            "PRESSURE": 101325,
            "RELATIVE_HUMIDITY": 50,
            "INTERIOR_TEMPERATURE": 20,
            "EXTERIOR_TEMPERATURE": 15,
        }
        parser._parse_init_block(params)

        # All parameters should be set
        self.assertEqual(parser.simulation_environment.init_pressure, 101325)
        self.assertEqual(parser.simulation_environment.relative_humidity, 50)
        self.assertEqual(parser.simulation_environment.interior_temperature, 20)
        self.assertEqual(parser.simulation_environment.exterior_temperature, 15)

    def test_parse_misc_block_all_params(self):
        """Test parsing MISC block with all possible parameters."""
        parser = CFASTParser()
        parser.simulation_environment = Mock()

        params = {"ADIABATIC": 0, "MAX_TIME_STEP": 0.05, "LOWER_OXYGEN_LIMIT": 0.15}
        parser._parse_misc_block(params)

        # All parameters should be set
        self.assertEqual(parser.simulation_environment.adiabatic, False)
        self.assertEqual(parser.simulation_environment.max_time_step, 0.05)
        self.assertEqual(parser.simulation_environment.lower_oxygen_limit, 0.15)
