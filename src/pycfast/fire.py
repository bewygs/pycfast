"""
Fire definition module for CFAST simulations.

This module provides the FireDefinition class for defining the fuel chemistry and
heat release rate, and the Fire class for adding a fire to a compartment.
"""

from __future__ import annotations

import warnings
from typing import Any

import numpy as np
import pandas as pd

from ._base_component import CFASTComponent
from .utils.namelist import NamelistRecord


class _Unset:
    """Sentinel type for "argument not supplied" on Fire.__init__."""

    def __repr__(self) -> str:
        return "<unset>"


# Typed Any so the float-typed chemistry parameters can default to it.
_UNSET: Any = _Unset()


class FireDefinition(CFASTComponent):
    """
    A reusable CFAST fire definition for the chemistry (``&CHEM``) and table (``&TABL``) sections.

    Fires in CFAST are defined in two parts: a "Fire Definition" that specifies the
    fuel composition, heat release rate, and species yields for the fire, and a
    "Fire Instance" (:class:`Fire`) that specifies the placement of a defined fire
    within a compartment in the simulation.

    Most of the time, you don't need to build a FireDefinition by yourself. Passing
    the chemistry arguments directly to :class:`Fire` creates one behind the scenes.
    Create one explicitly when several fires share the same definition.

    Parameters
    ----------
    fire_id : str
        The selected name must be unique (i.e., not the same as another fire definition
        in the same simulation). IDs for fire definitions can be the same as ones for
        fire instances.
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
    data_table : list[list[float]], dict, np.ndarray, or pd.DataFrame, optional
        Time-dependent fire properties with columns for TIME, HRR, HEIGHT, AREA,
        CO_YIELD, SOOT_YIELD, HCN_YIELD, HCL_YIELD, TRACE_YIELD. Properties are linearly
        interpolated between specified points. Defaults to ``DEFAULT_DATA_TABLE``
        (a single all-zero row) when not provided.

        .. list-table::
           :header-rows: 1
           :widths: 10 25 15 50

           * - Index
             - Name
             - Unit
             - Description
           * - 0
             - ``TIME``
             - s
             - Simulation time
           * - 1
             - ``HRR``
             - kW
             - Heat release rate
           * - 2
             - ``HEIGHT``
             - m
             - Flame height
           * - 3
             - ``AREA``
             - m²
             - Fire base area
           * - 4
             - ``CO_YIELD``
             - kg/kg
             - Carbon monoxide yield
           * - 5
             - ``SOOT_YIELD``
             - kg/kg
             - Soot yield
           * - 6
             - ``HCN_YIELD``
             - kg/kg
             - Hydrogen cyanide yield
           * - 7
             - ``HCL_YIELD``
             - kg/kg
             - Hydrogen chloride yield
           * - 8
             - ``TRACE_YIELD``
             - kg/kg
             - Trace species yield

        If a dict is used, keys must match column names from ``LABELS`` and values
        can be either a list of floats (one per timestep) or a scalar float (repeated for
        all timesteps). All list-valued columns must have the same length.

    Examples
    --------
    Define a fire once and place it twice in a compartment:

    >>> defn = FireDefinition(
    ...     fire_id="100kW",
    ...     heat_of_combustion=50000,
    ...     data_table=[[0, 100, 0.5, 0.36, 0, 0.001, 0, 0, 0]],
    ... )
    >>> burner1 = Fire(id="burner1", comp_id="ROOM1", location=[5.45, 2.15],
    ...                definition=defn)
    >>> burner2 = Fire(id="burner2", comp_id="ROOM1", location=[4.25, 2.15],
    ...                definition=defn)
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

    DEFAULT_DATA_TABLE: list[list[float]] = [[0, 0, 0, 0, 0, 0, 0, 0, 0]]

    def __init__(
        self,
        fire_id: str,
        carbon: float = 1,
        chlorine: float = 0,
        hydrogen: float = 4,
        nitrogen: float = 0,
        oxygen: float = 0,
        heat_of_combustion: float = 50000,
        radiative_fraction: float = 0.35,
        data_table: list[list[float]]
        | dict[str, list[float] | float]
        | np.ndarray
        | pd.DataFrame
        | None = None,
    ):
        self.fire_id = fire_id
        self.carbon = carbon
        self.chlorine = chlorine
        self.hydrogen = hydrogen
        self.nitrogen = nitrogen
        self.oxygen = oxygen
        self.heat_of_combustion = heat_of_combustion
        self.radiative_fraction = radiative_fraction
        if data_table is None:
            data_table = self.DEFAULT_DATA_TABLE
        self._data_table = self._process_data_table(data_table)

        self._validate()
        self._initialized = True

    def _validate(self) -> None:
        """Validate the chemistry fields and the HRR data table.

        Raises
        ------
        ValueError
            If ``heat_of_combustion`` is not positive, an atomic count is negative,
            or the ``TIME`` column is not strictly increasing.

        Warns
        -----
        UserWarning
            If carbon and hydrogen are both 0 (no hydrocarbon fuel), or if
            ``radiative_fraction`` is outside ``[0, 1]``.
        """
        if self.heat_of_combustion <= 0:
            raise ValueError(
                f"FireDefinition '{self.fire_id}': heat_of_combustion must be "
                f"positive, got {self.heat_of_combustion}."
            )

        for attr in ("carbon", "hydrogen", "nitrogen", "oxygen", "chlorine"):
            val = getattr(self, attr)
            if val < 0:
                raise ValueError(
                    f"FireDefinition '{self.fire_id}': {attr} must be non-negative, "
                    f"got {val}."
                )

        if self.carbon == 0 and self.hydrogen == 0:
            warnings.warn(
                f"FireDefinition '{self.fire_id}': carbon=0 and hydrogen=0: fuel "
                "contains no hydrocarbon. CFAST requires a hydrocarbon fuel, this may "
                "cause inaccurate results.",
                UserWarning,
                stacklevel=2,
            )

        if not 0.0 <= self.radiative_fraction <= 1.0:
            warnings.warn(
                f"FireDefinition '{self.fire_id}': "
                f"radiative_fraction={self.radiative_fraction} "
                "is outside [0, 1]. This may cause inaccurate results.",
                UserWarning,
                stacklevel=2,
            )

        if self._data_table:
            time_values = [row[0] for row in self._data_table]
            if any(
                t1 >= t2 for t1, t2 in zip(time_values, time_values[1:], strict=False)
            ):
                raise ValueError(
                    f"FireDefinition '{self.fire_id}': TIME values in data_table must "
                    f"be strictly monotonically increasing. Got: {time_values}"
                )

    @property
    def data_table(self) -> list[list[float]]:
        """Fire time-dependent data table as list of lists."""
        return self._data_table

    @data_table.setter
    def data_table(
        self,
        value: list[list[float]]
        | dict[str, list[float] | float]
        | np.ndarray
        | pd.DataFrame,
    ) -> None:
        self._data_table = self._process_data_table(value)
        if self._initialized:
            self._validate()

    def __eq__(self, other: object) -> bool:
        """Two definitions are equal when their chemistry and data table match."""
        if not isinstance(other, FireDefinition):
            return NotImplemented
        return (
            self.fire_id == other.fire_id
            and self.carbon == other.carbon
            and self.chlorine == other.chlorine
            and self.hydrogen == other.hydrogen
            and self.nitrogen == other.nitrogen
            and self.oxygen == other.oxygen
            and self.heat_of_combustion == other.heat_of_combustion
            and self.radiative_fraction == other.radiative_fraction
            and self._data_table == other._data_table
        )

    def __repr__(self) -> str:
        """Return a detailed string representation of the FireDefinition."""
        data_rows = len(self.data_table) if self.data_table else 0
        return (
            f"FireDefinition("
            f"fire_id='{self.fire_id}', "
            f"heat_of_combustion={self.heat_of_combustion}, "
            f"radiative_fraction={self.radiative_fraction}, "
            f"data_rows={data_rows}"
            ")"
        )

    def to_input_string(self) -> str:
        """
        Generate the ``&CHEM`` + ``&TABL`` CFAST input file string for this definition.

        Returns
        -------
        str
            Formatted ``&CHEM`` record followed by the ``&TABL`` labels record and one
            ``&TABL`` data record per row of the HRR table.

        Examples
        --------
        >>> defn = FireDefinition(
        ...     fire_id="WOOD",
        ...     data_table=[[0, 1000, 0.5, 1.0, 0.01, 0.01, 0, 0, 0]],
        ... )
        >>> print(defn.to_input_string())
        &CHEM ID = 'WOOD' CARBON = 1 CHLORINE = 0 HYDROGEN = 4 NITROGEN = 0 OXYGEN = 0 HEAT_OF_COMBUSTION = 50000 RADIATIVE_FRACTION = 0.35 /
        &TABL ID = 'WOOD' LABELS = 'TIME', 'HRR', 'HEIGHT', 'AREA', 'CO_YIELD', 'SOOT_YIELD', 'HCN_YIELD', 'HCL_YIELD', 'TRACE_YIELD' /
        &TABL ID = 'WOOD' DATA = 0.0, 1000.0, 0.5, 1.0, 0.01, 0.01, 0.0, 0.0, 0.0 /
        """
        # &CHEM record
        input_str = (
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

        # &TABL LABELS record
        input_str += (
            NamelistRecord("TABL")
            .add_field("ID", self.fire_id)
            .add_list_field("LABELS", self.LABELS)
            .build()
        )

        # &TABL DATA records
        if self.data_table:
            for row in self.data_table:
                input_str += (
                    NamelistRecord("TABL")
                    .add_field("ID", self.fire_id)
                    .add_list_field("DATA", row)
                    .build()
                )

        return input_str

    def to_dataframe(self) -> pd.DataFrame:
        """
        Convert the fire data table to a pandas DataFrame with proper column labels.

        Returns
        -------
        pd.DataFrame
            DataFrame with columns matching :attr:`LABELS`.

        Examples
        --------
        >>> defn = FireDefinition(
        ...     fire_id="WOOD",
        ...     data_table=[[0, 1000, 0.5, 1.0, 0.01, 0.01, 0, 0, 0]],
        ... )
        >>> defn.to_dataframe()
        TIME     HRR  HEIGHT  AREA  ...
        0   0.0  1000.0     0.5   1.0  ...
        [1 rows x 9 columns]
        """
        return pd.DataFrame(self.data_table, columns=self.LABELS)

    def _process_data_table(
        self,
        data_table: list[list[float]]
        | dict[str, list[float] | float]
        | np.ndarray
        | pd.DataFrame,
    ) -> list[list[float]]:
        """
        Process and validate data_table input from various formats.

        Parameters
        ----------
        data_table : list[list[float]], dict, np.ndarray, or pd.DataFrame
            Fire data in various formats. Must have columns/keys corresponding to
            :attr:`LABELS`.

        Returns
        -------
        list[list[float]]
            Standardized data table as list of lists.

        Raises
        ------
        TypeError
            If data_table is not one of the supported types.
        ValueError
            If data_table has the wrong shape, missing keys, mismatched column
            lengths, or non-numeric values.
        """
        if isinstance(data_table, dict):
            return self._process_dict_data_table(data_table)

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
                "data_table must be a list of lists, dict, NumPy array, "
                "pandas DataFrame, or None."
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

    def _process_dict_data_table(
        self, data_table: dict[str, list[float] | float]
    ) -> list[list[float]]:
        """
        Convert a dict-format data_table to the standard list-of-lists format.

        Parameters
        ----------
        data_table : dict[str, list[float] | float]
            Keys are column names from :attr:`LABELS`. Values are either a list
            (one entry per timestep) or a scalar (repeated for all timesteps).

        Returns
        -------
        list[list[float]]
            Data table as a list of lists.
        """
        invalid_keys = set(data_table.keys()) - set(self.LABELS)
        if invalid_keys:
            raise ValueError(
                f"Invalid data_table keys: {invalid_keys}. "
                f"Valid keys are: {self.LABELS}"
            )

        missing_keys = set(self.LABELS) - set(data_table.keys())
        if missing_keys:
            raise ValueError(
                f"Missing required data_table keys: {missing_keys}. "
                f"All columns are required: {self.LABELS}"
            )

        list_lengths: list[int] = []
        for value in data_table.values():
            if isinstance(value, list):
                list_lengths.append(len(value))

        if not list_lengths:
            raise ValueError(
                "data_table dict must have at least one list-valued column."
            )

        n_rows = list_lengths[0]
        if not all(length == n_rows for length in list_lengths):
            raise ValueError(
                "All list-valued columns in data_table must have the same length. "
                f"Got lengths: {dict(zip([k for k, v in data_table.items() if isinstance(v, list)], list_lengths, strict=False))}"
            )

        if n_rows < 1:
            raise ValueError("List-valued columns must contain at least one element.")

        columns: list[list[float]] = []
        for label in self.LABELS:
            value = data_table[label]
            if isinstance(value, list):
                columns.append(value)
            else:
                try:
                    scalar = float(value)
                except (ValueError, TypeError) as e:
                    raise ValueError(
                        "All values in data_table must be numeric. "
                        f"Got non-numeric value for '{label}': {value!r}"
                    ) from e
                columns.append([scalar] * n_rows)

        try:
            array_data = np.array(columns, dtype=float).T
        except (ValueError, TypeError) as e:
            raise ValueError("All values in data_table must be numeric.") from e

        result: list[list[float]] = array_data.tolist()
        return result


class Fire(CFASTComponent):
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
    fire_id : str, optional
        The selected name must be unique (i.e., not the same as another fire definition
        in the same simulation). IDs for fire definitions can be the same as ones for
        fire instances. Not required when ``definition`` is given (the id is taken
        from the definition).
    location : list[float]
        Position of the center of the base of the fire relative to the front left corner
        of the compartment. Format: [x, y]. Default units: m, default value: compartment center.
    ignition_criterion : str, optional
        The time of ignition can be controlled by a user-specified time, or by a
        user-specified target's surface temperature or incident heat flux.
        Options: "TIME", "TEMPERATURE", "FLUX".
    set_point : float, optional
        The critical value at which ignition will occur. If it is less than or equal
        to zero, the default value of zero is taken. Can be a time (s), temperature (°C),
        or flux (kW/m²) depending on criterion. Required when ignition_criterion is set.
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
    data_table : list[list[float]], dict, np.ndarray, or pd.DataFrame, optional
        Time-dependent fire properties with columns for TIME, HRR, HEIGHT, AREA,
        CO_YIELD, SOOT_YIELD, HCN_YIELD, HCL_YIELD, TRACE_YIELD. Properties are linearly
        interpolated between specified points. Defaults to ``DEFAULT_DATA_TABLE``
        (a single all-zero row) when not provided.

        .. list-table::
           :header-rows: 1
           :widths: 10 25 15 50

           * - Index
             - Name
             - Unit
             - Description
           * - 0
             - ``TIME``
             - s
             - Simulation time
           * - 1
             - ``HRR``
             - kW
             - Heat release rate
           * - 2
             - ``HEIGHT``
             - m
             - Flame height
           * - 3
             - ``AREA``
             - m²
             - Fire base area
           * - 4
             - ``CO_YIELD``
             - kg/kg
             - Carbon monoxide yield
           * - 5
             - ``SOOT_YIELD``
             - kg/kg
             - Soot yield
           * - 6
             - ``HCN_YIELD``
             - kg/kg
             - Hydrogen cyanide yield
           * - 7
             - ``HCL_YIELD``
             - kg/kg
             - Hydrogen chloride yield
           * - 8
             - ``TRACE_YIELD``
             - kg/kg
             - Trace species yield

        If a dict is used, keys must match column names from ``LABELS`` and values
        can be either a list of floats (one per timestep) or a scalar float (repeated for
        all timesteps). All list-valued columns must have the same length.
    definition : FireDefinition, optional
        An explicit fire definition to reference. Mutually exclusive with the chemistry
        arguments (``carbon`` … ``data_table``) and ``fire_id``. Use this to share a
        single definition across several fire instances.

    Examples
    --------
    Create a simple growing fire:

    >>> fire_data = [
    ...     [0, 0, 0.5, 0.1, 0.01, 0.01, 0, 0, 0],      # t=0s, no heat release
    ...     [60, 100, 0.5, 0.5, 0.01, 0.01, 0, 0, 0],   # t=60s, 100 kW
    ...     [300, 500, 1.0, 1.0, 0.01, 0.01, 0, 0, 0]   # t=300s, 500 kW peak
    ... ]
    >>> fire = Fire(
    ...     id="FIRE1",
    ...     comp_id="ROOM1",
    ...     fire_id="POLYURETHANE",
    ...     location=[2.0, 2.0],
    ...     carbon=27, hydrogen=36, oxygen=2, nitrogen=2, chlorine=0,
    ...     heat_of_combustion=23600,
    ...     radiative_fraction=0.35,
    ...     data_table=fire_data
    ... )

    Create a fire with a dict-format data table:

    >>> fire_data_dict = {
    ...     "TIME": [0, 60, 300],
    ...     "HRR": [0, 100, 500],
    ...     "HEIGHT": [0.5, 0.5, 1.0],
    ...     "AREA": [0.1, 0.5, 1.0],
    ...     "CO_YIELD": 0.01,
    ...     "SOOT_YIELD": 0.01,
    ...     "HCN_YIELD": 0,
    ...     "HCL_YIELD": 0,
    ...     "TRACE_YIELD": 0,
    ... }
    >>> fire = Fire(
    ...     id="FIRE2",
    ...     comp_id="ROOM1",
    ...     fire_id="POLYURETHANE",
    ...     location=[2.0, 2.0],
    ...     carbon=27, hydrogen=36, oxygen=2, nitrogen=2, chlorine=0,
    ...     heat_of_combustion=23600,
    ...     radiative_fraction=0.35,
    ...     data_table=fire_data_dict
    ... )

    Create a fire with a pandas DataFrame:

    >>> import pandas as pd
    >>> fire_data_df = pd.DataFrame({
    ...     "TIME": [0, 60, 300],
    ...     "HRR": [0, 100, 500],
    ...     "HEIGHT": [0.5, 0.5, 1.0],
    ...     "AREA": [0.1, 0.5, 1.0],
    ...     "CO_YIELD": [0.01, 0.01, 0.01],
    ...     "SOOT_YIELD": [0.01, 0.01, 0.01],
    ...     "HCN_YIELD": [0, 0, 0],
    ...     "HCL_YIELD": [0, 0, 0],
    ...     "TRACE_YIELD": [0, 0, 0],
    ... })
    >>> fire = Fire(
    ...     id="FIRE3",
    ...     comp_id="ROOM1",
    ...     fire_id="POLYURETHANE",
    ...     location=[2.0, 2.0],
    ...     carbon=27, hydrogen=36, oxygen=2, nitrogen=2, chlorine=0,
    ...     heat_of_combustion=23600,
    ...     radiative_fraction=0.35,
    ...     data_table=fire_data_df
    ... )

    The LABELS for the data table are fixed and must be in the following order below:

    """

    LABELS = FireDefinition.LABELS

    DEFAULT_DATA_TABLE: list[list[float]] = FireDefinition.DEFAULT_DATA_TABLE

    def __init__(
        self,
        id: str,
        comp_id: str,
        fire_id: str | None = None,
        location: list[float] | None = None,
        ignition_criterion: str | None = None,
        set_point: float | None = None,
        device_id: str | None = None,
        carbon: float = _UNSET,
        chlorine: float = _UNSET,
        hydrogen: float = _UNSET,
        nitrogen: float = _UNSET,
        oxygen: float = _UNSET,
        heat_of_combustion: float = _UNSET,
        radiative_fraction: float = _UNSET,
        data_table: list[list[float]]
        | dict[str, list[float] | float]
        | np.ndarray
        | pd.DataFrame
        | None = _UNSET,
        definition: FireDefinition | None = None,
    ):
        inline_chem: dict[str, Any] = {
            "carbon": carbon,
            "chlorine": chlorine,
            "hydrogen": hydrogen,
            "nitrogen": nitrogen,
            "oxygen": oxygen,
            "heat_of_combustion": heat_of_combustion,
            "radiative_fraction": radiative_fraction,
            "data_table": data_table,
        }
        provided_chem = {k: v for k, v in inline_chem.items() if v is not _UNSET}

        if definition is not None:
            if provided_chem or fire_id is not None:
                raise ValueError(
                    f"Fire '{id}': pass either a `definition` or inline chemistry "
                    "arguments (carbon, hydrogen, …, data_table) and `fire_id`, "
                    "not both."
                )
            self._definition = definition
        else:
            if fire_id is None:
                raise ValueError(
                    f"Fire '{id}': `fire_id` is required when no `definition` is given."
                )
            self._definition = FireDefinition(fire_id=fire_id, **provided_chem)

        self.id = id
        self.comp_id = comp_id
        self.location = location if location is not None else []
        self.ignition_criterion = ignition_criterion
        self.set_point = set_point
        self.device_id = device_id

        self._validate()
        self._initialized = True

    def _validate(self) -> None:
        """Validate the fire instance (placement and ignition) attributes.

        Chemistry and HRR-table validation lives on the referenced
        :class:`FireDefinition`.

        Raises
        ------
        TypeError
            If location is not a list.
        ValueError
            If any instance attribute violates the constraints.
        """
        if not isinstance(self.location, list):
            raise TypeError(
                f"Fire '{self.id}': location must be a list, got {type(self.location).__name__}."
            )

        if self.ignition_criterion is not None:
            valid_criteria = {"TIME", "TEMPERATURE", "FLUX"}
            if self.ignition_criterion not in valid_criteria:
                raise ValueError(
                    f"Fire '{self.id}': invalid ignition_criterion "
                    f"'{self.ignition_criterion}'. Valid options are: {valid_criteria}."
                )
            if self.set_point is None:
                raise ValueError(
                    f"Fire '{self.id}': set_point must be specified when "
                    f"ignition_criterion is '{self.ignition_criterion}'."
                )
            if (
                self.ignition_criterion in {"TEMPERATURE", "FLUX"}
                and self.device_id is None
            ):
                raise ValueError(
                    f"Fire '{self.id}': device_id must be specified when "
                    f"ignition_criterion is '{self.ignition_criterion}'."
                )

        if len(self.location) != 2:
            raise ValueError(
                f"Fire '{self.id}': location must be a list of two floats [x, y]."
            )

    @property
    def definition(self) -> FireDefinition:
        """The :class:`FireDefinition` (chemistry + HRR table) this instance uses."""
        return self._definition

    @property
    def fire_id(self) -> str:
        """Identifier of the referenced fire definition."""
        return self._definition.fire_id

    @fire_id.setter
    def fire_id(self, value: str) -> None:
        self._definition.fire_id = value

    @property
    def carbon(self) -> float:
        """Number of carbon atoms in the fuel molecule (from the definition)."""
        return self._definition.carbon

    @carbon.setter
    def carbon(self, value: float) -> None:
        self._definition.carbon = value

    @property
    def chlorine(self) -> float:
        """Number of chlorine atoms in the fuel molecule (from the definition)."""
        return self._definition.chlorine

    @chlorine.setter
    def chlorine(self, value: float) -> None:
        self._definition.chlorine = value

    @property
    def hydrogen(self) -> float:
        """Number of hydrogen atoms in the fuel molecule (from the definition)."""
        return self._definition.hydrogen

    @hydrogen.setter
    def hydrogen(self, value: float) -> None:
        self._definition.hydrogen = value

    @property
    def nitrogen(self) -> float:
        """Number of nitrogen atoms in the fuel molecule (from the definition)."""
        return self._definition.nitrogen

    @nitrogen.setter
    def nitrogen(self, value: float) -> None:
        self._definition.nitrogen = value

    @property
    def oxygen(self) -> float:
        """Number of oxygen atoms in the fuel molecule (from the definition)."""
        return self._definition.oxygen

    @oxygen.setter
    def oxygen(self, value: float) -> None:
        self._definition.oxygen = value

    @property
    def heat_of_combustion(self) -> float:
        """Energy released per unit mass of fuel consumed (from the definition)."""
        return self._definition.heat_of_combustion

    @heat_of_combustion.setter
    def heat_of_combustion(self, value: float) -> None:
        self._definition.heat_of_combustion = value

    @property
    def radiative_fraction(self) -> float:
        """Fraction of combustion energy emitted as thermal radiation (definition)."""
        return self._definition.radiative_fraction

    @radiative_fraction.setter
    def radiative_fraction(self, value: float) -> None:
        self._definition.radiative_fraction = value

    @property
    def data_table(self) -> list[list[float]]:
        """Fire time-dependent data table as list of lists (from the definition)."""
        return self._definition.data_table

    @data_table.setter
    def data_table(
        self,
        value: list[list[float]]
        | dict[str, list[float] | float]
        | np.ndarray
        | pd.DataFrame,
    ) -> None:
        self._definition.data_table = value

    def __repr__(self) -> str:
        """Return a detailed string representation of the Fire."""
        location_str = f"[{', '.join(map(str, self.location))}]"
        data_rows = len(self.data_table) if self.data_table else 0

        return (
            f"Fire("
            f"id='{self.id}', comp_id='{self.comp_id}', fire_id='{self.fire_id}', "
            f"location={location_str}, "
            f"heat_of_combustion={self.heat_of_combustion}, "
            f"radiative_fraction={self.radiative_fraction}, "
            f"data_rows={data_rows}"
            ")"
        )

    def __str__(self) -> str:
        """Return a user-friendly string representation of the Fire."""
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

    def to_instance_string(self) -> str:
        """
        Generate the ``&FIRE`` CFAST input file record for this instance.

        Returns
        -------
        str
            Formatted ``&FIRE`` record (placement and ignition only — chemistry and the
            HRR table are emitted by the :class:`FireDefinition`).

        Examples
        --------
        >>> fire = Fire(id="FIRE1", comp_id="ROOM1", fire_id="WOOD", location=[1.0, 1.0])
        >>> print(fire.to_instance_string())
        &FIRE ID = 'FIRE1' COMP_ID = 'ROOM1' FIRE_ID = 'WOOD' LOCATION = 1.0, 1.0 /
        """
        fire_rec = NamelistRecord("FIRE")
        fire_rec.add_field("ID", self.id)
        fire_rec.add_field("COMP_ID", self.comp_id)
        fire_rec.add_field("FIRE_ID", self.fire_id)
        fire_rec.add_list_field("LOCATION", self.location)

        if self.ignition_criterion is not None:
            fire_rec.add_field("IGNITION_CRITERION", self.ignition_criterion)
            fire_rec.add_numeric_field("SETPOINT", self.set_point)
            if self.ignition_criterion in {"TEMPERATURE", "FLUX"}:
                fire_rec.add_field("DEVC_ID", self.device_id)

        return fire_rec.build()

    def to_input_string(self) -> str:
        """
        Generate the full CFAST input file string for this fire.

        Emits the ``&FIRE`` instance record followed by the referenced definition's
        ``&CHEM`` + ``&TABL`` records. When several instances share one definition,
        :class:`~pycfast.model.CFASTModel` de-duplicates the definition so it is written
        only once; use :meth:`to_instance_string` and
        :meth:`FireDefinition.to_input_string` directly for that.

        Returns
        -------
        str
            Formatted string ready for inclusion in CFAST input file.

        Examples
        --------
        >>> fire = Fire(
        ...     id="FIRE1",
        ...     comp_id="ROOM1",
        ...     fire_id="WOOD",
        ...     location=[1.0, 1.0],
        ...     data_table=[[0, 1000, 0.5, 1.0, 0.01, 0.01, 0, 0, 0]]
        ... )
        >>> print(fire.to_input_string())
        &FIRE ID = 'FIRE1' COMP_ID = 'ROOM1' FIRE_ID = 'WOOD' LOCATION = 1.0, 1.0 /
        &CHEM ID = 'WOOD' CARBON = 1 CHLORINE = 0 HYDROGEN = 4 NITROGEN = 0 OXYGEN = 0 HEAT_OF_COMBUSTION = 50000 RADIATIVE_FRACTION = 0.35 /
        &TABL ID = 'WOOD' LABELS = 'TIME', 'HRR', 'HEIGHT', 'AREA', 'CO_YIELD', 'SOOT_YIELD', 'HCN_YIELD', 'HCL_YIELD', 'TRACE_YIELD' /
        &TABL ID = 'WOOD' DATA = 0.0, 1000.0, 0.5, 1.0, 0.01, 0.01, 0.0, 0.0, 0.0 /
        """
        return self.to_instance_string() + self._definition.to_input_string()

    def to_dataframe(self) -> pd.DataFrame:
        """
        Convert fire data table to pandas DataFrame with proper column labels.

        Returns
        -------
        pd.DataFrame
            DataFrame with columns matching LABELS for easy analysis and plotting.

        Examples
        --------
        >>> fire = Fire(
        ...     id="FIRE1",
        ...     comp_id="ROOM1",
        ...     fire_id="WOOD",
        ...     location=[1.0, 1.0],
        ...     data_table=[[0, 1000, 0.5, 1.0, 0.01, 0.01, 0, 0, 0]]
        ... )
        >>> df = fire.to_dataframe()
        >>> df
        TIME     HRR  HEIGHT  AREA  ...
        0   0.0  1000.0     0.5   1.0  ...
        [1 rows x 9 columns]
        """
        return self._definition.to_dataframe()
