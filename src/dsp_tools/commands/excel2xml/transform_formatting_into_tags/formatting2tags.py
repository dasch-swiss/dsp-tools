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


def formatting_to_tags(excel_path: Path, sheets: list[str] | None = None, columns: list[str] | None = None) -> None:
    workbook = load_workbook(excel_path, keep_vba=True, rich_text=True)
    files = _parse_excel_as_xml(excel_path)
    files = _clean_excel_as_xml(files)
    reformatted_workbook = _reformat_workbook(files, workbook, sheets, columns)
    reformatted_workbook.save(excel_path.parent / f"{excel_path.stem}-with-tags.xlsx")


def _parse_excel_as_xml(excel_path: Path) -> XMLParsedExcelFile:
    with ZipFile(excel_path, "r") as zip_ref:
        workbook_xml = etree.fromstring(zip_ref.read("xl/workbook.xml"))
        shared_strings_xml = etree.fromstring(zip_ref.read("xl/sharedStrings.xml"))
        all_sheets = _parse_sheets(zip_ref)
        return XMLParsedExcelFile(shared_strings=shared_strings_xml, sheets=all_sheets, workbook=workbook_xml)


def _parse_sheets(zip_ref: ZipFile) -> list[XMLParsedExcelSheet]:
    sheet_dict = {
        new_name: etree.fromstring(zip_ref.read(filepath))
        for name, filepath in zip_ref.NameToInfo.items()
        if (new_name := _get_worksheet_name(name))
    }
    hyperlink_dict = {
        new_name: etree.fromstring(zip_ref.read(filepath))
        for name, filepath in zip_ref.NameToInfo.items()
        if (new_name := _get_hyperlink_filename(name))
    }
    all_sheets = [
        XMLParsedExcelSheet(
            file_name=filename, sheet_name="", content=parsed_sheet, sheet_relations=hyperlink_dict.get(filename)
        )
        for filename, parsed_sheet in sheet_dict.items()
    ]
    return all_sheets


def _get_worksheet_name(filepath: str) -> str | None:
    if not (found := regex.search(r"xl\/worksheets\/sheet\d+\.xml", filepath)):
        return None
    return found.group(0).split("/")[-1]


def _get_hyperlink_filename(filepath: str) -> str | None:
    if not (found := regex.search(r"xl\/worksheets\/_rels\/sheet\d+\.xml\.rels", filepath)):
        return None
    return found.group(0).split("/")[-1].replace(".rels", "")


def _clean_excel_as_xml(files: XMLParsedExcelFile) -> XMLParsedExcelFile:
    workbook = _remove_namespaces(files.workbook)
    shared_strings = _remove_namespaces(files.shared_strings)
    sheets = [
        XMLParsedExcelSheet(
            file_name=x.file_name,
            sheet_name=x.sheet_name,
            content=_remove_namespaces(x.content),
            sheet_relations=_remove_namespaces(x.sheet_relations) if x.sheet_relations else None,
        )
        for x in files.sheets
    ]
    mapped_sheet_names = _map_sheet_names(workbook, sheets)
    return XMLParsedExcelFile(shared_strings=shared_strings, sheets=mapped_sheet_names)


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
        new_name = sheet_name_mapper[sheet.file_name]
        mapped_name_sheets.append(
            XMLParsedExcelSheet(
                file_name=sheet.file_name,
                sheet_name=new_name,
                content=sheet.content,
                sheet_relations=sheet.sheet_relations,
            )
        )
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
    string_locations = _extract_all_string_cells_info(files.sheets)
    # TODO: get all shared strings combined
    # TODO: reformat the locations
    # TODO: filter the locations


def _extract_all_string_cells_info(sheets: list[XMLParsedExcelSheet]) -> list[CellInformation]:
    all_locations = []
    for s in sheets:
        all_locations.extend(_extract_all_string_locations_one_sheet(s))
    return all_locations


def _extract_all_string_locations_one_sheet(sheet: XMLParsedExcelSheet) -> list[CellInformation]:
    hyperlink_mapper = (
        _get_hyperlink_mapper(sheet.content, sheet.sheet_relations) if sheet.sheet_relations is not None else {}
    )
    cell_info = []
    for ele in sheet.content.iterdescendants(tag="c"):
        if ele.attrib.get("t") == "s":
            cell_location = ele.attrib["r"]
            string_index = next(ele.iterdescendants(tag="v")).text
            cell_info.append(
                CellInformation(
                    sheet=sheet.sheet_name,
                    cell_name=cell_location,
                    shared_string_index=int(string_index),
                    hyperlink=hyperlink_mapper.get(cell_location),
                )
            )
    return cell_info


def _get_hyperlink_mapper(sheet: etree._Element, relation_sheet: etree._Element) -> dict[str, str]:
    cell2id = _extract_cell_number_to_link_id(sheet)
    id2url = _extract_link_id_to_url(relation_sheet)
    return {cell_num: id2url[url_id] for cell_num, url_id in cell2id.items()}


def _extract_cell_number_to_link_id(sheet: etree._Element) -> dict[str, str]:
    rel_attrib_key = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id"
    mapper = {}
    for ele in sheet.iterdescendants(tag="hyperlink"):
        mapper[ele.attrib["ref"]] = ele.attrib[rel_attrib_key]
    return mapper


def _extract_link_id_to_url(relation_sheet: etree._Element) -> dict[str, str]:
    mapper = {}
    for ele in relation_sheet.iterdescendants(tag="Relationship"):
        mapper[ele.attrib["Id"]] = ele.attrib["Target"]
    return mapper


def _reformat_location_of_string_elements(shared_strings: list[SharedStringElement]) -> list[SharedStringExcelPosition]:
    pass


def _extract_all_column_locations_and_names(workbook: Workbook) -> dict[str, list[str]]:
    pass


def _filter_columns_and_locations(
    columns_and_locations: dict[str, list[str]], sheets: list[str] | None, columns: list[str] | None
) -> dict[str, list[str]]:
    pass


def _filter_content_to_format(
    shared_strings: list[SharedStringExcelPosition], info_what_to_use: dict[str, list[str]]
) -> list[SharedStringElement]:
    pass


def _reformat_content(shared_strings: list[SharedStringElement]) -> list[FormattingTransformedCell]:
    pass


def _insert_content_into_workbook(reformatted: list[FormattingTransformedCell], workbook: Workbook) -> Workbook:
    pass
