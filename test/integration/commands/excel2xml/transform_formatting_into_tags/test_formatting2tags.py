import pytest
from lxml import etree

from dsp_tools.commands.excel2xml.transform_formatting_into_tags.formatting2tags import _extract_all_string_cells_info
from dsp_tools.commands.excel2xml.transform_formatting_into_tags.formatting2tags import (
    _extract_all_string_locations_one_sheet,
)
from dsp_tools.commands.excel2xml.transform_formatting_into_tags.formatting2tags import _extract_cell_number_to_link_id
from dsp_tools.commands.excel2xml.transform_formatting_into_tags.formatting2tags import _extract_link_id_to_url
from dsp_tools.commands.excel2xml.transform_formatting_into_tags.formatting2tags import _get_hyperlink_filename
from dsp_tools.commands.excel2xml.transform_formatting_into_tags.formatting2tags import _get_hyperlink_mapper
from dsp_tools.commands.excel2xml.transform_formatting_into_tags.formatting2tags import _get_worksheet_name
from dsp_tools.commands.excel2xml.transform_formatting_into_tags.models import CellInformation
from dsp_tools.commands.excel2xml.transform_formatting_into_tags.models import XMLParsedExcelFile
from dsp_tools.commands.excel2xml.transform_formatting_into_tags.models import XMLParsedExcelSheet


def test_parse_excel_as_xml(unclean_excel: XMLParsedExcelFile) -> None:
    assert isinstance(unclean_excel, XMLParsedExcelFile)
    assert isinstance(unclean_excel.shared_strings, etree._Element)
    assert isinstance(unclean_excel.workbook, etree._Element)
    assert len(unclean_excel.sheets) == 2
    one = next((x for x in unclean_excel.sheets if x.file_name == "sheet1.xml"))
    assert isinstance(one, XMLParsedExcelSheet)
    assert one.file_name == "sheet1.xml"
    assert one.sheet_name == ""
    assert isinstance(one.content, etree._Element)
    assert isinstance(one.sheet_relations, etree._Element)
    two = next((x for x in unclean_excel.sheets if x.file_name == "sheet2.xml"))
    assert isinstance(two, XMLParsedExcelSheet)
    assert two.file_name == "sheet2.xml"
    assert two.sheet_name == ""
    assert isinstance(two.content, etree._Element)
    assert not two.sheet_relations


def test_clean_excel_as_xml(cleaned_excel: XMLParsedExcelFile) -> None:
    assert isinstance(cleaned_excel, XMLParsedExcelFile)
    assert isinstance(cleaned_excel.shared_strings, etree._Element)
    assert len(cleaned_excel.sheets) == 2
    assert not cleaned_excel.workbook
    one = next((x for x in cleaned_excel.sheets if x.file_name == "sheet1.xml"))
    assert isinstance(one, XMLParsedExcelSheet)
    assert one.file_name == "sheet1.xml"
    assert one.sheet_name == "Formatting"
    assert isinstance(one.content, etree._Element)
    assert isinstance(one.sheet_relations, etree._Element)
    two = next((x for x in cleaned_excel.sheets if x.file_name == "sheet2.xml"))
    assert isinstance(two, XMLParsedExcelSheet)
    assert two.file_name == "sheet2.xml"
    assert two.sheet_name == "OtherContent"
    assert isinstance(two.content, etree._Element)
    assert not two.sheet_relations


def test_combine_information_from_xml_files(minimal_excel: XMLParsedExcelFile) -> None:
    raise NotImplementedError


class TestExtractFileNames:
    def test_sheet_name(self) -> None:
        result = _get_worksheet_name("xl/worksheets/sheet1.xml")
        assert result == "sheet1.xml"

    def test_not_sheet_name(self) -> None:
        assert not _get_worksheet_name("other")

    def test_rels_name(self) -> None:
        result = _get_hyperlink_filename("xl/worksheets/_rels/sheet1.xml.rels")
        assert result == "sheet1.xml"

    def test_not_rels_name(self) -> None:
        assert not _get_hyperlink_filename("other")


def test_extract_all_string_cells_info(minimal_excel: XMLParsedExcelFile) -> None:
    result = _extract_all_string_cells_info(minimal_excel.sheets)
    assert len(result) == 5


class TestExtractCellInformation:
    def test_no_links(self, sheet_no_links: XMLParsedExcelSheet) -> None:
        result = _extract_all_string_locations_one_sheet(sheet_no_links)
        assert len(result) == 2
        one = result[0]
        assert isinstance(one, CellInformation)
        assert one.sheet == "Sheet1"
        assert one.cell_name == "A1"
        assert one.shared_string_index == 1
        assert not one.hyperlink
        two = result[1]
        assert two.sheet == "Sheet1"
        assert two.cell_name == "A2"
        assert two.shared_string_index == 0
        assert not two.hyperlink

    def test_with_links(self, sheet_with_links: XMLParsedExcelSheet) -> None:
        result = _extract_all_string_locations_one_sheet(sheet_with_links)
        assert len(result) == 3
        with_link = next((x for x in result if x.cell_name == "B2"))
        assert isinstance(with_link, CellInformation)
        assert with_link.sheet == "Sheet2"
        assert with_link.cell_name == "B2"
        assert with_link.shared_string_index == 4
        assert with_link.hyperlink == "https://app.dasch.swiss/"


class TestHyperlinkMapper:
    def test_get_hyperlink_mapper(self, sheet_with_links: XMLParsedExcelSheet) -> None:
        result = _get_hyperlink_mapper(sheet_with_links.content, sheet_with_links.sheet_relations)
        assert result == {"B2": "https://app.dasch.swiss/"}

    def test_extract_cell_number_to_link_id(self, sheet_with_links: XMLParsedExcelSheet) -> None:
        result = _extract_cell_number_to_link_id(sheet_with_links.content)
        assert result == {"B2": "rId1"}

    def test_extract_link_id_to_url(self, sheet_with_links: XMLParsedExcelSheet) -> None:
        result = _extract_link_id_to_url(sheet_with_links.sheet_relations)
        assert result == {"rId1": "https://app.dasch.swiss/"}


if __name__ == "__main__":
    pytest.main([__file__])
