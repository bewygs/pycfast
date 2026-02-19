from __future__ import annotations

import pytest

from pycfast.devices import Devices

"""
Tests for the Devices class.
"""


class TestDevices:
    """Test class for Devices."""

    def test_init_plate_target(self):
        """Test initialization of a PLATE target device."""
        device = Devices(
            id="TARGET1",
            comp_id="ROOM1",
            location=[1.0, 2.0, 1.5],
            type="PLATE",
            material_id="STEEL",
            normal=[0, 0, -1],
            thickness=0.001,
            temperature_depth=0.0005,
            depth_units="M",
        )
        assert device.id == "TARGET1"
        assert device.comp_id == "ROOM1"
        assert device.location == [1.0, 2.0, 1.5]
        assert device.type == "PLATE"
        assert device.material_id == "STEEL"
        assert device.normal == [0, 0, -1]
        assert device.surface_orientation is None
        assert device.thickness == 0.001
        assert device.temperature_depth == 0.0005
        assert device.depth_units == "M"

    def test_init_cylinder_target(self):
        """Test initialization of a CYLINDER target device."""
        device = Devices(
            id="TARGET2",
            comp_id="ROOM1",
            location=[2.0, 3.0, 2.0],
            type="CYLINDER",
            material_id="ALUMINUM",
            surface_orientation="CEILING",
            temperature_depth=0.001,
        )
        assert device.id == "TARGET2"
        assert device.type == "CYLINDER"
        assert device.material_id == "ALUMINUM"
        assert device.surface_orientation == "CEILING"
        assert device.normal is None
        assert device.temperature_depth == 0.001

    def test_init_heat_detector(self):
        """Test initialization of a HEAT_DETECTOR device."""
        device = Devices(
            id="HD1",
            comp_id="ROOM1",
            location=[1.5, 1.5, 2.3],
            type="HEAT_DETECTOR",
            material_id="",  # Not used for detectors
            setpoint=70.0,
            rti=50.0,
        )
        assert device.id == "HD1"
        assert device.type == "HEAT_DETECTOR"
        assert device.setpoint == 70.0
        assert device.rti == 50.0

    def test_init_smoke_detector(self):
        """Test initialization of a SMOKE_DETECTOR device."""
        device = Devices(
            id="SD1",
            comp_id="ROOM1",
            location=[2.0, 2.0, 2.3],
            type="SMOKE_DETECTOR",
            material_id="",  # Not used for detectors
            obscuration=25.0,
        )
        assert device.id == "SD1"
        assert device.type == "SMOKE_DETECTOR"
        assert device.obscuration == 25.0

    def test_init_sprinkler(self):
        """Test initialization of a SPRINKLER device."""
        device = Devices(
            id="SPR1",
            comp_id="ROOM1",
            location=[3.0, 3.0, 2.4],
            type="SPRINKLER",
            material_id="",  # Not used for detectors
            setpoint=68.0,
            rti=165.0,
            spray_density=0.003,
        )
        assert device.id == "SPR1"
        assert device.type == "SPRINKLER"
        assert device.setpoint == 68.0
        assert device.rti == 165.0
        assert device.spray_density == 0.003

    def test_init_invalid_location_length(self):
        """Test that initialization fails with wrong location dimensions."""
        with pytest.raises(ValueError, match="location must be a list of 3 numbers"):
            Devices(
                id="DEV1",
                comp_id="ROOM1",
                location=[1.0, 2.0],  # Only 2 coordinates
                type="PLATE",
                material_id="STEEL",
                normal=[0, 0, -1],
                temperature_depth=0.0005,
            )

    def test_init_invalid_location_type(self):
        """Test that initialization fails with non-numeric location values."""
        with pytest.raises(ValueError, match="location must be a list of 3 numbers"):
            # This should fail validation even though it passes type checking temporarily
            invalid_location = [1.0, "invalid", 1.5]  # type: ignore
            Devices(
                id="DEV1",
                comp_id="ROOM1",
                location=invalid_location,
                type="PLATE",
                material_id="STEEL",
                normal=[0, 0, -1],
                temperature_depth=0.0005,
            )

    def test_init_target_missing_material_id(self):
        """Test that target initialization fails without material_id."""
        with pytest.raises(ValueError, match="requires material_id"):
            Devices(
                id="TARGET1",
                comp_id="ROOM1",
                location=[1.0, 2.0, 1.5],
                type="PLATE",
                material_id="",  # Empty material ID
                normal=[0, 0, -1],
                temperature_depth=0.0005,
            )

    def test_init_target_with_default_temperature_depth(self):
        """Test that target initialization uses default temperature_depth when not specified."""
        device = Devices(
            id="TARGET1",
            comp_id="ROOM1",
            location=[1.0, 2.0, 1.5],
            type="PLATE",
            material_id="STEEL",
            normal=[0, 0, -1],
            # temperature_depth not specified, should use default
        )
        # Should use default value of 0.5
        assert device.temperature_depth == 0.5

    def test_init_target_both_normal_and_orientation(self):
        """Test that target initialization fails with both normal and surface_orientation."""
        with pytest.raises(ValueError, match="either normal or surface_orientation"):
            Devices(
                id="TARGET1",
                comp_id="ROOM1",
                location=[1.0, 2.0, 1.5],
                type="PLATE",
                material_id="STEEL",
                normal=[0, 0, -1],
                surface_orientation="CEILING",  # Both provided
                temperature_depth=0.0005,
            )

    def test_init_target_neither_normal_nor_orientation(self):
        """Test that target initialization fails without normal or surface_orientation."""
        with pytest.raises(ValueError, match="either normal or surface_orientation"):
            Devices(
                id="TARGET1",
                comp_id="ROOM1",
                location=[1.0, 2.0, 1.5],
                type="PLATE",
                material_id="STEEL",
                temperature_depth=0.0005,
                # Neither normal nor surface_orientation provided
            )

    def test_init_target_invalid_normal(self):
        """Test that target initialization fails with invalid normal vector."""
        with pytest.raises(ValueError, match="normal must be a list of 3 numbers"):
            Devices(
                id="TARGET1",
                comp_id="ROOM1",
                location=[1.0, 2.0, 1.5],
                type="PLATE",
                material_id="STEEL",
                normal=[0, 0],  # Only 2 components
                temperature_depth=0.0005,
            )

    def test_init_heat_detector_missing_parameters(self):
        """Test that heat detector initialization fails without required parameters."""
        with pytest.raises(ValueError, match="HEAT_DETECTOR requires setpoint and rti"):
            Devices(
                id="HD1",
                comp_id="ROOM1",
                location=[1.5, 1.5, 2.3],
                type="HEAT_DETECTOR",
                material_id="",
                setpoint=70.0,
                # Missing rti
            )

    def test_init_smoke_detector_with_default_obscuration(self):
        """Test that smoke detector initialization uses default obscuration when not specified."""
        device = Devices(
            id="SD1",
            comp_id="ROOM1",
            location=[2.0, 2.0, 2.3],
            type="SMOKE_DETECTOR",
            material_id="",
            # obscuration not specified, should use default
        )
        # Should use default value of 23.93
        assert device.obscuration == 23.93

    def test_init_sprinkler_missing_parameters(self):
        """Test that sprinkler initialization fails without required parameters."""
        with pytest.raises(
            ValueError, match="SPRINKLER requires setpoint, rti, and spray_density"
        ):
            Devices(
                id="SPR1",
                comp_id="ROOM1",
                location=[3.0, 3.0, 2.4],
                type="SPRINKLER",
                material_id="",
                setpoint=68.0,
                rti=165.0,
                # Missing spray_density
            )

    def test_init_unknown_device_type(self):
        """Test that initialization fails with unknown device type."""
        with pytest.raises(ValueError, match="Unknown device type"):
            Devices(
                id="DEV1",
                comp_id="ROOM1",
                location=[1.0, 2.0, 1.5],
                type="UNKNOWN_TYPE",
                material_id="STEEL",
            )

    def test_to_input_string_plate_target_with_normal(self):
        """Test input string generation for plate target with normal vector."""
        device = Devices(
            id="TARGET1",
            comp_id="ROOM1",
            location=[1.0, 2.0, 1.5],
            type="PLATE",
            material_id="STEEL",
            normal=[0, 0, -1],
            thickness=0.001,
            temperature_depth=0.0005,
            depth_units="M",
        )
        result = device.to_input_string()
        expected_parts = [
            "ID = 'TARGET1'",
            "COMP_ID = 'ROOM1'",
            "LOCATION = 1.0, 2.0, 1.5",
            "TYPE = 'PLATE'",
            "MATL_ID = 'STEEL'",
            "NORMAL = 0, 0, -1",
            "THICKNESS = 0.001",
            "TEMPERATURE_DEPTH = 0.0005",
            "DEPTH_UNITS = 'M'",
        ]
        for part in expected_parts:
            assert part in result
        assert result.startswith("&DEVC")
        assert result.endswith("/\n")

    def test_to_input_string_plate_target_with_surface_orientation(self):
        """Test input string generation for plate target with surface orientation."""
        device = Devices(
            id="TARGET2",
            comp_id="ROOM1",
            location=[2.0, 3.0, 2.0],
            type="PLATE",
            material_id="ALUMINUM",
            surface_orientation="CEILING",
            temperature_depth=0.001,
        )
        result = device.to_input_string()
        assert "SURFACE_ORIENTATION = 'CEILING'" in result
        assert "NORMAL" not in result

    def test_to_input_string_heat_detector(self):
        """Test input string generation for heat detector."""
        device = Devices(
            id="HD1",
            comp_id="ROOM1",
            location=[1.5, 1.5, 2.3],
            type="HEAT_DETECTOR",
            material_id="",
            setpoint=70.0,
            rti=50.0,
        )
        result = device.to_input_string()
        expected_parts = [
            "ID = 'HD1'",
            "TYPE = 'HEAT_DETECTOR'",
            "SETPOINT = 70.0",
            "RTI = 50.0",
        ]
        for part in expected_parts:
            assert part in result
        assert "MATL_ID" not in result  # Shouldn't include material for detectors

    def test_to_input_string_smoke_detector(self):
        """Test input string generation for smoke detector."""
        device = Devices(
            id="SD1",
            comp_id="ROOM1",
            location=[2.0, 2.0, 2.3],
            type="SMOKE_DETECTOR",
            material_id="",
            obscuration=25.0,
        )
        result = device.to_input_string()
        assert "TYPE = 'SMOKE_DETECTOR'" in result
        assert "SETPOINTS = 25.0, 25.0" in result

    def test_to_input_string_sprinkler(self):
        """Test input string generation for sprinkler."""
        device = Devices(
            id="SPR1",
            comp_id="ROOM1",
            location=[3.0, 3.0, 2.4],
            type="SPRINKLER",
            material_id="",
            setpoint=68.0,
            rti=165.0,
            spray_density=0.003,
        )
        result = device.to_input_string()
        expected_parts = [
            "TYPE = 'SPRINKLER'",
            "SETPOINT = 68.0",
            "RTI = 165.0",
            "SPRAY_DENSITY = 0.003",
        ]
        for part in expected_parts:
            assert part in result

    def test_to_input_string_with_adiabatic(self):
        """Test input string generation with adiabatic flag."""
        device = Devices(
            id="DEV1",
            comp_id="ROOM1",
            location=[1.0, 2.0, 1.5],
            type="PLATE",
            material_id="STEEL",
            normal=[0, 0, -1],
            thickness=0.001,
            temperature_depth=0.0005,
            adiabatic=True,
        )
        result = device.to_input_string()
        assert "ADIABATIC_TARGET = .TRUE." in result

    def test_to_input_string_with_convection_coefficients(self):
        """Test input string generation with convection coefficients."""
        device = Devices(
            id="DEV2",
            comp_id="ROOM1",
            location=[1.0, 2.0, 1.5],
            type="PLATE",
            material_id="STEEL",
            normal=[0, 0, -1],
            thickness=0.001,
            temperature_depth=0.0005,
            convection_coefficients=[10.0, 20.0, 30.0],
        )
        result = device.to_input_string()
        assert "CONVECTION_COEFFICIENTS = 10.0, 20.0, 30.0" in result

    # Test class methods
    def test_create_target_classmethod(self):
        """Test the create_target class method."""
        device = Devices.create_target(
            id="TARGET1",
            comp_id="ROOM1",
            location=[1.0, 2.0, 1.5],
            type="PLATE",
            material_id="STEEL",
            normal=[0, 0, -1],
            temperature_depth=0.0005,
            thickness=0.001,
        )
        assert isinstance(device, Devices)
        assert device.type == "PLATE"
        assert device.material_id == "STEEL"
        assert device.normal == [0, 0, -1]

    def test_create_target_classmethod_validation(self):
        """Test that create_target class method validates inputs."""
        with pytest.raises(ValueError, match="either normal or surface_orientation"):
            Devices.create_target(
                id="TARGET1",
                comp_id="ROOM1",
                location=[1.0, 2.0, 1.5],
                type="PLATE",
                material_id="STEEL",
                temperature_depth=0.0005,
                # Neither normal nor surface_orientation provided
            )

    @pytest.mark.parametrize(
        ("factory_method", "factory_kwargs", "expected_type", "extra_checks"),
        [
            pytest.param(
                "create_heat_detector",
                {
                    "id": "HD1",
                    "comp_id": "ROOM1",
                    "location": [1.5, 1.5, 2.3],
                    "setpoint": 70.0,
                    "rti": 50.0,
                },
                "HEAT_DETECTOR",
                {"setpoint": 70.0, "rti": 50.0},
                id="heat-detector",
            ),
            pytest.param(
                "create_smoke_detector",
                {
                    "id": "SD1",
                    "comp_id": "ROOM1",
                    "location": [2.0, 2.0, 2.3],
                    "setpoint": 25.0,
                    "obscuration": 25.0,
                },
                "SMOKE_DETECTOR",
                {"obscuration": 25.0},
                id="smoke-detector",
            ),
            pytest.param(
                "create_sprinkler",
                {
                    "id": "SPR1",
                    "comp_id": "ROOM1",
                    "location": [3.0, 3.0, 2.4],
                    "setpoint": 68.0,
                    "rti": 165.0,
                    "spray_density": 0.003,
                },
                "SPRINKLER",
                {"setpoint": 68.0, "rti": 165.0, "spray_density": 0.003},
                id="sprinkler",
            ),
        ],
    )
    def test_create_device_classmethod(
        self,
        factory_method: str,
        factory_kwargs: dict,
        expected_type: str,
        extra_checks: dict,
    ):
        """Test device creation class methods."""
        method = getattr(Devices, factory_method)
        device = method(**factory_kwargs)
        assert isinstance(device, Devices)
        assert device.type == expected_type
        for attr, value in extra_checks.items():
            assert getattr(device, attr) == value

    def test_repr_target(self):
        """Test __repr__ method for target device."""
        device = Devices(
            id="TEMP_01",
            comp_id="ROOM1",
            location=[1.0, 2.0, 1.5],
            type="PLATE",
            material_id="STEEL",
            normal=[0, 0, -1],
            thickness=0.001,
            temperature_depth=0.0005,
        )

        repr_str = repr(device)
        assert "Devices(" in repr_str
        assert "id='TEMP_01'" in repr_str
        assert "type='PLATE'" in repr_str
        assert "comp_id='ROOM1'" in repr_str
        assert "location=[1.0, 2.0, 1.5]" in repr_str
        assert "material_id='STEEL'" in repr_str
        assert "thickness=0.001" in repr_str
        assert "temperature_depth=0.0005" in repr_str

    def test_repr_detector(self):
        """Test __repr__ method for detector device."""
        device = Devices.create_heat_detector(
            id="HD_01",
            comp_id="ROOM1",
            location=[2.0, 2.0, 2.4],
            setpoint=74.0,
            rti=50.0,
        )

        repr_str = repr(device)
        assert "Devices(" in repr_str
        assert "id='HD_01'" in repr_str
        assert "type='HEAT_DETECTOR'" in repr_str
        assert "setpoint=74.0" in repr_str
        assert "rti=50.0" in repr_str

    def test_str_target(self):
        """Test __str__ method for target device."""
        device = Devices(
            id="TEMP_01",
            comp_id="LIVING_ROOM",
            location=[1.0, 2.0, 1.5],
            type="PLATE",
            material_id="STEEL",
            normal=[0, 0, -1],
            thickness=0.002,
            temperature_depth=0.001,
        )

        str_repr = str(device)
        assert "Target 'TEMP_01' (PLATE)" in str_repr
        assert "in 'LIVING_ROOM'" in str_repr
        assert "at (1.0, 2.0, 1.5)" in str_repr
        assert "material: STEEL" in str_repr
        assert "depth: 0.001m" in str_repr
        assert "thickness: 0.002m" in str_repr

    def test_str_heat_detector(self):
        """Test __str__ method for heat detector."""
        device = Devices.create_heat_detector(
            id="HD_01",
            comp_id="BEDROOM",
            location=[2.0, 2.0, 2.4],
            setpoint=74.0,
            rti=50.0,
        )

        str_repr = str(device)
        assert "Detector 'HD_01' (Heat Detector)" in str_repr
        assert "in 'BEDROOM'" in str_repr
        assert "at (2.0, 2.0, 2.4)" in str_repr
        assert "setpoint: 74.0°C" in str_repr
        assert "RTI: 50.0" in str_repr

    def test_str_smoke_detector(self):
        """Test __str__ method for smoke detector."""
        device = Devices.create_smoke_detector(
            id="SD_01",
            comp_id="HALLWAY",
            location=[3.0, 1.0, 2.4],
            setpoint=5.0,
            obscuration=20.0,
        )

        str_repr = str(device)
        assert "Detector 'SD_01' (Smoke Detector)" in str_repr
        assert "in 'HALLWAY'" in str_repr
        assert "setpoint: 5.0" in str_repr

    def test_str_sprinkler(self):
        """Test __str__ method for sprinkler."""
        device = Devices.create_sprinkler(
            id="SPR_01",
            comp_id="KITCHEN",
            location=[2.5, 2.5, 2.4],
            setpoint=68.0,
            rti=165.0,
            spray_density=0.003,
        )

        str_repr = str(device)
        assert "Detector 'SPR_01' (Sprinkler)" in str_repr
        assert "in 'KITCHEN'" in str_repr
        assert "setpoint: 68.0" in str_repr
        assert "RTI: 165.0" in str_repr
        assert "spray: 0.003" in str_repr

    # Note: __eq__ and __hash__ methods not implemented in current version
    # These tests are removed to match actual implementation

    def test_getitem_target(self) -> None:
        """Test __getitem__ method for target device."""
        device = Devices(
            id="TEMP_01",
            comp_id="ROOM1",
            location=[1.0, 2.0, 1.5],
            type="PLATE",
            material_id="STEEL",
            normal=[0, 0, -1],
            thickness=0.001,
            temperature_depth=0.0005,
        )

        assert device["id"] == "TEMP_01"
        assert device["comp_id"] == "ROOM1"
        assert device["location"] == [1.0, 2.0, 1.5]
        assert device["type"] == "PLATE"
        assert device["material_id"] == "STEEL"
        assert device["normal"] == [0, 0, -1]
        assert device["thickness"] == 0.001
        assert device["temperature_depth"] == 0.0005

    def test_getitem_detector(self) -> None:
        """Test __getitem__ method for detector device."""
        device = Devices.create_heat_detector("HD1", "ROOM1", [1, 2, 3], 70.0, 50.0)

        assert device["id"] == "HD1"
        assert device["setpoint"] == 70.0
        assert device["rti"] == 50.0
        # Note: material_id doesn't exist on detector objects in simplified implementation

    def test_getitem_invalid_key(self) -> None:
        """Test __getitem__ method with invalid key."""
        device = Devices.create_heat_detector("HD1", "ROOM1", [1, 2, 3], 70.0, 50.0)

        with pytest.raises(
            KeyError, match="Property 'invalid_key' not found in Devices"
        ):
            device["invalid_key"]

    def test_setitem_common_properties(self) -> None:
        """Test __setitem__ method for common properties."""
        device = Devices.create_heat_detector("HD1", "ROOM1", [1, 2, 3], 70.0, 50.0)

        device["id"] = "NEW_HD"
        assert device.id == "NEW_HD"

        device["comp_id"] = "NEW_ROOM"
        assert device.comp_id == "NEW_ROOM"

        device["location"] = [4.0, 5.0, 6.0]
        assert device.location == [4.0, 5.0, 6.0]

    def test_setitem_invalid_key(self) -> None:
        """Test __setitem__ method with invalid key."""
        device = Devices.create_heat_detector("HD1", "ROOM1", [1, 2, 3], 70.0, 50.0)

        with pytest.raises(KeyError, match="Cannot set 'invalid_key'"):
            device["invalid_key"] = "value"

    def test_repr_html_detector(self) -> None:
        """Test _repr_html_ method for detector device."""
        device = Devices.create_heat_detector(
            id="HD_01",
            comp_id="BEDROOM",
            location=[2.0, 2.0, 2.4],
            setpoint=74.0,
            rti=50.0,
        )

        html_str = device._repr_html_()

        # Check that it returns valid HTML string
        assert isinstance(html_str, str)
        assert len(html_str) > 0

        # Check for expected HTML structure
        assert '<div class="pycfast-card' in html_str
        assert "Device: HD_01" in html_str
        assert "Heat Detector" in html_str
        assert "BEDROOM" in html_str

        # Check device properties
        assert "74.0°C" in html_str
        assert "50.0 (m·s)½" in html_str
        assert "(2.0, 2.0, 2.4)" in html_str

    def test_repr_html_target(self) -> None:
        """Test _repr_html_ method for target device."""
        device = Devices(
            id="TEMP_01",
            comp_id="ROOM1",
            location=[1.0, 2.0, 1.5],
            type="PLATE",
            material_id="STEEL",
            normal=[0, 0, -1],
            thickness=0.001,
            temperature_depth=0.0005,
        )

        html_str = device._repr_html_()

        # Check that it returns valid HTML string
        assert isinstance(html_str, str)
        assert len(html_str) > 0

        # Check for expected HTML structure
        assert '<div class="pycfast-card' in html_str
        assert "Device: TEMP_01" in html_str
        assert "Target" in html_str  # Check more flexible string
        assert "STEEL" in html_str
        assert "0.001" in html_str

    def test_repr_html_smoke_detector(self) -> None:
        """Test _repr_html_ method for smoke detector device."""
        device = Devices.create_smoke_detector(
            id="SD_01",
            comp_id="LIVING_ROOM",
            location=[3.0, 3.0, 2.4],
            setpoint=5.0,
        )

        html_str = device._repr_html_()

        assert isinstance(html_str, str)
        assert "Device: SD_01" in html_str
        assert "Smoke Detector" in html_str
        assert "LIVING_ROOM" in html_str
        assert "5.0" in html_str  # Check for setpoint value


