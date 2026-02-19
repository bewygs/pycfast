"""
Material thermal property definitions for CFAST simulations.

This module provides the MaterialProperties class for defining
thermophysical properties of materials used in CFAST simulations.
"""

from __future__ import annotations

from typing import Any

from .utils.namelist import NamelistRecord
from .utils.theme import build_card


class MaterialProperties:
    """
    Defines thermophysical properties of materials used for compartment surfaces or targets.

    CFAST and CEdit do not include predefined thermal properties for compartment materials.
    Thus, the user needs to define materials for use within a specific simulation. These may
    be from other simulations or input directly from reference sources or test results.
    The thermophysical properties are specified at one condition of temperature, humidity, etc.
    Only a single layer per boundary is allowed (some previous versions allowed up to three).

    Parameters
    ----------
    id : str
        A one-word (no more than 8 characters) unique identifier for the material. This
        identifier should not contain any spaces and is used in other CFAST inputs to
        identify the particular material referenced.
    material : str
        A descriptive name for the material.
    conductivity : float, optional
        Thermal conductivity for the material. Default units: kW/(m·°C) or kW/(m·K).
    specific_heat : float, optional
        Specific heat for the material. Default units: kJ/(kg·°C) or kJ/(kg·K).
    density : float, optional
        Density for the material. Default units: kg/m³.
    thickness : float, optional
        Thickness of the material. Note that if two materials with identical thermal
        properties but with different thicknesses are desired, two separate materials
        must be defined. Default units: m.
    emissivity : float, optional
        Emissivity of the material surface. This is the fraction of radiation that is
        absorbed by the material. Default units: none, default value: 0.9.

    Notes
    -----
    The thermophysical properties are specified at one condition of temperature, humidity, etc.
    Values are assumed constant (no temperature dependence). Responsibility for data accuracy
    lies with the user.

    Examples
    --------
    Create a gypsum wallboard material:

    >>> gypsum = MaterialProperties(
    ...     id="GYPSUM",
    ...     material="Gypsum Wallboard",
    ...     conductivity=0.17,
    ...     density=930,
    ...     specific_heat=1.09,
    ...     thickness=0.016,
    ...     emissivity=0.9,
    ... )
    >>> print(gypsum.id)
    GYPSUM
    """

    def __init__(
        self,
        id: str,
        material: str,
        conductivity: float | None = None,
        density: float | None = None,
        specific_heat: float | None = None,
        thickness: float | None = None,
        emissivity: float | None = 0.9,
    ):
        self.id = id
        self.material = material
        self.conductivity = conductivity
        self.density = density
        self.specific_heat = specific_heat
        self.thickness = thickness
        self.emissivity = emissivity

        self._validate()

    def _validate(self) -> None:
        """Validate the current state of the material property attributes.

        Raises
        ------
        TypeError
            If id is not a string or exceeds 16 characters.
        """
        if not isinstance(self.id, str) or len(self.id) > 16:
            raise TypeError("id must be a string with no more than 16 characters.")

    def __repr__(self) -> str:
        """Return a detailed string representation of the MaterialProperties."""
        return (
            f"MaterialProperties("
            f"id='{self.id}', material='{self.material}', "
            f"conductivity={self.conductivity}, density={self.density}, "
            f"specific_heat={self.specific_heat}, thickness={self.thickness}, "
            f"emissivity={self.emissivity}"
            f")"
        )

    def __str__(self) -> str:
        """Return a user-friendly string representation of the MaterialProperties."""
        return (
            f"Material '{self.id}' ({self.material}): "
            f"k={self.conductivity}, ρ={self.density}, c={self.specific_heat}, "
            f"t={self.thickness}, ε={self.emissivity}"
        )

    def _repr_html_(self) -> str:
        """Return an HTML representation for Jupyter/interactive environments."""
        body_html = f"""
            <div class="pycfast-card-grid">
                <div><strong>Conductivity:</strong> {getattr(self, "conductivity", "N/A")} W/m·K</div>
                <div><strong>Density:</strong> {getattr(self, "density", "N/A")} kg/m³</div>
                <div><strong>Specific Heat:</strong> {getattr(self, "specific_heat", "N/A")} kJ/kg·K</div>
                <div><strong>Thickness:</strong> {getattr(self, "thickness", "N/A")} m</div>
                <div><strong>Emissivity:</strong> {getattr(self, "emissivity", "N/A")}</div>
            </div>
        """

        return build_card(
            icon="🧱",
            gradient="linear-gradient(135deg, #2d3436, #636e72)",
            title=f"Material: {self.id}",
            subtitle=f"<strong>{getattr(self, 'material', 'Material')}</strong>",
            accent_color="#636e72",
            body_html=body_html,
        )

    def __getitem__(self, key: str) -> Any:
        """Get material property by name for dictionary-like access."""
        if not hasattr(self, key):
            raise KeyError(f"Property '{key}' not found in MaterialProperties.")
        return getattr(self, key)

    def __setitem__(self, key: str, value: Any) -> None:
        """Set material property by name for dictionary-like assignment.

        Validates the object state after setting the attribute to ensure
        all constraints are still satisfied.

        Raises
        ------
        KeyError
            If the property does not exist.
        TypeError
            If setting this value would violate object constraints.
        """
        if not hasattr(self, key):
            raise KeyError(
                f"Cannot set '{key}'. Property does not exist in MaterialProperties."
            )
        old_value = getattr(self, key)
        setattr(self, key, value)
        try:
            self._validate()
        except Exception:
            setattr(self, key, old_value)
            raise

    def to_input_string(self) -> str:
        """
        Generate CFAST input file string for this material.

        Returns
        -------
        str
            Formatted string ready for inclusion in CFAST input file.

        Examples
        --------
        >>> mat = MaterialProperties("GYPSUM", "Gypsum Board", 0.17, 930, 1.09, 0.016, 0.9)
        >>> print(mat.to_input_string().strip())
        &MATL ID = 'GYPSUM' MATERIAL = 'Gypsum Board' CONDUCTIVITY = 0.17 DENSITY = 930 SPECIFIC_HEAT = 1.09 THICKNESS = 0.016 EMISSIVITY = 0.9 /
        """
        return (
            NamelistRecord("MATL")
            .add_field("ID", self.id)
            .add_field("MATERIAL", self.material)
            .add_field("CONDUCTIVITY", self.conductivity)
            .add_field("DENSITY", self.density)
            .add_field("SPECIFIC_HEAT", self.specific_heat)
            .add_field("THICKNESS", self.thickness)
            .add_field("EMISSIVITY", self.emissivity)
            .build()
        )
