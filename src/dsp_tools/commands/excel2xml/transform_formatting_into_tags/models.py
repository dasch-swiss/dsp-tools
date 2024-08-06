from __future__ import annotations

from dataclasses import dataclass

from lxml import etree


@dataclass
class ParsedExcelFile:
    workbook: etree._Element
    shared_strings: etree._Element
    sheets: list[ParsedExcelSheet]


@dataclass
class ParsedExcelSheet:
    name: str
    content: etree._Element


@dataclass
class CellInformation:
    sheet: str
    shared_string_index: int
    hyperlink: etree._Element | None = None


@dataclass
class SharedStringElement:
    location: CellInformation
    string_ele: etree._Element


@dataclass
class SharedStringExcelPosition:
    sheet: str
    column: str
    excel_row: int
    content: SharedStringElement


@dataclass
class FormattingTransformedCell:
    sheet_name: str
    location_str: str
    content: str
