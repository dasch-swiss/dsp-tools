from pathlib import Path

import pytest
from lxml import etree

from dsp_tools.commands.excel2xml.transform_formatting_into_tags.formatting2tags import _clean_excel_as_xml
from dsp_tools.commands.excel2xml.transform_formatting_into_tags.formatting2tags import _parse_excel_as_xml
from dsp_tools.commands.excel2xml.transform_formatting_into_tags.models import XMLParsedExcelFile
from dsp_tools.commands.excel2xml.transform_formatting_into_tags.models import XMLParsedExcelSheet


@pytest.fixture()
def unclean_excel() -> XMLParsedExcelFile:
    return _parse_excel_as_xml(Path("testdata/excel2xml/formatting2tags/formatted-text-test.xlsx"))


@pytest.fixture()
def cleaned_excel(unclean_excel: XMLParsedExcelFile) -> XMLParsedExcelFile:
    return _clean_excel_as_xml(unclean_excel)


@pytest.fixture()
def minimal_excel() -> XMLParsedExcelFile:
    read = _parse_excel_as_xml(Path("testdata/excel2xml/formatting2tags/minimal-test.xlsx"))
    return _clean_excel_as_xml(read)


@pytest.fixture()
def sheet_no_links(minimal_excel: XMLParsedExcelFile) -> XMLParsedExcelSheet:
    return next((x for x in minimal_excel.sheets if x.file_name == "sheet1.xml"))


@pytest.fixture()
def sheet_with_links(minimal_excel: XMLParsedExcelFile) -> XMLParsedExcelSheet:
    return next((x for x in minimal_excel.sheets if x.file_name == "sheet2.xml"))


@pytest.fixture()
def one_string_cell() -> etree._Element:
    return etree.fromstring("""
        <c r="A2" t="s">
            <v>0</v>
        </c>
    """)


@pytest.fixture()
def one_non_string_cell() -> etree._Element:
    return etree.fromstring("""
        <c r="A2">
            <v>1</v>
        </c>
    """)