class TestDevicesSetItemValidation:
    """Test validation in __setitem__ to ensure data integrity."""

    @pytest.mark.parametrize(
        "invalid_location",
        [
            pytest.param([1.0, 2.0], id="too-few"),
            pytest.param([1.0, 2.0, 3.0, 4.0], id="too-many"),
            pytest.param([1.0, "a", 3.0], id="non-numeric"),
        ],
    )
    def test_setitem_invalid_location(self, invalid_location):
        """Test that __setitem__ rejects invalid location values."""
        device = Devices(
            id="T1",
            comp_id="ROOM1",
            location=[1.0, 2.0, 3.0],
            type="PLATE",
            material_id="CONCRETE",
            surface_orientation="CEILING",
        )
        with pytest.raises(ValueError, match="location must be a list of 3 numbers"):
            device["location"] = invalid_location

    def test_setitem_target_empty_material_id(self):
        """Test that __setitem__ rejects empty material_id for target types."""
        device = Devices(
            id="T1",
            comp_id="ROOM1",
            location=[1.0, 2.0, 3.0],
            type="PLATE",
            material_id="CONCRETE",
            surface_orientation="CEILING",
        )
        with pytest.raises(ValueError, match="requires material_id"):
            device["material_id"] = ""

    def test_setitem_target_both_normal_and_orientation(self):
        """Test that __setitem__ rejects both normal and surface_orientation set."""
        device = Devices(
            id="T1",
            comp_id="ROOM1",
            location=[1.0, 2.0, 3.0],
            type="PLATE",
            material_id="CONCRETE",
            normal=[0.0, 0.0, 1.0],
        )
        # Adding surface_orientation when normal is already set
        device.surface_orientation = "CEILING"
        with pytest.raises(ValueError, match="requires either normal or"):
            device._validate()

    def test_setitem_heat_detector_removes_setpoint(self):
        """Test that __setitem__ rejects None setpoint for heat detector."""
        device = Devices.create_heat_detector(
            id="HD1",
            comp_id="ROOM1",
            location=[1.0, 2.0, 3.0],
            setpoint=57.0,
            rti=100.0,
        )
        with pytest.raises(ValueError, match="HEAT_DETECTOR requires setpoint and rti"):
            device["setpoint"] = None

    def test_setitem_sprinkler_removes_spray_density(self):
        """Test that __setitem__ rejects None spray_density for sprinkler."""
        device = Devices.create_sprinkler(
            id="SP1",
            comp_id="ROOM1",
            location=[1.0, 2.0, 3.0],
            setpoint=68.0,
            rti=50.0,
            spray_density=0.07,
        )
        with pytest.raises(
            ValueError, match="SPRINKLER requires setpoint, rti, and spray_density"
        ):
            device["spray_density"] = None

    def test_setitem_valid_location_change(self):
        """Test that __setitem__ accepts valid location change."""
        device = Devices.create_smoke_detector(
            id="SD1",
            comp_id="ROOM1",
            location=[1.0, 2.0, 3.0],
            setpoint=5.0,
        )
        device["location"] = [4.0, 5.0, 6.0]
        assert device.location == [4.0, 5.0, 6.0]

    def test_setitem_invalid_does_not_mutate_state(self):
        """Test that a failed __setitem__ rolls back to the previous value."""
        device = Devices(
            id="T1",
            comp_id="ROOM1",
            location=[1.0, 2.0, 3.0],
            type="PLATE",
            material_id="CONCRETE",
            surface_orientation="CEILING",
        )
        before = device.location.copy()

        with pytest.raises(ValueError):
            device["location"] = [1.0, 2.0]  # need to be 3 values

        assert device.location == before
