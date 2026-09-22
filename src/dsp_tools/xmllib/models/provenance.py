from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SourceProvenance:
    """
    Where a value came from in the source data, for use in the `provenance` parameter of the `add_...` methods.

    `row` is 1-based and counts the header row, matching what a researcher sees in the spreadsheet program.

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
