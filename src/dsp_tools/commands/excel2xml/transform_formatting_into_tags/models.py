from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from lxml import etree


@dataclass
class ExcelSheet:
    sheet_name: str
    xml_filename: str
    cells: list[InputCell]


@dataclass
class InputCell(Protocol): ...


@dataclass
class InputCellRaw(InputCell):
    location_str: str
    content_xml: etree._Element
    hyperlink: etree._Element | None = None


@dataclass
class InputCellCleaned(InputCell):
    column: str
    df_row: int
    content_xml: etree._Element
    hyperlink: str | None = None


@dataclass
class FormattingTransformedCell:
    sheet_name: str
    column: str
    df_row: int
    content: str
