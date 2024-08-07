import pytest
from lxml import etree

from dsp_tools.commands.excel2xml.transform_formatting_into_tags.formatting2tags import _get_hyperlink_mapper
from dsp_tools.commands.excel2xml.transform_formatting_into_tags.models import XMLParsedExcelFile
from dsp_tools.commands.excel2xml.transform_formatting_into_tags.models import XMLParsedExcelSheet


def test_parse_excel_as_xml(unclean_excel: XMLParsedExcelFile) -> None:
    assert isinstance(unclean_excel, XMLParsedExcelFile)
    assert isinstance(unclean_excel.shared_strings, etree._Element)
    assert len(unclean_excel.sheets) == 2
    assert isinstance(unclean_excel.workbook, etree._Element)


def test_clean_excel_as_xml(cleaned_excel: XMLParsedExcelFile) -> None:
    assert isinstance(cleaned_excel, XMLParsedExcelFile)
    assert isinstance(cleaned_excel.shared_strings, etree._Element)
    assert len(cleaned_excel.sheets) == 2
    assert not cleaned_excel.workbook


def test_combine_information_from_xml_files(minimal_excel: XMLParsedExcelFile) -> None:
    raise NotImplementedError


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
