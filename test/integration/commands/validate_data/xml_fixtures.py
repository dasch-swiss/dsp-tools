from pathlib import Path

import pytest
from lxml import etree

from dsp_tools.commands.validate_data.xml_validate import _parse_and_clean_file


@pytest.fixture
def data_xml() -> etree._Element:
    return _parse_and_clean_file(Path("testdata/data-validate/data/minimal_correct.xml"), "http://0.0.0.0:3333")
