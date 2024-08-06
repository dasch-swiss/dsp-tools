from pathlib import Path

import pytest

from dsp_tools.commands.excel2xml.transform_formatting_into_tags.formatting2tags import _parse_excel_as_xml
from dsp_tools.commands.excel2xml.transform_formatting_into_tags.models import XMLParsedExcelFile


@pytest.fixture()
def excel_as_xml() -> XMLParsedExcelFile:
    return _parse_excel_as_xml(Path("testdata/excel2xml/formatting2tags/formatted-text-test.xlsx"))


def test_parse_excel_as_xml(excel_as_xml: XMLParsedExcelFile) -> None:
    assert isinstance(excel_as_xml, XMLParsedExcelFile)
    assert len(excel_as_xml.sheets) == 2


if __name__ == "__main__":
    pytest.main([__file__])
