"""
Simulation Environment module for CFAST simulations.

This module provides the SimulationEnvironment class for defining the initial
conditions and simulation time for the CFAST input file.
"""

from __future__ import annotations

from typing import Any

from .utils.namelist import NamelistRecord
from .utils.theme import build_card


class SimulationEnvironment:
    """
    Defines the initial conditions and simulation time for the CFAST input file.

    The Environment page defines the simulation environment, including version and title
    information, simulation times, ambient conditions, and miscellaneous global parameters.
    Ambient conditions define the environment at which the scenario begins. Initial pressures
    in a structure are calculated based on NOAA/NASA tables. It is convenient to choose the
    base of a structure to be at zero height and then reference the height of the structure
    with respect to that height.

    Parameters
    ----------
    title : str
        The first thing to do when setting up an input file is to give the simulation
        a title. The title is optional and may consist of letters, numbers, and/or
        symbols and may be up to 50 characters. All output files will be tagged with
        this character string.
    time_simulation : int, optional
        The length of time over which the simulation takes place. The maximum value
        for this input is 86400 s (1 day). Default units: s, default value: 900 s.
    print : int, optional
        The time interval between each printing of the output data. If equal to zero,
        no output values will appear. Default units: s, default value: 60 s.
    smokeview : int, optional
        CFAST can output a subset of the results in a format compatible with the
        visualization program Smokeview. This input defines the time interval between
        outputs of the model results in a Smokeview-compatible format. A value greater
        than zero must be used if the Smokeview output is desired. Default units: s,
        default value: 15 s.
    spreadsheet : int, optional
        CFAST can output the results of the simulation in a set of comma-delimited
        spreadsheet files. This parameter defines the time interval between these outputs.
        A value greater than zero must be used if the spreadsheet files are desired.
        Default units: s, default value: 15 s.
    init_pressure : float, optional
        Initial values for ambient atmospheric pressure inside and outside the structure
        at the station elevation. The default value is standard atmospheric pressure at
        sea level. Default units: Pa, default value: 101325 Pa.
    relative_humidity : float, optional
        The initial relative humidity in the system, only specified for the interior.
        This is converted to kilograms of water per cubic meter as an initial condition
        for both the interior and exterior of the structure. Default units: % RH,
        default value: 50 %.
    interior_temperature : float, optional
        Initial ambient temperature inside the structure at the station elevation.
        Default units: °C, default value: 20 °C.
    exterior_temperature : float, optional
        Initial ambient temperature outside the structure at the station elevation.
        Default units: °C, default value: 20 °C.
    adiabatic : bool, optional
        When this option is enabled, all of the compartment surfaces are assumed to be
        perfect insulators and the materials section of the compartments tab becomes
        grayed out. This feature is useful when designing an experiment in which it is
        safe to assume that there is no heat transfer to the walls of the compartments.
    max_time_step : float, optional
        CFAST will automatically adjust the time interval for the solution of the
        differential equation set up or down so that the simulation is as efficient as
        possible within the pre-defined error tolerances. This parameter places a maximum
        value for the equation solver and can normally be left at the default value. In
        cases (which are hopefully rare) where the model fails to converge on a solution,
        this value can be reduced which often will allow the simulation to successfully
        complete. Default units: s, default value: 2 s.
    lower_oxygen_limit : float, optional
        In the CFAST model, a limit is incorporated by limiting the burning rate as the
        oxygen level decreases until a "lower oxygen limit" (LOL) is reached. The lower
        oxygen limit is incorporated through a smooth decrease in the burning rate near
        the limit. Normally, this value would not be changed by the user. Default units: %,
        default value: 15 %.

    Notes
    -----
    The equations implemented in the model are not designed to handle negative elevations
    and altitudes. Usually, the station elevation is set to zero and the pressure to
    ambient. The effect of changing these values is minor.

    Examples
    --------
    Create a simulation environment following CFAST conventions:

    >>> simulation_env = SimulationEnvironment(
    ...     title="Office Fire Simulation",
    ...     time_simulation=1800,  # Length of simulation (s)
    ...     print=10,              # Text output interval (s)
    ...     smokeview=1,           # Smokeview output interval (s)
    ...     spreadsheet=1          # Spreadsheet output interval (s)
    ... )
    """

    def __init__(
        self,
        title: str,
        time_simulation: int | None = 900,
        print: int | None = 60,
        smokeview: int | None = 15,
        spreadsheet: int | None = 15,
        init_pressure: float | None = 101325,
        relative_humidity: float | None = 50,
        interior_temperature: float | None = 20,
        exterior_temperature: float | None = 20,
        adiabatic: bool | None = None,
        max_time_step: float | None = None,  # =2 in CFAST if None
        lower_oxygen_limit: float | None = None,
        extra_custom: str | None = None,  # mainly use for DIAG section
    ):
        self.title = title
        self.time_simulation = time_simulation
        self.print = print
        self.smokeview = smokeview
        self.spreadsheet = spreadsheet
        self.init_pressure = init_pressure
        self.relative_humidity = relative_humidity
        self.interior_temperature = interior_temperature
        self.exterior_temperature = exterior_temperature
        self.adiabatic = adiabatic
        self.max_time_step = max_time_step
        self.lower_oxygen_limit = lower_oxygen_limit
        self.extra_custom = extra_custom

    def __repr__(self) -> str:
        """Return a detailed string representation of the SimulationEnvironment."""
        return (
            f"SimulationEnvironment("
            f"title='{self.title}', time_simulation={self.time_simulation}, "
            f"print={self.print}, smokeview={self.smokeview}, "
            f"spreadsheet={self.spreadsheet}, "
            f"init_pressure={self.init_pressure}, "
            f"relative_humidity={self.relative_humidity}, "
            f"interior_temperature={self.interior_temperature}, "
            f"exterior_temperature={self.exterior_temperature}"
            f")"
        )

    def __str__(self) -> str:
        """Return a user-friendly string representation of the SimulationEnvironment."""
        return (
            f"Simulation Environment '{self.title}': "
            f"duration={self.time_simulation}s, "
            f"temp_in={self.interior_temperature}°C, "
            f"temp_out={self.exterior_temperature}°C"
        )

    def _repr_html_(self) -> str:
        """Return an HTML representation for Jupyter/interactive environments."""
        duration_str = (
            f"{self.time_simulation / 60:.0f} min"
            if self.time_simulation is not None and self.time_simulation >= 60
            else f"{self.time_simulation} s"
        )

        body_html = f"""
            <div class="pycfast-card-grid" style="margin-bottom: 10px;">
                <div><strong>Duration:</strong> {duration_str}</div>
                <div><strong>Print interval:</strong> {getattr(self, "print", "N/A")} s</div>
                <div><strong>Interior temp:</strong> {getattr(self, "interior_temperature", "N/A")}°C</div>
                <div><strong>Exterior temp:</strong> {getattr(self, "exterior_temperature", "N/A")}°C</div>
                <div><strong>Pressure:</strong> {getattr(self, "init_pressure", "N/A")} Pa</div>
                <div><strong>Humidity:</strong> {getattr(self, "relative_humidity", "N/A")}%</div>
            </div>
            <details class="pycfast-inline-detail">
                <summary>Advanced Settings</summary>
                <div class="pycfast-detail-content">
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(120px, 1fr)); gap: 5px;">
                        <div>Smokeview: {getattr(self, "smokeview", "N/A")} s</div>
                        <div>Spreadsheet: {getattr(self, "spreadsheet", "N/A")} s</div>
                        <div>Max timestep: {getattr(self, "max_time_step", "N/A")} s</div>
                        <div>O₂ limit: {getattr(self, "lower_oxygen_limit", "N/A")}</div>
                        <div>Adiabatic: {getattr(self, "adiabatic", False)}</div>
                    </div>
                </div>
            </details>
        """

        return build_card(
            icon="⚙️",
            gradient="linear-gradient(135deg, #00b894, #00cec9)",
            title="Simulation Environment",
            subtitle=f"<strong>{getattr(self, 'title', 'Untitled Simulation')}</strong>",
            accent_color="#00b894",
            body_html=body_html,
        )

    def __getitem__(self, key: str) -> Any:
        """Get environment property by name for dictionary-like access."""
        if not hasattr(self, key):
            raise KeyError(f"Property '{key}' not found in SimulationEnvironment.")
        return getattr(self, key)

    def __setitem__(self, key: str, value: Any) -> None:
        """Set environment property by name for dictionary-like assignment."""
        if not hasattr(self, key):
            raise KeyError(
                f"Cannot set '{key}'. Property does not exist in SimulationEnvironment."
            )
        setattr(self, key, value)

    def to_input_string(self) -> str:
        """
        Generate CFAST input file string for the simulation environment.

        Returns
        -------
        str
            Formatted string ready for inclusion in CFAST input file.

        Examples
        --------
        >>> config = SimulationEnvironment("Test", 300, print=10)
        >>> print(config.to_input_string())
        &HEAD VERSION = 7700 TITLE = 'Test' /

        !! Scenario Configuration
        &TIME SIMULATION = 300 PRINT = 10 ...
        """
        head = (
            NamelistRecord("HEAD")
            .add_field("VERSION", 7700)
            .add_field("TITLE", self.title)
            .build()
        )

        time_rec = (
            NamelistRecord("TIME")
            .add_field("SIMULATION", self.time_simulation)
            .add_field("PRINT", self.print)
            .add_field("SMOKEVIEW", self.smokeview)
            .add_field("SPREADSHEET", self.spreadsheet)
            .build()
        )

        init_rec = (
            NamelistRecord("INIT")
            .add_field("PRESSURE", self.init_pressure)
            .add_field("RELATIVE_HUMIDITY", self.relative_humidity)
            .add_field("INTERIOR_TEMPERATURE", self.interior_temperature)
            .add_field("EXTERIOR_TEMPERATURE", self.exterior_temperature)
            .build()
        )

        input_str = head + "\n!! Scenario Configuration \n" + time_rec + init_rec

        if self.adiabatic or self.max_time_step or self.lower_oxygen_limit:
            misc = NamelistRecord("MISC")
            if self.adiabatic is not None:
                misc.add_field("ADIABATIC", self.adiabatic)
            misc.add_field("MAX_TIME_STEP", self.max_time_step)
            misc.add_field("LOWER_OXYGEN_LIMIT", self.lower_oxygen_limit)
            input_str += misc.build()

        if self.extra_custom:
            input_str += f"{self.extra_custom}\n"

        return input_str
