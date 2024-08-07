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


@pytest.fixture()
def one_hyperlink() -> etree._Element:
    return etree.fromstring("""
        <hyperlink ref="B2" r:id="rId1" xr:uid="{E409A7F7-CD3B-AD4B-B9A8-916CE1594F27}"/>
    """)


@pytest.fixture()
def one_hyperlink_relation() -> etree._Element:
    return etree.fromstring("""
        <Relationship 
            Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink" 
            Target="https://app.dasch.swiss/" TargetMode="External"
        />
    """)


@pytest.fixture()
def one_shared_string_no_formatting() -> etree._Element:
    return etree.fromstring("""
        <si>
            <t>Sheet2 B2 Link</t>
        </si>
    """)


@pytest.fixture()
def one_shared_string_formatting() -> etree._Element:
    return etree.fromstring("""
        <si>
        <r>
            <t xml:space="preserve">Sheet1 A2 </t>
        </r>
        <r>
            <rPr>
                <b/>
                <sz val="12"/>
                <color theme="1"/>
                <rFont val="Calibri"/>
                <family val="2"/>
                <scheme val="minor"/>
            </rPr>
            <t>Bold</t>
        </r>
        <r>
            <rPr>
                <sz val="12"/>
                <color theme="1"/>
                <rFont val="Calibri"/>
                <family val="2"/>
                <scheme val="minor"/>
            </rPr>
            <t xml:space="preserve"> After</t>
        </r>
    </si>
    """)
