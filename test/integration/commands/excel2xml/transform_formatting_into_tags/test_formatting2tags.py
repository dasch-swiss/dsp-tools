from pathlib import Path

import pytest
from lxml import etree

from dsp_tools.commands.excel2xml.transform_formatting_into_tags.formatting2tags import _clean_excel_as_xml
from dsp_tools.commands.excel2xml.transform_formatting_into_tags.formatting2tags import _parse_excel_as_xml
from dsp_tools.commands.excel2xml.transform_formatting_into_tags.models import XMLParsedExcelFile


@pytest.fixture()
def unclean_excel() -> XMLParsedExcelFile:
    return _parse_excel_as_xml(Path("testdata/excel2xml/formatting2tags/formatted-text-test.xlsx"))


@pytest.fixture()
def cleaned_excel(unclean_excel: XMLParsedExcelFile) -> XMLParsedExcelFile:
    return _clean_excel_as_xml(unclean_excel)


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


if __name__ == "__main__":
    pytest.main([__file__])
