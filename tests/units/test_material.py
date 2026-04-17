from __future__ import annotations

import pytest

from pycfast.material import Material

"""
Tests for the Material class.
"""


class TestMaterial:
    """Test class for Material."""

    def test_init_default(self):
        """Test default initialization."""
        mat = Material(id="NM1", material="New Material 1")

        assert mat.id == "NM1"
        assert mat.material == "New Material 1"
        assert mat.conductivity is None
        assert mat.density is None
        assert mat.specific_heat is None
        assert mat.thickness is None
        assert mat.emissivity == 0.9

    def test_init_with_all_parameters(self):
        """Test initialization with all parameters."""
        mat = Material(
            id="GYPSUM",
            material="Gypsum Wallboard",
            conductivity=0.17,
            density=930,
            specific_heat=1.09,
            thickness=0.016,
            emissivity=0.9,
        )
        assert mat.id == "GYPSUM"
        assert mat.material == "Gypsum Wallboard"
        assert mat.conductivity == 0.17
        assert mat.density == 930
        assert mat.specific_heat == 1.09
        assert mat.thickness == 0.016
        assert mat.emissivity == 0.9

    def test_init_different_materials(self):
        """Test initialization with different material types."""
        # Steel
        steel = Material(
            id="STEEL",
            material="Structural Steel",
            conductivity=45.0,
            density=7850,
            specific_heat=0.46,
            thickness=0.01,
            emissivity=0.7,
        )
        assert steel.id == "STEEL"
        assert steel.conductivity == 45.0
        assert steel.density == 7850

        # Wood
        wood = Material(
            id="WOOD",
            material="Pine Wood",
            conductivity=0.14,
            density=500,
            specific_heat=1.38,
            thickness=0.02,
            emissivity=0.95,
        )
        assert wood.id == "WOOD"
        assert wood.emissivity == 0.95

    def test_init_invalid_id_type(self):
        """Test that initialization fails with non-string ID."""
        with pytest.raises(TypeError, match="id must be a string"):
            Material(id=123, material="Test Material")  # type: ignore

    def test_init_invalid_id_length(self):
        """Test that initialization fails with ID too long."""
        with pytest.raises(
            TypeError, match="id must be a string with no more than 16 characters"
        ):
            Material(id="THIS_ID_IS_TOO_LONG_FOR_CFAST", material="Test Material")

    def test_init_boundary_id_length(self):
        """Test initialization with ID exactly at 16 character limit."""
        mat = Material(id="EXACTLY_16_CHARS", material="Test Material")  # 16 characters
        assert mat.id == "EXACTLY_16_CHARS"

    def test_to_input_string_basic(self):
        """Test basic input string generation."""
        mat = Material(
            id="GYPSUM",
            material="Gypsum Board",
            conductivity=0.17,
            density=930,
            specific_heat=1.09,
            thickness=0.016,
            emissivity=0.9,
        )
        result = mat.to_input_string()
        assert result.startswith("&MATL")
        assert result.endswith("/\n")
        assert "ID = 'GYPSUM'" in result
        assert "MATERIAL = 'Gypsum Board'" in result
        assert "CONDUCTIVITY = 0.17" in result
        assert "DENSITY = 930" in result
        assert "SPECIFIC_HEAT = 1.09" in result
        assert "THICKNESS = 0.016" in result
        assert "EMISSIVITY = 0.9" in result
        assert "None" not in result

    def test_to_input_string_with_spaces_in_material_name(self):
        """Test input string generation with spaces in material name."""
        mat = Material(
            id="CONCRETE",
            material="High Density Concrete",
            conductivity=1.75,
            density=2300,
            specific_heat=0.88,
            thickness=0.1,
            emissivity=0.94,
        )
        result = mat.to_input_string()
        assert "MATERIAL = 'High Density Concrete'" in result

    def test_to_input_string_integer_values(self):
        """Test input string generation with integer values."""
        mat = Material(
            id="MAT1",
            material="Test Material",
            conductivity=1,  # Integer
            density=1000,  # Integer
            specific_heat=1,  # Integer
            thickness=1,  # Integer
            emissivity=1,  # Integer
        )
        result = mat.to_input_string()
        assert "CONDUCTIVITY = 1" in result
        assert "DENSITY = 1000" in result
        assert "SPECIFIC_HEAT = 1" in result
        assert "THICKNESS = 1" in result
        assert "EMISSIVITY = 1" in result

    def test_to_input_string_float_values(self):
        """Test input string generation with float values."""
        mat = Material(
            id="MAT2",
            material="Test Material",
            conductivity=0.123456,
            density=789.123,
            specific_heat=1.234567,
            thickness=0.009876,
            emissivity=0.85432,
        )
        result = mat.to_input_string()
        assert "CONDUCTIVITY = 0.123456" in result
        assert "DENSITY = 789.123" in result
        assert "SPECIFIC_HEAT = 1.234567" in result
        assert "THICKNESS = 0.009876" in result
        assert "EMISSIVITY = 0.85432" in result

    def test_to_input_string_default_values(self):
        """Test input string generation with default values omits None fields."""
        mat = Material(id="NM1", material="New Material 1")
        result = mat.to_input_string()
        assert result.startswith("&MATL")
        assert result.endswith("/\n")
        assert "ID = 'NM1'" in result
        assert "MATERIAL = 'New Material 1'" in result
        assert "EMISSIVITY = 0.9" in result
        # None fields must be omitted, not emitted as "None"
        assert "None" not in result
        assert "CONDUCTIVITY" not in result
        assert "DENSITY" not in result
        assert "SPECIFIC_HEAT" not in result
        assert "THICKNESS" not in result

    def test_to_input_string_special_characters_in_name(self):
        """Test input string generation with special characters in material name."""
        mat = Material(
            id="SPECIAL",
            material="Material-123 (Type A)",
            conductivity=0.5,
            density=1200,
            specific_heat=0.8,
            thickness=0.02,
            emissivity=0.85,
        )
        result = mat.to_input_string()
        assert "MATERIAL = 'Material-123 (Type A)'" in result

    @pytest.mark.parametrize(
        "prop,value",
        [
            pytest.param("conductivity", 0.0, id="zero-conductivity"),
            pytest.param("conductivity", -1.0, id="negative-conductivity"),
            pytest.param("density", 0.0, id="zero-density"),
            pytest.param("density", -500, id="negative-density"),
            pytest.param("specific_heat", 0.0, id="zero-specific-heat"),
            pytest.param("specific_heat", -0.5, id="negative-specific-heat"),
            pytest.param("thickness", 0.0, id="zero-thickness"),
            pytest.param("thickness", -0.01, id="negative-thickness"),
        ],
    )
    def test_invalid_physical_properties(self, prop, value):
        """Test that zero or negative physical properties raise ValueError."""
        kwargs = {"id": "ZERO", "material": "Test Material", prop: value}
        with pytest.raises(ValueError, match=f"{prop} must be positive"):
            Material(**kwargs)

    def test_emissivity_warning(self):
        """Test that emissivity values outside 0-1 raise a warning."""
        with pytest.warns(UserWarning, match="This may cause inaccurate results"):
            Material(
                id="TestMat",
                material="Test Material",
                emissivity=1.5,
            )

    def test_to_input_string_ends_correctly(self):
        """Test that input string ends with proper format."""
        mat = Material(id="NM1", material="New Material 1")
        result = mat.to_input_string()
        assert result.startswith("&MATL")
        assert result.endswith("/\n")

    @pytest.mark.parametrize(
        "mat_id",
        [
            pytest.param("", id="empty-string"),
            pytest.param("A", id="single-char"),
            pytest.param("1234567890123456", id="exact-16-chars"),
        ],
    )
    def test_id_validation_edge_cases(self, mat_id: str):
        """Test ID validation edge cases."""
        mat = Material(id=mat_id, material="Test Material")
        assert mat.id == mat_id

    def test_none_values_handling(self):
        """Test handling of None values in parameters."""
        mat = Material(
            id="TEST",
            material="Test Material",
            conductivity=None,
            density=None,
            specific_heat=None,
            thickness=None,
            emissivity=None,
        )

        # Should accept None values without error
        assert mat.material == "Test Material"
        assert mat.conductivity is None
        assert mat.density is None
        assert mat.specific_heat is None
        assert mat.thickness is None
        assert mat.emissivity is None

    # Tests for dunder methods
    def test_repr(self) -> None:
        """Test __repr__ method."""
        mat = Material(
            id="GYPSUM",
            material="Gypsum Wallboard",
            conductivity=0.17,
            density=930,
            specific_heat=1.09,
            thickness=0.016,
            emissivity=0.9,
        )

        repr_str = repr(mat)
        assert "Material(" in repr_str
        assert "id='GYPSUM'" in repr_str
        assert "material='Gypsum Wallboard'" in repr_str
        assert "conductivity=0.17" in repr_str
        assert "density=930" in repr_str

    def test_str(self) -> None:
        """Test __str__ method."""
        mat = Material(
            id="CONCRETE",
            material="Normal Weight Concrete",
            conductivity=1.2,
            density=2400,
            specific_heat=0.88,
            thickness=0.10,
            emissivity=0.94,
        )

        str_repr = str(mat)
        assert "Material 'CONCRETE'" in str_repr
        assert "Normal Weight Concrete" in str_repr
        assert "k=1.2" in str_repr
        assert "ρ=2400" in str_repr
        assert "c=0.88" in str_repr
        assert "t=0.1" in str_repr
        assert "ε=0.94" in str_repr

    def test_str_with_none_values(self) -> None:
        """Test __str__ method with None values."""
        mat = Material(
            id="INCOMPLETE",
            material="Incomplete Material",
            conductivity=None,
            density=None,
        )

        str_repr = str(mat)
        assert "Material 'INCOMPLETE'" in str_repr
        assert "Incomplete Material" in str_repr
        assert "k=None" in str_repr
        assert "ρ=None" in str_repr

    def test_getitem(self) -> None:
        """Test __getitem__ method."""
        mat = Material(
            id="WOOD",
            material="Oak Wood",
            conductivity=0.16,
            density=750,
            specific_heat=2.85,
            thickness=0.025,
            emissivity=0.9,
        )

        assert mat["id"] == "WOOD"
        assert mat["material"] == "Oak Wood"
        assert mat["conductivity"] == 0.16
        assert mat["density"] == 750
        assert mat["specific_heat"] == 2.85
        assert mat["thickness"] == 0.025
        assert mat["emissivity"] == 0.9

    def test_getitem_invalid_key(self) -> None:
        """Test __getitem__ method with invalid key."""
        mat = Material(id="STEEL", material="Steel Material")

        with pytest.raises(
            KeyError, match="Property 'invalid_key' not found in Material"
        ):
            mat["invalid_key"]

    def test_setitem(self) -> None:
        """Test __setitem__ method."""
        mat = Material(id="TEST_MAT", material="Test Material")

        # Test setting various properties
        mat["id"] = "NEW_MATERIAL"
        assert mat.id == "NEW_MATERIAL"

        mat["material"] = "New Material Description"
        assert mat.material == "New Material Description"

        mat["conductivity"] = 0.5
        assert mat.conductivity == 0.5

        mat["density"] = 1200
        assert mat.density == 1200

        mat["specific_heat"] = 1.5
        assert mat.specific_heat == 1.5

        mat["thickness"] = 0.05
        assert mat.thickness == 0.05

        mat["emissivity"] = 0.8
        assert mat.emissivity == 0.8

    def test_setitem_none_values(self) -> None:
        """Test __setitem__ method with None values."""
        mat = Material(id="TEST_MAT", material="Test Material")

        mat["material"] = None
        assert mat.material is None

        mat["conductivity"] = None
        assert mat.conductivity is None

        mat["density"] = None
        assert mat.density is None

    def test_setitem_invalid_key(self) -> None:
        """Test __setitem__ method with invalid key."""
        mat = Material(id="TEST_MAT", material="Test Material")

        with pytest.raises(KeyError, match="Cannot set 'invalid_key'"):
            mat["invalid_key"] = "value"


