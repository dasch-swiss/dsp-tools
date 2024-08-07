import pytest
from lxml import etree

from dsp_tools.commands.excel2xml.transform_formatting_into_tags.formatting2tags import _get_hyperlink_filename
from dsp_tools.commands.excel2xml.transform_formatting_into_tags.formatting2tags import _get_hyperlink_mapper
from dsp_tools.commands.excel2xml.transform_formatting_into_tags.formatting2tags import _get_worksheet_name
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


class TestConstructCellInformation:
    def test_no_links(self, minimal_excel: XMLParsedExcelFile) -> None:
        raise NotImplementedError

    def test_with_links(self, cleaned_excel: XMLParsedExcelFile) -> None:
        raise NotImplementedError


class TestHyperlinkMapper:
    def test_no_links(self, sheet_no_links: XMLParsedExcelSheet) -> None:
        assert not _get_hyperlink_mapper(sheet_no_links)

    def test_with_links(self, sheet_with_links: XMLParsedExcelSheet) -> None:
        result = _get_hyperlink_mapper(sheet_with_links)
        assert result == {"B2": "https://app.dasch.swiss/"}


if __name__ == "__main__":
    pytest.main([__file__])
