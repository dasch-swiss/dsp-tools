from __future__ import annotations

from dataclasses import dataclass

from lxml import etree

from dsp_tools.commands.excel2xml.transform_formatting_into_tags.models_standoff import CellChunk


@dataclass
class XMLParsedExcelFile:
    workbook: etree._Element
    shared_strings: etree._Element
    sheets: list[XMLParsedExcelSheet]


@dataclass
class XMLParsedExcelSheet:
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
    content: CellChunk
