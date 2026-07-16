from __future__ import annotations

import pytest

from pycfast.visualization import Visualization

"""
Tests for the Visualization class.
"""


class TestVisualization:
    """Test class for Visualization."""

    def test_init_2d_slice(self):
        """Test initialization of a 2-D slice visualization."""
        viz = Visualization(
            viz_type="2-D",
            comp_id="ROOM1",
            plane="X",
            position=2.5,
        )
        assert viz.viz_type == "2-D"
        assert viz.comp_id == "ROOM1"
        assert viz.plane == "X"
        assert viz.position == 2.5
        assert viz.value is None

    def test_init_3d_slice(self):
        """Test initialization of a 3-D slice visualization."""
        viz = Visualization(viz_type="3-D", comp_id="ROOM1")
        assert viz.viz_type == "3-D"
        assert viz.comp_id == "ROOM1"
        assert viz.plane is None
        assert viz.position is None
        assert viz.value is None

    def test_init_isosurface(self):
        """Test initialization of an isosurface visualization."""
        viz = Visualization(viz_type="ISOSURFACE", value=305.0)
        assert viz.viz_type == "ISOSURFACE"
        assert viz.comp_id is None
        assert viz.value == 305.0

    def test_to_input_string_2d_slice(self):
        """Test input string generation for a 2-D slice."""
        viz = Visualization(viz_type="2-D", comp_id="ROOM1", plane="Y", position=1.2)
        result = viz.to_input_string()
        assert result.startswith("&SLCF")
        assert result.endswith("/\n")
        assert "COMP_ID = 'ROOM1'" in result
        assert "DOMAIN = '2-D'" in result
        assert "PLANE = 'Y'" in result
        assert "POSITION = 1.2" in result
        assert "None" not in result

    def test_to_input_string_2d_slice_all_compartments(self):
        """Test that COMP_ID is omitted when comp_id is None (all compartments)."""
        viz = Visualization(viz_type="2-D", plane="X", position=0.0)
        result = viz.to_input_string()
        assert result.startswith("&SLCF")
        assert "COMP_ID" not in result
        assert "DOMAIN = '2-D'" in result
        assert "PLANE = 'X'" in result
        assert "POSITION = 0.0" in result

    def test_to_input_string_3d_slice(self):
        """Test input string generation for a 3-D slice."""
        viz = Visualization(viz_type="3-D", comp_id="ROOM1")
        result = viz.to_input_string()
        assert result.startswith("&SLCF")
        assert result.endswith("/\n")
        assert "COMP_ID = 'ROOM1'" in result
        assert "DOMAIN = '3-D'" in result
        assert "PLANE" not in result
        assert "POSITION" not in result

    def test_to_input_string_isosurface(self):
        """Test input string generation for an isosurface."""
        viz = Visualization(viz_type="ISOSURFACE", value=305.0)
        result = viz.to_input_string()
        assert result.startswith("&ISOF")
        assert result.endswith("/\n")
        assert "VALUE = 305.0" in result
        assert "COMP_ID" not in result
        assert "DOMAIN" not in result

    def test_to_input_string_isosurface_with_compartment(self):
        """Test input string generation for an isosurface in a single compartment."""
        viz = Visualization(viz_type="ISOSURFACE", comp_id="ROOM1", value=100.0)
        result = viz.to_input_string()
        assert result.startswith("&ISOF")
        assert "COMP_ID = 'ROOM1'" in result
        assert "VALUE = 100.0" in result

    def test_slice_2d_classmethod(self):
        """Test the slice_2d class method."""
        viz = Visualization.slice_2d(plane="Z", position=2.3, comp_id="KITCHEN")
        assert isinstance(viz, Visualization)
        assert viz.viz_type == "2-D"
        assert viz.plane == "Z"
        assert viz.position == 2.3
        assert viz.comp_id == "KITCHEN"

    def test_slice_2d_classmethod_defaults(self):
        """Test the slice_2d class method default values."""
        viz = Visualization.slice_2d(plane="X")
        assert viz.position == 0.0
        assert viz.comp_id is None

    def test_slice_3d_classmethod(self):
        """Test the slice_3d class method."""
        viz = Visualization.slice_3d(comp_id="LIVING")
        assert isinstance(viz, Visualization)
        assert viz.viz_type == "3-D"
        assert viz.comp_id == "LIVING"

    def test_isosurface_classmethod(self):
        """Test the isosurface class method."""
        viz = Visualization.isosurface(value=250.0)
        assert isinstance(viz, Visualization)
        assert viz.viz_type == "ISOSURFACE"
        assert viz.value == 250.0
        assert viz.comp_id is None

    @pytest.mark.parametrize("plane", ["X", "Y", "Z"])
    def test_to_input_string_2d_with_different_planes(self, plane: str):
        """Test input string generation for 2-D slices with all valid planes."""
        viz = Visualization.slice_2d(plane=plane, position=1.0)
        result = viz.to_input_string()
        assert f"PLANE = '{plane}'" in result

    def test_init_invalid_viz_type(self):
        """Test that initialization fails with an invalid viz_type."""
        with pytest.raises(ValueError, match="must be one of"):
            Visualization(viz_type="4-D")

    def test_init_viz_type_not_str(self):
        """Test that initialization fails when viz_type is not a string."""
        with pytest.raises(TypeError, match="viz_type must be a str"):
            Visualization(viz_type=123)  # type: ignore[arg-type]

    @pytest.mark.parametrize("bad_id", ["", 42])
    def test_init_invalid_comp_id(self, bad_id: object):
        """Test that initialization fails with an invalid comp_id."""
        with pytest.raises(ValueError, match="comp_id must be a non-empty string"):
            Visualization(viz_type="3-D", comp_id=bad_id)  # type: ignore[arg-type]

    def test_init_2d_missing_plane(self):
        """Test that 2-D slice fails without a plane value."""
        with pytest.raises(ValueError, match="2-D slice requires a plane"):
            Visualization(viz_type="2-D", position=1.0)

    def test_init_2d_plane_not_str(self):
        """Test that 2-D slice fails when plane is not a string."""
        with pytest.raises(TypeError, match="plane must be a str"):
            Visualization(viz_type="2-D", plane=1, position=1.0)  # type: ignore[arg-type]

    def test_init_2d_invalid_plane(self):
        """Test that 2-D slice fails with an invalid plane."""
        with pytest.raises(ValueError, match="must be one of"):
            Visualization(viz_type="2-D", plane="W", position=1.0)

    def test_init_2d_missing_position(self):
        """Test that 2-D slice fails without a position value."""
        with pytest.raises(ValueError, match="2-D slice requires a position"):
            Visualization(viz_type="2-D", plane="X")

    def test_init_2d_position_not_numeric(self):
        """Test that 2-D slice fails when position is not numeric."""
        with pytest.raises(TypeError, match="position must be a float"):
            Visualization(viz_type="2-D", plane="X", position="middle")  # type: ignore[arg-type]

    def test_init_2d_negative_position(self):
        """Test that 2-D slice fails with a negative position."""
        with pytest.raises(ValueError, match="must be >= 0"):
            Visualization(viz_type="2-D", plane="X", position=-1.0)

    def test_init_isosurface_missing_value(self):
        """Test that isosurface fails without a value."""
        with pytest.raises(ValueError, match="isosurface requires a value"):
            Visualization(viz_type="ISOSURFACE")

    def test_init_isosurface_value_not_numeric(self):
        """Test that isosurface fails when value is not numeric."""
        with pytest.raises(TypeError, match="value must be a float"):
            Visualization(viz_type="ISOSURFACE", value="hot")  # type: ignore[arg-type]

    def test_init_2d_with_value_warning(self):
        """Test that a warning is raised when value is provided for a 2-D slice."""
        with pytest.warns(UserWarning, match="value should be None for 2-D"):
            Visualization(viz_type="2-D", plane="X", position=1.0, value=300.0)

    def test_init_3d_with_extra_fields_warning(self):
        """Test that a warning is raised when extra fields are provided for a 3-D slice."""
        with pytest.warns(UserWarning, match="should be None for 3-D"):
            Visualization(viz_type="3-D", plane="X")

    def test_init_isosurface_with_extra_fields_warning(self):
        """Test that a warning is raised when plane/position are provided for an isosurface."""
        with pytest.warns(UserWarning, match="should be None for isosurfaces"):
            Visualization(viz_type="ISOSURFACE", value=300.0, position=1.0)

    def test_to_input_string_3d_ignores_extra_fields(self):
        """Test that 3-D slices don't include PLANE/POSITION even when provided."""
        with pytest.warns(UserWarning):
            viz = Visualization(viz_type="3-D", plane="X", position=1.0)
        result = viz.to_input_string()
        assert "PLANE" not in result
        assert "POSITION" not in result

    # Tests for dunder methods
    def test_repr(self) -> None:
        """Test __repr__ method."""
        viz = Visualization(viz_type="2-D", comp_id="ROOM1", plane="X", position=2.5)

        repr_str = repr(viz)
        assert "Visualization(" in repr_str
        assert "viz_type='2-D'" in repr_str
        assert "comp_id='ROOM1'" in repr_str
        assert "plane='X'" in repr_str
        assert "position=2.5" in repr_str
        assert "value=None" in repr_str

    def test_repr_isosurface(self) -> None:
        """Test __repr__ method for isosurface."""
        viz = Visualization.isosurface(value=305.0)

        repr_str = repr(viz)
        assert "Visualization(" in repr_str
        assert "viz_type='ISOSURFACE'" in repr_str
        assert "comp_id=None" in repr_str
        assert "value=305.0" in repr_str

    def test_str_2d_slice(self) -> None:
        """Test __str__ method for a 2-D slice."""
        viz = Visualization.slice_2d(plane="X", position=2.5, comp_id="ROOM1")

        str_repr = str(viz)
        assert "Visualization (2-D):" in str_repr
        assert "plane X at 2.5 m" in str_repr
        assert "in ROOM1" in str_repr

    def test_str_3d_slice_all_compartments(self) -> None:
        """Test __str__ method for a 3-D slice in all compartments."""
        viz = Visualization.slice_3d()

        str_repr = str(viz)
        assert "Visualization (3-D):" in str_repr
        assert "in all compartments" in str_repr

    def test_str_isosurface(self) -> None:
        """Test __str__ method for an isosurface."""
        viz = Visualization.isosurface(value=305.0)

        str_repr = str(viz)
        assert "Visualization (ISOSURFACE):" in str_repr
        assert "305.0 °C" in str_repr

    def test_setattr_updates_attributes(self) -> None:
        """Test that attribute assignment updates the instance."""
        viz = Visualization.slice_2d(plane="X", position=1.0, comp_id="ROOM1")

        viz.plane = "Y"
        assert viz.plane == "Y"

        viz.position = 2.0
        assert viz.position == 2.0

        viz.comp_id = None
        assert viz.comp_id is None

    def test_setattr_invalid_raises(self) -> None:
        """Setting an invalid value triggers validation and raises."""
        viz = Visualization.slice_2d(plane="X", position=1.0)

        with pytest.raises(ValueError):
            viz.plane = "INVALID_PLANE"
