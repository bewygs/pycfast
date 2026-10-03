---
name: cfast-docstrings
description: Check and update the docstrings of PyCFAST components (Compartment, WallVent, Fire, Device, ...) against the CFAST User's Guide LaTeX vendored in docs/cfast-reference. Use after the reference documentation is bumped, when a component parameter is added or changed, or when asked whether a docstring matches the CFAST documentation.
---

# CFAST docstrings

Component docstrings are near-verbatim copies of the CFAST User's Guide. The guide
is vendored as LaTeX in `docs/cfast-reference/`, taken from `firemodels/cfast`
`master` at the commit recorded in `docs/cfast-reference/.cfast_version`
(refreshed by `docs/update_cfast_ref.sh` and the weekly `sync-cfast-ref-doc`
workflow). This skill compares each docstring with the guide, tells which entries
must change, and applies the changes. Deviations from the guide are rare and
recorded in `references/deviations.md`.

## Sources

| What | Where |
|---|---|
| Parameter text, GUI default | `Input_File_Chapter.tex`: `\item[Label] (default: ...; namelist: \ct{KEY}) text` |
| Type, units, solver default | `Appendix_CFAST_Keywords.tex`: one table per namelist (`tbl:COMP`, ...). `CHEM` is `tbl:FIRE`, `FIRE` is `tbl:FIRE2`, `TABL` is `tbl:FIRE3` |
| Class summary and Notes | Prose of the component's chapter in `Input_File_Chapter.tex` |
| What CFAST actually reads | `Source/CFAST/input_namelist.f90` upstream and the `.in` files in `tests/verification_tests/Verification/` |

When the guide contradicts what CFAST reads, CFAST wins. Record the case in
`references/deviations.md`.

## Procedure

1. Run the packet script from the repository root. Without arguments, it prints
   a summary of all components. With component names, it prints one review
   packet per component:

   ```bash
   uv run python .claude/skills/cfast-docstrings/scripts/review_packet.py
   uv run python .claude/skills/cfast-docstrings/scripts/review_packet.py Compartment
   ```

   For each parameter, the packet shows the CFAST keyword(s) it is written to
   (read from the `NamelistRecord` calls, so it follows the serializer), the
   appendix row, the guide entry and the current docstring entry. It then lists
   the keywords in scope that pycfast does not write, the guide entries matched
   to no parameter, and the guide prose of the chapter.
2. Read `references/deviations.md`. Do not report or undo a listed deviation.
3. Read the class source (docstring, `__init__`, `_validate`, `to_input_string`).
   The packet does not cover Examples, Raises or validation rules.
4. Classify every parameter and the class docstring:
   - `ok`: same meaning, and the wording differs only by the allowed edits below.
   - `update`: the docstring is stale, paraphrased, wrong, or misses a
     default or units that the guide gives.
   - `deviation`: intentional difference, already listed or new. Add a new one to
     `references/deviations.md` in the same change.
   - `ask`: the guide is unclear, contradicts the code, or the change would alter
     behaviour (a default, a validation). Do not guess; report it.

   `FLAG:` lines are hints computed by regex. Check each one against the `.tex`
   before acting. A parameter without flags still needs its text compared.
5. Edit the docstrings (rules below). Do not touch the code, except the docstring
   of `to_input_string` if its example output changes.
6. Validate:

   ```bash
   uv run pytest --doctest-modules src/pycfast/<module>.py
   make check
   make format
   ```

7. Report one table per component, then the `ask` items and the CFAST keywords
   pycfast does not expose yet:

   | Parameter | Status | Change / reason |
   |---|---|---|

## Writing rules

Copy, do not paraphrase. Only these edits to the guide text are allowed:

- **LaTeX to RST**: `\ct{KEY}` becomes ``` ``KEY`` ```. Units are written in
  Unicode (`m²`, `m³/s`, `°C`, `kW/m²`, `(m·s)^(1/2)`). Drop `\ref`, `\cite`, figures
  and tables. Tables the guide reproduces from other works "with permission"
  (e.g. the leakage areas from the Handbook of Smoke Control Engineering) are
  never copied: mention the source instead.
- **GUI to API**: the guide describes CEdit. Replace tab, page, button,
  checkbox, dropdown and "CEdit" wording, and GUI labels, with the pycfast parameter
  name (``` ``ceiling_mat_id`` ```), the CFAST keyword, or neutral wording.
  "Materials tab Thickness" becomes "the ``thickness`` of the material".
- **Shared or split entries**: when one guide item covers several parameters
  (`ORIGIN(1:3)` gives `origin_x`, `origin_y`, `origin_z`; "Ceiling, Walls, Floor"
  gives three parameters), each parameter gets the shared sentence, narrowed to
  its own axis or surface.
- **pycfast specifics come after the CFAST text**: accepted Python form (tuple
  order, list length), cross-parameter constraints enforced by `_validate`, as
  in "Format: (wall, floor)." or "Must match the number of materials in
  ``ceiling_mat_id``."
- **No version wording**: no "version 7", "CFAST 7.x" or "in this release". The
  only exception is a keyword that one supported CFAST version does not read:
  then end the entry with "Only read by CFAST 8." (or the version concerned),
  and its default must be `None`.
- Never add physics, limits or claims that are not in the guide. When the guide
  is silent on a pycfast-only parameter (`extra_custom`, `definition`), keep or
  write a short factual description of what pycfast does with it.

Parameter entry format (numpydoc, rendered by napoleon):

```text
name : type, optional
    <CFAST sentences>. <pycfast specifics>. Default units: <units>, default value: <value>.
```

- `optional` iff the signature gives a default.
- `Default units:` comes from the appendix or the guide. Values are always in
  these units, since pycfast does no conversion. Omit it for strings, booleans
  and unitless values.
- `default value:` is what CFAST uses when the parameter keeps its pycfast
  default:
  - signature default not `None`: that value, since pycfast writes it;
  - signature default `None`: the keyword is omitted, so state the solver
    default from the appendix (or the guide when the appendix is empty);
  - no default anywhere (required input): omit it.
- Combined: `Default units: m, default value: 0 m.` Unitless:
  `Default value: 1 (fully open).` Off by default: `Default value: off.`

Class docstring:

- Keep the one-line summary unless it is wrong.
- Extended summary: the chapter or section introduction, with the GUI wording
  removed.
- `Notes`: modelling assumptions and cautions from the guide prose. The last
  paragraph of `Notes` is exactly:

  ```rst
  Adapted from the `CFAST User's Guide <https://pages.nist.gov/cfast/>`__.
  ```

  The double underscore makes the link anonymous. A named link repeated in
  several classes breaks the `-W` docs build.
- Keep `Examples`, `Raises` and `See Also` as they are. They are pycfast's own.
