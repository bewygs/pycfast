r"""
Canonical builder for CFAST Fortran namelist records.

Provides a ``NamelistRecord`` helper that collects fields, formats values
by type, omits ``None`` values, and produces deterministic single-line
output suitable for CFAST input files.

Formatting rules
-----------------
* Record shape: ``&KEYWORD field1 field2 ... /\n``
* Fields separated by **spaces** (no inter-field commas).
* String values are single-quoted: ``KEY = 'VALUE'``
* Numeric values are rendered with ``str()``: ``KEY = 3.0``
* Boolean values use Fortran literals: ``.TRUE.`` / ``.FALSE.``
* List values are **comma-separated** internally:
    ``KEY = 'A', 'B'``  or  ``KEY = 1.0, 2.0``
* ``None`` values are silently skipped -- never emitted.

Note that the file generated might differ from an CEdit file
in terms of whitespace, commas, field order, and numeric formatting
(e.g. ``3.0`` vs ``3``). However, the generated file will be semantically
equivalent to CFAST and should not affect simulation results.
Verification tests confirm that.
"""

from __future__ import annotations

from collections.abc import Sequence

# Scalar types accepted by the builder.
_Scalar = str | int | float | bool


class NamelistRecord:
    r"""Builder for a single CFAST Fortran namelist record.

    Parameters
    ----------
    keyword : str
        The namelist keyword (e.g. ``"COMP"``, ``"VENT"``, ``"MATL"``).

    Examples
    --------
    >>> rec = NamelistRecord("COMP")
    >>> rec.add_field("ID", "ROOM1")
    NamelistRecord('COMP')
    >>> rec.add_field("WIDTH", 3.0)
    NamelistRecord('COMP')
    >>> rec.build()
    "&COMP ID = 'ROOM1' WIDTH = 3.0 /\n"
    """

    def __init__(self, keyword: str) -> None:
        self._keyword = keyword
        self._fields: list[tuple[str, str]] = []

    def add_field(
        self,
        key: str,
        value: _Scalar | None,
    ) -> NamelistRecord:
        """Append a scalar field, skipping ``None``.

        Parameters
        ----------
        key : str
            The CFAST keyword name (e.g. ``"WIDTH"``).
        value : str | int | float | bool | None
            The value.  ``None`` => field is omitted.  ``bool`` =>
            ``.TRUE.`` / ``.FALSE.``.  ``str`` => single-quoted.

        Returns
        -------
        NamelistRecord
            ``self``, for chaining.
        """
        if value is None:
            return self
        self._fields.append((key, _format_scalar(value)))
        return self

    def add_numeric_field(
        self,
        key: str,
        value: int | float | str | None,
    ) -> NamelistRecord:
        """Append a numeric field, coercing string values to numbers.

        Use this instead of ``add_field`` when the CFAST keyword expects a
        numeric value but the data source may supply a string (e.g. values
        originating from the parser).

        Parameters
        ----------
        key : str
            The CFAST keyword name.
        value : int | float | str | None
            The value.  ``None`` => field is omitted.  Strings are
            coerced to ``int`` or ``float``.

        Returns
        -------
        NamelistRecord
            ``self``, for chaining.
        """
        if value is None:
            return self
        self._fields.append((key, str(_coerce_numeric(value))))
        return self

    def add_list_field(
        self,
        key: str,
        values: Sequence[_Scalar] | None,
    ) -> NamelistRecord:
        """Append a list field, skipping ``None``.

        Parameters
        ----------
        key : str
            The CFAST keyword name.
        values : list or tuple of scalars, or None
            Each element is formatted individually and joined with ``", "``.

        Returns
        -------
        NamelistRecord
            ``self``, for chaining.
        """
        if values is None:
            return self
        formatted = ", ".join(_format_scalar(v) for v in values)
        self._fields.append((key, formatted))
        return self

    def add_raw(self, key: str, raw_value: str) -> NamelistRecord:
        """Append a pre-formatted value verbatim.

        Parameters
        ----------
        key : str
            The CFAST keyword name.
        raw_value : str
            Already-formatted value string (inserted as-is).

        Returns
        -------
        NamelistRecord
            ``self``, for chaining.
        """
        self._fields.append((key, raw_value))
        return self

    def build(self) -> str:
        r"""Render the namelist record.

        Returns
        -------
        str
            A single line ``"&KEYWORD field1 field2 ... /\n"``.
        """
        parts: list[str] = [f"&{self._keyword}"]
        for key, formatted_value in self._fields:
            parts.append(f"{key} = {formatted_value}")
        return " ".join(parts) + " /\n"


def _format_scalar(value: _Scalar) -> str:
    """Format a single scalar value for a Fortran namelist.

    Parameters
    ----------
    value : str | int | float | bool
        The Python value to format.

    Returns
    -------
    str
        Formatted namelist token.
    """
    # bool must be checked before int (bool is a subclass of int).
    if isinstance(value, bool):
        return ".TRUE." if value else ".FALSE."
    if isinstance(value, str):
        return f"'{value}'"
    # int / float – use default str()
    return str(value)


def _coerce_numeric(value: int | float | str) -> int | float:
    """Coerce a value to a numeric type if possible.

    Parameters
    ----------
    value : int | float | str
        The value to coerce.

    Returns
    -------
    int | float
        The numeric value.

    Raises
    ------
    ValueError
        If a string value cannot be converted to a number.
    """
    if isinstance(value, int | float):
        return value
    # Try int first, then float.
    try:
        return int(value)
    except ValueError:
        return float(value)
