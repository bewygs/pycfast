"""
Material thermal property definitions for CFAST simulations.

This module provides the Material class for defining
thermophysical properties of materials used in CFAST simulations.
"""

from __future__ import annotations

import warnings

from ._base_component import CFASTComponent
from .utils.namelist import NamelistRecord


class Material(CFASTComponent):
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
    conductivity : float
        Thermal conductivity for the material. Default units: kW/(m·°C) or kW/(m·K).
    specific_heat : float
        Specific heat for the material. Default units: kJ/(kg·°C) or kJ/(kg·K).
    density : float
        Density for the material. Default units: kg/m³.
    thickness : float
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

    >>> gypsum = Material(
    ...     id="GYPSUM",
    ...     material="Gypsum Wallboard",
    ...     conductivity=0.17,
    ...     density=930,
    ...     specific_heat=1.09,
    ...     thickness=0.016,
    ...     emissivity=0.9,
    ... )
    """

    def __init__(
        self,
        id: str,
        material: str,
        conductivity: float,
        density: float,
        specific_heat: float,
        thickness: float,
        emissivity: float = 0.9,
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
            If id or material is not a string.
        ValueError
            If id is longer than 16 characters, or if conductivity, density,
            specific_heat, or thickness is not positive.

        Warns
        -----
        UserWarning
            If id is longer than 8 characters (exceeds the CFAST documented limit).
            If emissivity is outside [0, 1].
        """
        if not isinstance(self.id, str):
            raise TypeError("id must be a string.")
        if len(self.id) > 16:
            raise ValueError(
                f"Material '{self.id}': id must be no more than 16 characters long."
            )
        if len(self.id) > 8:
            warnings.warn(
                f"Material '{self.id}': id exceeds the 8-character limit documented "
                "by CFAST. This may cause issues with some CFAST versions.",
                UserWarning,
                stacklevel=2,
            )
        if not isinstance(self.material, str):
            raise TypeError(f"Material '{self.id}': material must be a string.")

        for prop, val in (
            ("conductivity", self.conductivity),
            ("density", self.density),
            ("specific_heat", self.specific_heat),
            ("thickness", self.thickness),
        ):
            if val <= 0:
                raise ValueError(
                    f"Material '{self.id}': {prop} must be positive, got {val}."
                )

        if not 0.0 <= self.emissivity <= 1.0:
            warnings.warn(
                f"Material '{self.id}': emissivity={self.emissivity} is outside "
                "[0, 1]. This may cause inaccurate results.",
                UserWarning,
                stacklevel=2,
            )

    def __repr__(self) -> str:
        """Return a detailed string representation of the Material."""
        return (
            f"Material("
            f"id='{self.id}', material='{self.material}', "
            f"conductivity={self.conductivity}, density={self.density}, "
            f"specific_heat={self.specific_heat}, thickness={self.thickness}, "
            f"emissivity={self.emissivity}"
            ")"
        )

    def __str__(self) -> str:
        """Return a user-friendly string representation of the Material."""
        return (
            f"Material '{self.id}' ({self.material}): "
            f"k={self.conductivity}, ρ={self.density}, c={self.specific_heat}, "
            f"t={self.thickness}, ε={self.emissivity}"
        )

    def to_input_string(self) -> str:
        """
        Generate CFAST input file string for this material.

        Returns
        -------
        str
            Formatted string ready for inclusion in CFAST input file.

        Examples
        --------
        >>> mat = Material("GYPSUM", "Gypsum Board", 0.17, 930, 1.09, 0.016, 0.9)
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
