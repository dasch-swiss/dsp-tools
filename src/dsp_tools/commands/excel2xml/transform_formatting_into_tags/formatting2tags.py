from pathlib import Path

from openpyxl import Workbook

from dsp_tools.commands.excel2xml.transform_formatting_into_tags.models import CellInformation
from dsp_tools.commands.excel2xml.transform_formatting_into_tags.models import FormattingTransformedCell
from dsp_tools.commands.excel2xml.transform_formatting_into_tags.models import ParsedExcelFile
from dsp_tools.commands.excel2xml.transform_formatting_into_tags.models import ParsedExcelSheet
from dsp_tools.commands.excel2xml.transform_formatting_into_tags.models import SharedStringElement
from dsp_tools.commands.excel2xml.transform_formatting_into_tags.models import SharedStringExcelPosition


def formatting_to_tags(excel_file: Path, sheets: list[str] | None = None, columns: list[str] | None = None) -> None:
    files = _parse_excel_as_xml(excel_file)
    workbook = _parse_excel_as_workbook(excel_file)
    shared_string_elements = _combine_information_from_xml_files(files)
    reformatted_shared_strings = _reformat_location_of_string_elements(shared_string_elements)
    columns_and_locations = _extract_all_column_locations_and_names(workbook)
    content_to_format_locations = _filter_columns_and_locations(columns_and_locations, sheets, columns)
    filtered_content = _filter_content_to_format(reformatted_shared_strings, content_to_format_locations)
    # TODO: if len(filtered_content) == 0: stop with warning
    reformatted_content = _reformat_content(filtered_content)
    reformatted_workbook = _insert_content_into_workbook(reformatted_content, workbook)
    # TODO: save workbook


def _parse_excel_as_workbook(excel_path: Path) -> Workbook:
    raise NotImplementedError


def _parse_excel_as_xml(excel_path: Path) -> ParsedExcelFile:
    raise NotImplementedError


def _combine_information_from_xml_files(files: ParsedExcelFile) -> list[SharedStringElement]:
    # TODO: map sheet names
    string_locations = _extract_all_string_locations(files.sheets)
    # TODO: get all shared strings combined
    # TODO: reformat the locations
    # TODO: filter the locations


def _extract_all_string_locations(sheets: list[ParsedExcelSheet]) -> list[CellInformation]:
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
