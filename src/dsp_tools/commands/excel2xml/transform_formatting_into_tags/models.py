from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from lxml import etree


@dataclass
class ExcelSheet:
    name: str
    filename: str
    cells: list[Cell]


@dataclass
class Cell(Protocol): ...


@dataclass
class InputCell(Cell):
    location_str: str
    content_xml: etree._Element
    hyperlink: etree._Element | None = None


@dataclass
class InputCellCleaned(Cell):
    column: str
    df_row: int
    content_xml: etree._Element
    hyperlink: str | None = None


@dataclass
class FormattingTransformedCell(Cell):
    column: str
    df_row: int
    content: str
