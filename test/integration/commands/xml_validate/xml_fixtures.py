from pathlib import Path

import pytest
from lxml import etree

from dsp_tools.commands.xml_validate.xml_validate import _parse_and_clean_file


@pytest.fixture
def data_xml() -> etree._Element:
    return _parse_and_clean_file(
        Path("testdata/xml-validate/data_correct.xml"), "http://0.0.0.0:3333/ontology/9999/onto/v2#"
    )
