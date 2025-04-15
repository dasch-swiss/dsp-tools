import pytest

from dsp_tools.xmllib.internal_helpers import numeric_entities
from dsp_tools.xmllib.internal_helpers import unescape_standoff_tags


def test_unescape_standoff_tags() -> None:
    unescape_standoff_tags("")
    pytest.fail("TODO")


def test_numeric_entities() -> None:
    numeric_entities("")
    pytest.fail("TODO")
