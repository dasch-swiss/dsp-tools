
import pytest
from lxml import etree

from dsp_tools.commands.excel2xml.transform_formatting_into_tags.models import XMLParsedExcelFile


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


if __name__ == "__main__":
    pytest.main([__file__])
