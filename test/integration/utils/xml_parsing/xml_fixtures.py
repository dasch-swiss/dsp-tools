from pathlib import Path

import pytest
from lxml import etree

from dsp_tools.utils.xml_parsing.xx_xml_parsing_and_cleaning import get_xml_project


@pytest.fixture
def data_xml() -> etree._Element:
    return get_xml_project(Path("testdata/validate-data/generic/minimal_correct.xml"), "http://0.0.0.0:3333").root
