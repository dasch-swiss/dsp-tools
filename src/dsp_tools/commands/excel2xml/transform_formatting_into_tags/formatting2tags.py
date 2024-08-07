from copy import deepcopy
from pathlib import Path
from zipfile import ZipFile

import regex
from lxml import etree
from openpyxl import Workbook
from openpyxl import load_workbook

from dsp_tools.commands.excel2xml.transform_formatting_into_tags.models import CellInformation
from dsp_tools.commands.excel2xml.transform_formatting_into_tags.models import FormattingTransformedCell
from dsp_tools.commands.excel2xml.transform_formatting_into_tags.models import SharedStringElement
from dsp_tools.commands.excel2xml.transform_formatting_into_tags.models import SharedStringExcelPosition
from dsp_tools.commands.excel2xml.transform_formatting_into_tags.models import XMLParsedExcelFile
from dsp_tools.commands.excel2xml.transform_formatting_into_tags.models import XMLParsedExcelSheet


def formatting_to_tags(excel_file: Path, sheets: list[str] | None = None, columns: list[str] | None = None) -> None:
    workbook = load_workbook(excel_file, keep_vba=True, rich_text=True)
    files = _parse_and_clean_excel_as_xml(excel_file)
    reformatted_workbook = _reformat_workbook(files, workbook, sheets, columns)
    reformatted_workbook.save(excel_file.parent / f"{excel_file.stem}-with-tags.xlsx")


def _parse_and_clean_excel_as_xml(excel_path: Path) -> XMLParsedExcelFile:
    files = _parse_excel_as_xml(excel_path)
    workbook = _remove_namespaces(files.workbook)
    shared_strings = _remove_namespaces(files.shared_strings)
    sheets = [XMLParsedExcelSheet(x.name, _remove_namespaces(x.content)) for x in files.sheets]
    mapped_sheet_names = _map_sheet_names(workbook, sheets)
    return XMLParsedExcelFile(workbook=workbook, shared_strings=shared_strings, sheets=mapped_sheet_names)


def _parse_excel_as_xml(excel_path):
    with ZipFile(excel_path, "r") as zip_ref:
        workbook_xml = etree.fromstring(zip_ref.read("xl/workbook.xml"))
        shared_strings_xml = etree.fromstring(zip_ref.read("xl/sharedStrings.xml"))
        sheet_files = [x for x in zip_ref.NameToInfo if regex.search(r"xl\/worksheets\/sheet\d+\.xml", x)]
        sheets_parsed = [etree.fromstring(zip_ref.read(x)) for x in sheet_files]
        all_sheets = [
            XMLParsedExcelSheet(name=name.split("/")[-1], content=sheet)
            for name, sheet in zip(sheet_files, sheets_parsed)
        ]
        return XMLParsedExcelFile(workbook=workbook_xml, shared_strings=shared_strings_xml, sheets=all_sheets)


def _remove_namespaces(root: etree._Element) -> etree._Element:
    changed = deepcopy(root)
    for elem in changed.iter():
        # Skip comments and processing instructions, because they do not have names
        if not (isinstance(elem, etree._Comment) or isinstance(elem, etree._ProcessingInstruction)):
            elem.tag = etree.QName(elem).localname
    etree.cleanup_namespaces(changed)
    return changed


def _map_sheet_names(workbook: etree._Element, sheets: list[XMLParsedExcelSheet]) -> list[XMLParsedExcelSheet]:
    sheet_name_mapper = {}
    for sheet_element in workbook.iterdescendants(tag="sheet"):
        sheet_name = sheet_element.attrib["name"]
        sheet_id = sheet_element.attrib["sheetId"]
        sheet_name_mapper[f"sheet{sheet_id}.xml"] = sheet_name
    mapped_name_sheets = []
    for sheet in sheets:
        new_name = sheet_name_mapper[sheet.name]
        mapped_name_sheets.append(XMLParsedExcelSheet(new_name, sheet.content))
    return mapped_name_sheets


def _reformat_workbook(
    files: XMLParsedExcelFile,
    workbook: Workbook,
    sheets: list[str] | None,
    columns: list[str] | None,
) -> Workbook:
    shared_string_elements = _combine_information_from_xml_files(files)
    reformatted_shared_strings = _reformat_location_of_string_elements(shared_string_elements)
    columns_and_locations = _extract_all_column_locations_and_names(workbook)
    content_to_format_locations = _filter_columns_and_locations(columns_and_locations, sheets, columns)
    filtered_content = _filter_content_to_format(reformatted_shared_strings, content_to_format_locations)
    # TODO: if len(filtered_content) == 0: stop with warning
    reformatted_content = _reformat_content(filtered_content)
    return _insert_content_into_workbook(reformatted_content, workbook)


def _combine_information_from_xml_files(files: XMLParsedExcelFile) -> list[SharedStringElement]:
    string_locations = _extract_all_string_locations(files.sheets)
    # TODO: get all shared strings combined
    # TODO: reformat the locations
    # TODO: filter the locations


def _extract_all_string_locations(sheets: list[XMLParsedExcelSheet]) -> list[CellInformation]:
    raise NotImplementedError


def _reformat_location_of_string_elements(shared_strings: list[SharedStringElement]) -> list[SharedStringExcelPosition]:
    raise NotImplementedError


def _extract_all_column_locations_and_names(workbook: Workbook) -> dict[str, list[str]]:
    raise NotImplementedError


def _filter_columns_and_locations(
    columns_and_locations: dict[str, list[str]], sheets: list[str] | None, columns: list[str] | None
) -> dict[str, list[str]]:
    raise NotImplementedError


def _filter_content_to_format(
    shared_strings: list[SharedStringExcelPosition], info_what_to_use: dict[str, list[str]]
) -> list[SharedStringElement]:
    raise NotImplementedError


def _reformat_content(shared_strings: list[SharedStringElement]) -> list[FormattingTransformedCell]:
    raise NotImplementedError


def _insert_content_into_workbook(reformatted: list[FormattingTransformedCell], workbook: Workbook) -> Workbook:
    raise NotImplementedError
