from pathlib import Path

import pytest
from lxml import etree

from dsp_tools.utils.xml_utils import parse_and_clean_xml_file


@pytest.fixture
def data_xml() -> etree._Element:
    return parse_and_clean_xml_file(Path("testdata/xml-validate/data_correct.xml"))