class TestMaterialSetItemValidation:
    """Test validation in __setitem__ to ensure data integrity."""

    @pytest.mark.parametrize(
        "invalid_id",
        [
            pytest.param("A" * 17, id="too-long"),
            pytest.param(123, id="not-a-string"),
        ],
    )
    def test_setitem_invalid_id(self, invalid_id):
        """Test that __setitem__ rejects invalid id values."""
        mat = Material(id="VALID", material="Concrete", conductivity=1.6, density=2400)
        with pytest.raises(TypeError, match="id must be a string"):
            mat["id"] = invalid_id

    def test_setitem_valid_id(self):
        """Test that __setitem__ accepts valid id change."""
        mat = Material(id="VALID", material="Concrete", conductivity=1.6, density=2400)
        mat["id"] = "NEW_ID"
        assert mat.id == "NEW_ID"

    def test_setitem_valid_conductivity(self):
        """Test that __setitem__ accepts valid conductivity change."""
        mat = Material(id="VALID", material="Concrete", conductivity=1.6, density=2400)
        mat["conductivity"] = 2.0
        assert mat.conductivity == 2.0

    def test_setitem_invalid_does_not_mutate_state(self):
        """Test that a failed __setitem__ rolls back to the previous value."""
        mat = Material(
            id="VALID_ID", material="Concrete", conductivity=1.6, density=2400
        )

        with pytest.raises(TypeError):
            mat["id"] = "A" * 17  # Too long

        assert mat.id == "VALID_ID"
