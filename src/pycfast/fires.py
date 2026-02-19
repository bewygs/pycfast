"""
Fire definition module for CFAST simulations.

This module provides the Fires class for defining fire sources in a
compartment. Fires are characterized by their heat release rate over time,
chemical composition, and physical properties.
"""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

from .utils.namelist import NamelistRecord
from .utils.theme import build_card


class Fires:
    """
    Represents a fire source in a CFAST simulation.

    A fire in CFAST is specified via a time-dependent heat release rate (HRR). The
    specified heat of combustion is used to calculate the mass loss rate of fuel,
    from which the production rate of combustion products can be calculated using
    specified product yields. The heat release and the corresponding product generation
    rates go to zero when the lower oxygen limit is reached, and are replaced by the
    appropriate production rate of unburned fuel gas which is transported from zone
    to zone until there is sufficient oxygen and a high enough temperature to support
    combustion. The model can simulate multiple fires in one or more compartments. These
    fires are treated as totally separate entities, with no interaction of the plumes.
    These fires can be ignited at a prescribed time, or when a corresponding target reaches a
    specified temperature or heat flux. Fires in CFAST are defined in two parts: a
    "Fire Definition" that specifies the fuel composition, heat release rate, and
    species yields for the fire, and a "Fire Instance" that specifies the placement of
    a defined fire within a compartment in the simulation. A single fire definition may
    be associated with more than one fire instance in a simulation if desired. The
    combustion model is defined by a one-step reaction where burning fuels in CFAST
    are assumed to be hydrocarbon fuels that contain at least carbon and hydrogen and
    optionally oxygen, nitrogen, and chlorine. All of the specified nitrogen and chlorine
    is assumed to completely react to form HCN and HCl. Fire properties are linearly
    interpolated between specified time points. If the simulation time is longer than
    the total duration of the fire, the final values specified for the fire are
    continued until the end of the simulation.

    Parameters
    ----------
    id : str
        The selected name must be unique (i.e., not the same as another fire instance
        in the same simulation).
    comp_id : str
        Name of the compartment where the fire occurs.
    fire_id : str
        The selected name must be unique (i.e., not the same as another fire definition
        in the same simulation). IDs for fire definitions can be the same as ones for
        fire instances.
    location : list[float]
        Position of the center of the base of the fire relative to the front left corner
        of the compartment. Format: [x, y]. Default units: m, default value: compartment center.
    ignition_criterion : str, optional
        The time of ignition can be controlled by a user-specified time, or by a
        user-specified target's surface temperature or incident heat flux.
        Options: "TIME", "TEMPERATURE", "FLUX".
    set_point : float, optional
        The critical value at which ignition will occur. If it is less than or equal
        to zero, the default value of zero is taken. Can be temperature (°C) or flux
        (kW/m²) depending on criterion.
    device_id : str, optional
        User-specified target used to calculate surface temperature or incident heat
        flux to ignite fire. Target is typically placed at the base of the fire to be ignited.
    carbon : float
        The number of carbon atoms in the fuel molecule. Burning fuels in CFAST are
        assumed to be hydrocarbon fuels that contain at least carbon and hydrogen.
        Default value: 1.
    chlorine : float
        The number of chlorine atoms in the fuel molecule. All of the specified chlorine
        is assumed to completely react to form HCl. Default value: 0.
    hydrogen : float
        The number of hydrogen atoms in the fuel molecule. Burning fuels in CFAST are
        assumed to be hydrocarbon fuels that contain at least carbon and hydrogen.
        Default value: 4.
    nitrogen : float
        The number of nitrogen atoms in the fuel molecule. All of the specified nitrogen
        is assumed to completely react to form HCN. Default value: 0.
    oxygen : float
        The number of oxygen atoms in the fuel molecule. Default value: 0.
    heat_of_combustion : float
        The energy released per unit mass of fuel consumed. Default units: kJ/kg,
        default value: 50000 kJ/kg.
    radiative_fraction : float
        The fraction of the combustion energy that is emitted in the form of thermal
        radiation. Default units: none, default value: 0.35.
    data_table : list[list[float]], np.ndarray, or pd.DataFrame
        Time-dependent fire properties with columns for TIME, HRR, HEIGHT, AREA,
        CO_YIELD, SOOT_YIELD, HCN_YIELD, HCL_YIELD, TRACE_YIELD. Properties are linearly
        interpolated between specified points. Each row must contain exactly 9 values
        corresponding to the LABELS columns.

    Examples
    --------
    Create a simple growing fire:

    >>> fire_data = [
    ...     [0, 0, 0.5, 0.1, 0.01, 0.01, 0, 0, 0],      # t=0s, no heat release
    ...     [60, 100, 0.5, 0.5, 0.01, 0.01, 0, 0, 0],   # t=60s, 100 kW
    ...     [300, 500, 1.0, 1.0, 0.01, 0.01, 0, 0, 0]   # t=300s, 500 kW peak
    ... ]
    >>> fire = Fires(
    ...     id="FIRE1",
    ...     comp_id="ROOM1",
    ...     fire_id="POLYURETHANE",
    ...     location=[2.0, 2.0],           # Center of 4x4m room
    ...     carbon=27, hydrogen=36, oxygen=2, nitrogen=2, chlorine=0,
    ...     heat_of_combustion=23600,      # kJ/kg for polyurethane
    ...     radiative_fraction=0.35,      # 35% radiant fraction
    ...     data_table=fire_data
    ... )

    Create a fire with target-based ignition:

    >>> steady_fire = Fires(
    ...     id="IGNITED_FIRE",
    ...     comp_id="BEDROOM",
    ...     fire_id="WOOD",
    ...     location=[1.5, 2.0],           # Near bed location
    ...     ignition_criterion="TEMPERATURE",
    ...     set_point=200,                 # Ignite at 200°C
    ...     device_id="BED_TARGET",        # Temperature measured at bed
    ...     carbon=1, hydrogen=4, oxygen=0, nitrogen=0, chlorine=0,
    ...     heat_of_combustion=50000,      # Default combustion heat
    ...     radiative_fraction=0.35,      # Default radiant fraction
    ...     data_table=[[0, 1000, 0, 1.0, 0.01, 0.01, 0, 0, 0]]  # Steady 1 MW
    ... )
    """

    LABELS = [
        "TIME",
        "HRR",
        "HEIGHT",
        "AREA",
        "CO_YIELD",
        "SOOT_YIELD",
        "HCN_YIELD",
        "HCL_YIELD",
        "TRACE_YIELD",
    ]

    def __init__(
        self,
        id: str,
        comp_id: str,
        fire_id: str,
        location: list[float],
        ignition_criterion: str | None = None,
        set_point: float | None = None,
        device_id: str | None = None,
        carbon: float = 1,
        chlorine: float = 0,
        hydrogen: float = 4,
        nitrogen: float = 0,
        oxygen: float = 0,
        heat_of_combustion: float = 50000,
        radiative_fraction: float = 0.35,
        data_table: list[list[float]] | np.ndarray | pd.DataFrame | None = None,
    ):
        self.id = id
        self.comp_id = comp_id
        self.fire_id = fire_id
        self.location = location
        self.ignition_criterion = ignition_criterion
        self.set_point = set_point
        self.device_id = device_id
        self.carbon = carbon
        self.chlorine = chlorine
        self.hydrogen = hydrogen
        self.nitrogen = nitrogen
        self.oxygen = oxygen
        self.heat_of_combustion = heat_of_combustion
        self.radiative_fraction = radiative_fraction
        self.data_table = self._process_data_table(data_table)

        self._validate()

    def _validate(self) -> None:
        """Validate the current state of the fire attributes.

        Raises
        ------
        ValueError
            If any attribute violates the constraints.
        """
        if len(self.location) != 2:
            raise ValueError("Location must be a list of two floats [x, y].")

    def __repr__(self) -> str:
        """Return a detailed string representation of the Fires."""
        location_str = f"[{', '.join(map(str, self.location))}]"
        data_rows = len(self.data_table) if self.data_table else 0

        return (
            f"Fires("
            f"id='{self.id}', comp_id='{self.comp_id}', fire_id='{self.fire_id}', "
            f"location={location_str}, "
            f"heat_of_combustion={self.heat_of_combustion}, "
            f"radiative_fraction={self.radiative_fraction}, "
            f"data_rows={data_rows}"
            f")"
        )

    def __str__(self) -> str:
        """Return a user-friendly string representation of the Fires."""
        location_str = f"({self.location[0]}, {self.location[1]})"

        peak_hrr: float = 0
        duration: float = 0
        if self.data_table:
            hrr_values = [
                row[1] for row in self.data_table if len(row) > 1
            ]  # HRR is column 1
            time_values = [
                row[0] for row in self.data_table if len(row) > 0
            ]  # TIME is column 0
            peak_hrr = max(hrr_values) if hrr_values else 0
            duration = max(time_values) if time_values else 0

        fire_info = f"Fire '{self.id}' ({self.fire_id})"
        details = []

        if peak_hrr > 0:
            if peak_hrr >= 1000000:  # >= 1 MW
                details.append(f"peak: {peak_hrr / 1000000:.1f} MW")
            elif peak_hrr >= 1000:  # >= 1 kW
                details.append(f"peak: {peak_hrr / 1000:.0f} kW")
            else:
                details.append(f"peak: {peak_hrr:.0f} W")

        if duration > 0:
            if duration >= 3600:  # >= 1 hour
                details.append(f"duration: {duration / 3600:.1f}h")
            elif duration >= 60:  # >= 1 minute
                details.append(f"duration: {duration / 60:.0f}min")
            else:
                details.append(f"duration: {duration:.0f}s")

        details.append(f"χr: {self.radiative_fraction}")

        details_str = f" ({', '.join(details)})" if details else ""

        return f"{fire_info} in '{self.comp_id}' at {location_str}{details_str}"

    def _repr_html_(self) -> str:
        """Return an HTML representation for Jupyter/interactive environments."""
        location_str = f"({self.location[0]}, {self.location[1]})"

        # Calculate peak HRR and duration for display
        peak_hrr = 0.0
        duration = 0.0
        data_points = 0
        if self.data_table:
            hrr_values = [row[1] for row in self.data_table if len(row) > 1]
            time_values = [row[0] for row in self.data_table if len(row) > 0]
            peak_hrr = max(hrr_values) if hrr_values else 0
            duration = max(time_values) if time_values else 0
            data_points = len(self.data_table)

        # Format HRR display
        if peak_hrr >= 1000000:  # >= 1 MW
            hrr_display = f"{peak_hrr / 1000000:.1f} MW"
        elif peak_hrr >= 1000:  # >= 1 kW
            hrr_display = f"{peak_hrr / 1000:.0f} kW"
        else:
            hrr_display = f"{peak_hrr:.0f} W"

        # Format duration display
        if duration >= 3600:  # >= 1 hour
            duration_display = f"{duration / 3600:.1f}h"
        elif duration >= 60:  # >= 1 minute
            duration_display = f"{duration / 60:.0f}min"
        else:
            duration_display = f"{duration:.0f}s"

        body_html = f"""
            <div class="pycfast-card-grid">
                <div><strong>Peak HRR:</strong> {hrr_display}</div>
                <div><strong>Duration:</strong> {duration_display}</div>
                <div><strong>Location:</strong> {location_str}</div>
                <div><strong>χᵣ:</strong> {self.radiative_fraction}</div>
                <div><strong>ΔHc:</strong> {self.heat_of_combustion} kJ/kg</div>
                <div><strong>Data points:</strong> {data_points}</div>
            </div>
            <details class="pycfast-inline-detail">
                <summary>Chemical Composition</summary>
                <div class="pycfast-detail-content">
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(80px, 1fr)); gap: 5px;">
                        <div>C: {getattr(self, "carbon", 0)}</div>
                        <div>H: {getattr(self, "hydrogen", 0)}</div>
                        <div>O: {getattr(self, "oxygen", 0)}</div>
                        <div>N: {getattr(self, "nitrogen", 0)}</div>
                        <div>Cl: {getattr(self, "chlorine", 0)}</div>
                    </div>
                </div>
            </details>
        """

        return build_card(
            icon="🔥",
            gradient="linear-gradient(135deg, #ff4757, #ff3838)",
            title=f"Fire: {self.id}",
            subtitle=f"<strong>{self.fire_id}</strong> in compartment <strong>{self.comp_id}</strong>",
            accent_color="#ff4757",
            body_html=body_html,
        )

    def __getitem__(self, key: str) -> Any:
        """Get fire property by name for dictionary-like access."""
        if not hasattr(self, key):
            raise KeyError(f"Property '{key}' not found in Fires.")
        return getattr(self, key)

    def __setitem__(self, key: str, value: Any) -> None:
        """Set fire property by name for dictionary-like assignment.

        Validates the object state after setting the attribute to ensure
        all constraints are still satisfied.

        Raises
        ------
        KeyError
            If the property does not exist.
        ValueError
            If setting this value would violate object constraints.
        """
        if not hasattr(self, key):
            raise KeyError(f"Cannot set '{key}'. Property does not exist in Fires.")
        old_value = getattr(self, key)
        setattr(self, key, value)
        try:
            self._validate()
        except Exception:
            setattr(self, key, old_value)
            raise

    def to_input_string(self) -> str:
        """
        Generate CFAST input file string for this fire.

        Returns
        -------
        str
            Formatted string ready for inclusion in CFAST input file.

        Examples
        --------
        >>> fire = Fires(id="FIRE1", comp_id="ROOM1", fire_id="WOOD",
        ...               location=[1.0, 1.0], data_table=[[0, 1000, 0.5, 1.0, 0.01, 0.01, 0, 0, 0]])
        >>> print(fire.to_input_string())
        &FIRE ID = 'FIRE1' COMP_ID = 'ROOM1' FIRE_ID = 'WOOD' LOCATION = 1.0, 1.0 /
        &CHEM ID = 'WOOD' CARBON = 1 ... /
        &TABL ID = 'WOOD' LABELS = 'TIME', 'HRR', ... /
        &TABL ID = 'WOOD' DATA = 0, 1000, 0.5, 1.0, 0.01, 0.01, 0, 0, 0 /
        """
        # &FIRE record
        fire_rec = NamelistRecord("FIRE")
        fire_rec.add_field("ID", self.id)
        fire_rec.add_field("COMP_ID", self.comp_id)
        fire_rec.add_field("FIRE_ID", self.fire_id)
        fire_rec.add_list_field("LOCATION", self.location)

        if self.ignition_criterion and self.ignition_criterion != "TIME":
            fire_rec.add_field("IGNITION_CRITERION", self.ignition_criterion)
        if self.ignition_criterion is not None:
            fire_rec.add_field("DEVC_ID", self.device_id)
            fire_rec.add_numeric_field("SETPOINT", self.set_point)

        input_str = fire_rec.build()

        # &CHEM record
        chem_rec = (
            NamelistRecord("CHEM")
            .add_field("ID", self.fire_id)
            .add_field("CARBON", self.carbon)
            .add_field("CHLORINE", self.chlorine)
            .add_field("HYDROGEN", self.hydrogen)
            .add_field("NITROGEN", self.nitrogen)
            .add_field("OXYGEN", self.oxygen)
            .add_field("HEAT_OF_COMBUSTION", self.heat_of_combustion)
            .add_field("RADIATIVE_FRACTION", self.radiative_fraction)
            .build()
        )
        input_str += chem_rec

        # &TABL LABELS record
        labels_rec = (
            NamelistRecord("TABL")
            .add_field("ID", self.fire_id)
            .add_list_field("LABELS", self.LABELS)
            .build()
        )
        input_str += labels_rec

        # &TABL DATA records
        if self.data_table:
            for row in self.data_table:
                data_rec = (
                    NamelistRecord("TABL")
                    .add_field("ID", self.fire_id)
                    .add_list_field("DATA", row)
                    .build()
                )
                input_str += data_rec

        return input_str

    def to_dataframe(self) -> pd.DataFrame:
        """
        Convert fire data table to pandas DataFrame with proper column labels.

        Returns
        -------
        pd.DataFrame
            DataFrame with columns matching LABELS for easy analysis and plotting.

        Examples
        --------
        >>> fire = Fires(id="FIRE1", comp_id="ROOM1", fire_id="WOOD",
        ...               location=[1.0, 1.0],
        ...               data_table=[[0, 1000, 0.5, 1.0, 0.01, 0.01, 0, 0, 0]])
        >>> df = fire.to_dataframe()
        >>> df['HRR'].max()  # Find peak heat release rate
        1000.0
        """
        return pd.DataFrame(self.data_table, columns=self.LABELS)

    def _process_data_table(
        self, data_table: list[list[float]] | np.ndarray | pd.DataFrame | None
    ) -> list[list[float]]:
        """
        Process and validate data_table input from various formats.

        Parameters
        ----------
        data_table : list[list[float]], np.ndarray, pd.DataFrame, or None
            Fire data in various formats. Must have shape (n_rows, 9) where columns
            correspond to LABELS: ["TIME", "HRR", "HEIGHT", "AREA", "CO_YIELD",
            "SOOT_YIELD", "HCN_YIELD", "HCL_YIELD", "TRACE_YIELD"].

        Returns
        -------
        list[list[float]]
            Standardized data table as list of lists.
        """
        if data_table is None:
            return [[0, 0, 0, 0, 0, 0, 0, 0, 0]]

        if isinstance(data_table, pd.DataFrame):
            if list(data_table.columns) == self.LABELS:
                array_data = data_table.values
            elif data_table.shape[1] == len(self.LABELS):
                array_data = data_table.values
            else:
                raise ValueError(
                    f"DataFrame must have {len(self.LABELS)} columns. "
                    f"Got {data_table.shape[1]} columns. "
                    f"Expected columns: {self.LABELS}"
                )

        elif isinstance(data_table, np.ndarray):
            if data_table.ndim != 2:
                raise ValueError("NumPy array must be 2-dimensional.")
            if data_table.shape[1] != len(self.LABELS):
                raise ValueError(
                    f"NumPy array must have exactly {len(self.LABELS)} columns."
                )
            array_data = data_table

        elif isinstance(data_table, list):
            if not data_table or len(data_table) < 1:
                raise ValueError("data_table must contain at least one row.")
            array_data = np.array(data_table)

        else:
            raise TypeError(
                "data_table must be a list of lists, NumPy array, pandas DataFrame, or None."
            )

        if array_data.shape[1] != len(self.LABELS):
            raise ValueError(
                f"data_table must have exactly {len(self.LABELS)} columns. "
                f"Got {array_data.shape[1]} columns. "
                f"Expected columns: {self.LABELS}"
            )

        try:
            array_data = array_data.astype(float)
        except (ValueError, TypeError) as e:
            raise ValueError("All values in data_table must be numeric.") from e

        # Type cast to satisfy mypy - we know this is list[list[float]] due to validation above
        result: list[list[float]] = array_data.tolist()
        return result
