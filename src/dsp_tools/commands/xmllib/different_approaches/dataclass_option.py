from __future__ import annotations

import warnings
from dataclasses import dataclass
from typing import Any

from lxml import etree

from dsp_tools.commands.xmllib.value_checkers import is_integer
from dsp_tools.models.custom_warnings import DspToolsUserWarning

"""
Advantage: 
    Validation always happens at creation.
Disadvantage: 
    Resource ID is not provided in the warnings message.
"""


@dataclass
class IntValue:
    value: int | str
    prop_name: str
    permissions: str | None = "prop-default"
    comment: str | None = None

    def __post_init__(self) -> None:
        if not is_integer(self.value):
            _warn_type_mismatch(expected_type="integer", value=self.value, prop_name=self.prop_name)

    def serialise(self) -> etree._Element:
        pass

    def make_prop(self) -> etree._Element:
        pass

    def make_element(self) -> etree._Element:
        pass


def _warn_type_mismatch(expected_type: str, value: Any, prop_name: str) -> None:
    """Emits a warning if a values is not in the expected format."""
    msg = f"The value '{value}' with the property {prop_name}, is invalid. The expected type is {expected_type}"
    warnings.warn(DspToolsUserWarning(msg))
