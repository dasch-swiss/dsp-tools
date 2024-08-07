from __future__ import annotations

from dataclasses import dataclass

from lxml import etree

from dsp_tools.commands.excel2xml.transform_formatting_into_tags.models_standoff import CellChunk


@dataclass
class XMLParsedExcelFile:
    """
    An Excel file contains several files and folders in the background.
    They can be extracted by parsing them as ZipFiles.
    Not all the files are relevant for the current purpose.
    This class contains the parsed files that are relevant.

    Args:
        workbook: "workbook.xml"
                  Metadata of the file.
                  Relevant because it maps the custom sheet names to the sheet IDs
        shared_strings: "sharedStrings.xml"
                        The content of the cells that are formatted as strings.
                        The location of the cells is not included.
                        The order of the string elements is based on which cell was last edited.
        sheets: a list of all the sheets in the Excel
    """

    workbook: etree._Element
    shared_strings: etree._Element
    sheets: list[XMLParsedExcelSheet]


@dataclass
class XMLParsedExcelSheet:
    """
    The number of cells and some formatting data for each sheet is saved in one XML file.
    If the datatype of the cell is not a string, the content of the cell is also located here.
    If the datatype is a string, the element contains an index number of the element in the "sharedStrings.xml" file.
    It contains an element storing all the hyperlinks in a file,
    the location of which is saved in an attribute of the element.

    Args:
        name: name of the sheet, either the custom name or in the format of "sheet1.xml"
        content: the parsed content of the file
    """

    name: str
    content: etree._Element


@dataclass
class CellInformation:
    """
    Stores reformatted information about one cell with a sting datatype in a sheet.
    All this information can be constructed from the parsed "sheet.xml" file.

    Args:
        sheet: name of the sheet, corresponds to the user-facing name in the Excel
        cell_name: name of the cell in the format of A1, B12, etc.
        shared_string_index: index number of the element in the "sharedStrings.xml"
        hyperlink: the element containing the hyperlink if applicable
    """

    sheet: str
    cell_name: str
    shared_string_index: int
    hyperlink: etree._Element | None = None


@dataclass
class SharedStringElement:
    """Contains the location information and the string element of a string cell."""

    location: CellInformation
    string_ele: etree._Element


@dataclass
class SharedStringExcelPosition:
    """
    Users can specify the columns they want to include.
    The column names are not visible in the location cells.
    The first row is not recognised as header.
    To filter out the cells that should be reformatted and create
    a mapping of the cell locations in the format of e.g. A1, need to be transformed.

    Args:
        sheet: user-facing sheet name
        column: user-facing column name
        excel_row: row number
        content: Class containing all the cell information
    """

    sheet: str
    column: str
    excel_row: int
    content: SharedStringElement


@dataclass
class FormattingTransformedCell:
    """Reformatted cell content and information to locate it on an openpyxl workbook."""

    sheet_name: str
    location_str: str
    content: CellChunk
