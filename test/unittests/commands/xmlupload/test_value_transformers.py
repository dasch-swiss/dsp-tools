from typing import Any

import pytest
from rdflib import XSD
from rdflib import Literal

from dsp_tools.commands.xmlupload.value_transformers import transform_xsd_boolean
from dsp_tools.models.exceptions import BaseError


@pytest.mark.parametrize(
    ("input_bool", "success"),
    [
        ("true", True),
        ("True", True),
        ("1", True),
        (1, True),
        (True, True),
        ("false", False),
        ("False", False),
        ("0", False),
        (0, False),
        (False, False),
    ],
)
def test_transform_boolean_success(input_bool: Any, success: bool) -> None:
    result = transform_xsd_boolean(input_bool)
    assert result == Literal(success, datatype=XSD.boolean)


def test_transform_boolean_raises_string() -> None:
    with pytest.raises(BaseError):
        transform_xsd_boolean("foo")


def test_transform_boolean_raises_int() -> None:
    with pytest.raises(BaseError):
        transform_xsd_boolean(2)
