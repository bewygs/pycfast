from __future__ import annotations

import pytest

from pycfast.material import Material

"""
Tests for the Material class.
"""

_BASE_KWARGS: dict = {
    "id": "BASE",
    "material": "Base Material",
    "conductivity": 1.0,
    "density": 1000,
    "specific_heat": 1.0,
    "thickness": 0.01,
}


class TestMaterial:
    """Test class for Material."""

    def test_init_with_all_parameters(self):
        """Test initialization with all parameters, including default emissivity."""
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

        # emissivity defaults to 0.9
        mat_no_emissivity = Material(
            id="GYPSUM",
            material="Gypsum Wallboard",
            conductivity=0.17,
            density=930,
            specific_heat=1.09,
            thickness=0.016,
        )
        assert mat_no_emissivity.emissivity == 0.9

    def test_init_invalid_id_type(self):
        """Test that initialization fails with non-string ID."""
        with pytest.raises(TypeError, match="id must be a string"):
            Material(id=123, **{k: v for k, v in _BASE_KWARGS.items() if k != "id"})  # type: ignore

    def test_init_invalid_id_length(self):
        """Test that initialization fails with ID too long."""
        with pytest.raises(
            ValueError, match="id must be no more than 16 characters long"
        ):
            Material(
                id="THIS_ID_IS_TOO_LONG_FOR_CFAST",
                **{k: v for k, v in _BASE_KWARGS.items() if k != "id"},
            )

    def test_id_length_warning(self):
        """Test that id between 9 and 16 characters warns about CFAST documented limit."""
        with pytest.warns(UserWarning, match="8-character limit"):
            Material(
                id="EXACTLY_16_CHARS",
                **{k: v for k, v in _BASE_KWARGS.items() if k != "id"},
            )

    def test_init_invalid_material_type(self):
        """Test that initialization fails with non-string material."""
        with pytest.raises(TypeError, match="material must be a string"):
            Material(
                id="TEST",
                material=123,
                conductivity=1.0,
                density=1000,
                specific_heat=1.0,
                thickness=0.01,
            )  # type: ignore

    def test_to_input_string(self):
        """Test input string generation: format, all fields present, special characters in name."""
        mat = Material(
            id="GYPSUM",
            material="Gypsum Board (5/8 in)",
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
        assert "MATERIAL = 'Gypsum Board (5/8 in)'" in result
        assert "CONDUCTIVITY = 0.17" in result
        assert "DENSITY = 930" in result
        assert "SPECIFIC_HEAT = 1.09" in result
        assert "THICKNESS = 0.016" in result
        assert "EMISSIVITY = 0.9" in result
        assert "None" not in result

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
        kwargs = {**_BASE_KWARGS, prop: value}
        with pytest.raises(ValueError, match=f"{prop} must be positive"):
            Material(**kwargs)

    def test_emissivity_warning(self):
        """Test that emissivity values outside 0-1 raise a warning."""
        with pytest.warns(UserWarning, match="This may cause inaccurate results"):
            Material(**_BASE_KWARGS, emissivity=1.5)

    @pytest.mark.parametrize(
        "mat_id",
        [
            pytest.param("", id="empty-string"),
            pytest.param("A", id="single-char"),
            pytest.param("EXACTLY8", id="exact-8-chars"),
        ],
    )
    def test_id_validation_valid_cases(self, mat_id: str):
        """Test ID validation for valid cases that produce no warning."""
        mat = Material(
            id=mat_id, **{k: v for k, v in _BASE_KWARGS.items() if k != "id"}
        )
        assert mat.id == mat_id

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
        mat = Material(**_BASE_KWARGS)

        with pytest.raises(
            KeyError, match="Property 'invalid_key' not found in Material"
        ):
            mat["invalid_key"]

    def test_setitem(self) -> None:
        """Test __setitem__ method."""
        mat = Material(**_BASE_KWARGS)

        mat["id"] = "NEW_MAT"
        assert mat.id == "NEW_MAT"

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

    def test_setitem_invalid_key(self) -> None:
        """Test __setitem__ method with invalid key."""
        mat = Material(**_BASE_KWARGS)

        with pytest.raises(KeyError, match="Cannot set 'invalid_key'"):
            mat["invalid_key"] = "value"


class TestMaterialSetItemValidation:
    """Test validation in __setitem__ to ensure data integrity."""

    @pytest.fixture
    def mat(self) -> Material:
        return Material(**_BASE_KWARGS)

    @pytest.mark.parametrize(
        "invalid_id, expected_exc, expected_match",
        [
            pytest.param(
                "A" * 17,
                ValueError,
                "id must be no more than 16 characters long",
                id="too-long",
            ),
            pytest.param(123, TypeError, "id must be a string", id="not-a-string"),
        ],
    )
    def test_setitem_invalid_id(self, mat, invalid_id, expected_exc, expected_match):
        """Test that __setitem__ rejects invalid id values."""
        with pytest.raises(expected_exc, match=expected_match):
            mat["id"] = invalid_id

    def test_setitem_valid_id(self, mat):
        """Test that __setitem__ accepts valid id change."""
        mat["id"] = "NEW_ID"
        assert mat.id == "NEW_ID"

    def test_setitem_valid_conductivity(self, mat):
        """Test that __setitem__ accepts valid conductivity change."""
        mat["conductivity"] = 2.0
        assert mat.conductivity == 2.0

    def test_setitem_invalid_does_not_mutate_state(self, mat):
        """Test that a failed __setitem__ rolls back to the previous value."""
        with pytest.raises(ValueError):
            mat["id"] = "A" * 17  # Too long

        assert mat.id == "BASE"
