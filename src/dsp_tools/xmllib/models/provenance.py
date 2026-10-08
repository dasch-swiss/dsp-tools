from __future__ import annotations

import numbers
from dataclasses import dataclass
from typing import Any

import regex

from dsp_tools.xmllib.internal.checkers import is_nonempty_value_internal
from dsp_tools.xmllib.internal.xmllib_warnings import MessageInfo
from dsp_tools.xmllib.internal.xmllib_warnings_util import emit_xmllib_input_warning


@dataclass(frozen=True)
class SourceProvenance:
    """
    Where a value came from in the source data, for use in the `provenance` parameter of the `add_...` methods.

    `row` is 1-based and counts the header row, matching what a researcher sees in the spreadsheet program.

    Invalid input never raises an error:

    - An empty `source_file` becomes an empty string and emits a warning.
    - An empty `sheet`, `row` or `cell` (for example `None`, `pd.NA` or `""`) becomes `None`.
    - A `sheet` or `cell` that is not a string is converted to a string.
    - A `row` that is not an integer (for example `"abc"` or `5.5`) becomes `None` and emits a warning.

    Examples:
        ```python
        provenance = xmllib.SourceProvenance(
            source_file="data.xlsx",
            sheet="Sheet1",
            row=5,
            cell="C",
        )
        ```
    """

    source_file: str
    sheet: str | None = None
    row: int | None = None
    cell: str | None = None

    def __post_init__(self) -> None:
        # The dataclass is frozen, so the normalised values are set with object.__setattr__.
        object.__setattr__(self, "source_file", _normalise_source_file(self.source_file))
        object.__setattr__(self, "sheet", _normalise_optional_str(self.sheet))
        object.__setattr__(self, "row", _normalise_row(self.row))
        object.__setattr__(self, "cell", _normalise_optional_str(self.cell))


def _normalise_source_file(value: Any) -> str:
    if is_nonempty_value_internal(value):
        return str(value)
    msg = f"The source_file of a SourceProvenance must be a non-empty string, but your input is '{value}'."
    emit_xmllib_input_warning(MessageInfo(message=msg, field="provenance"))
    return ""


def _normalise_optional_str(value: Any) -> str | None:
    if is_nonempty_value_internal(value):
        return str(value)
    return None


def _normalise_row(value: Any) -> int | None:
    if not is_nonempty_value_internal(value):
        return None
    if isinstance(value, numbers.Integral) and not isinstance(value, bool):
        return int(value)
    if isinstance(value, float) and value.is_integer():
        return int(value)
    if isinstance(value, str) and regex.fullmatch(r"\d+", value.strip()):
        return int(value)
    msg = f"The row of a SourceProvenance must be an integer, but your input is '{value}'. The row is ignored."
    emit_xmllib_input_warning(MessageInfo(message=msg, field="provenance"))
    return None
