# Intentional deviations from the CFAST User's Guide

Cases where a docstring knowingly differs from `docs/cfast-reference`. The
`cfast-docstrings` skill does not report or undo them. Add a row whenever a new
deviation is decided, and remove it once the guide or pycfast changes.

| Component | Parameter / keyword | Guide | Docstring | Reason |
|---|---|---|---|---|
| `Material` | `conductivity` / `CONDUCTIVITY` | kW/(m·K) | W/(m·K) | CFAST reads W/(m·K): `input_namelist.f90` comments `!w/m-k`, and the verification files give steel `CONDUCTIVITY = 48`. |
| `Material` | `specific_heat` / `SPECIFIC_HEAT` | kJ/(kg·K) | kJ/(kg·°C) or kJ/(kg·K) | Same unit, both spellings kept for readers. |
| `Compartment` | `origin_x`, `origin_y`, `origin_z` / `ORIGIN(1:3)` | one triplet | three floats | pycfast splits the triplet, written back as `ORIGIN`. |
| `Compartment` | `id` | default none (required) | default `'Comp 1'` | pycfast default, so a compartment can be created without arguments. |
| `FireDefinition` | `nitrogen`, `oxygen` / `NITROGEN`, `OXYGEN` | lists the keywords as `N` and `O` | `NITROGEN`, `OXYGEN` | Typo in the guide: the `CHEM` namelist reads `NITROGEN` and `OXYGEN`. |
| `MechanicalVent` | `area`, `heights` / `AREAS(1:2)`, `HEIGHTS(1:2)` | documents `AREA`, `HEIGHT` (one value) | one value per connected compartment | pycfast writes the two-value forms, which CFAST still reads. |
| `Device` | `obscuration` / `SETPOINTS(1:2)` | `SETPOINT` or `SETPOINTS(1:2)` | single value | pycfast writes the value as both the smoldering and flaming set points. |
