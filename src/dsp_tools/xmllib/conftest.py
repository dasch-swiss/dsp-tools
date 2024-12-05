from typing import Any

import pytest

from dsp_tools import xmllib


@pytest.fixture(autouse=True)
def add_xmllib_namespace(doctest_namespace: dict[str, Any]) -> None:
    """
    Add "xmllib" to the namespace of the doctests. 
    This allows to use `xmllib.find_date_in_string()` in the docstring examples, 
    instead of `find_date_in_string()`.
    See https://docs.pytest.org/en/stable/how-to/doctest.html#doctest-namespace-fixture.

    Args:
        doctest_namespace: dict object into which you place the objects you want to appear in the doctest namespace
    """
    doctest_namespace["xmllib"] = xmllib
