from __future__ import annotations

import warnings
from typing import Any

from lxml import etree

from dsp_tools.commands.xmllib.value_checkers import is_integer
from dsp_tools.models.custom_warnings import DspToolsUserWarning

"""
Advantage: 
    Validation always happens at creation.
    Resource ID is communicated during a warning
Disadvantage: 
    __init__ is wordy
"""


class IntValue:
    value: int | str
    prop_name: str
    permissions: str | None = "prop-default"
    comment: str | None = None

    def __init__(
        self,
        value: int | str,
        prop_name: str,
        permissions: str | None = "prop-default",
        comment: str | None = None,
        res_id: str | None = None,
    ) -> None:
        self.value = value
        self.prop_name = prop_name
        self.permissions = permissions
        self.comment = comment

        if not is_integer(self.value):
            _warn_type_mismatch(expected_type="integer", value=self.value, prop_name=self.prop_name, res_id=res_id)

    def serialise(self) -> etree._Element:
        pass

    def make_prop(self) -> etree._Element:
        pass

    def make_element(self) -> etree._Element:
        pass


def _warn_type_mismatch(expected_type: str, value: Any, prop_name: str, res_id: str) -> None:
    """Emits a warning if a values is not in the expected format."""
    msg = (
        f"The resource '{res_id}' with the value '{value}' and the property {prop_name}, is invalid. "
        f"The expected type is {expected_type}."
    )
    warnings.warn(DspToolsUserWarning(msg))
