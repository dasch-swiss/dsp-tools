from __future__ import annotations

import warnings
from dataclasses import dataclass
from typing import Any

import pandas as pd
from lxml import etree

from dsp_tools.commands.xmllib.value_checkers import is_integer
from dsp_tools.models.custom_warnings import DspToolsUserWarning

"""
Advantage: 
    Creation and usage separated
    Res ID is included in the warning
Disadvantage: 
    Value classes can be instantiated without check (otherwise we would get duplicate warnings)
    Each value also needs a dedicated factory.
"""


class IntValueFactory:
    def create(
        self,
        value: int | str,
        prop_name: str,
        res_id: str,
        permissions: str | None = "prop-default",
        comment: str | None = None,
    ) -> IntValue:
        if not is_integer(value):
            _warn_type_mismatch(expected_type="integer", value=value, prop_name=prop_name, res_id=res_id)
        return IntValue(value=value, prop_name=prop_name, permissions=permissions, comment=comment)

    def create_several(
        self,
        values: list[int | str],
        prop_name: str,
        res_id: str,
        permissions: str | None = "prop-default",
        comment: str | None = None,
    ) -> list[IntValue]:
        return [
            self.create(value=x, prop_name=prop_name, res_id=res_id, permissions=permissions, comment=comment)
            for x in values
        ]

    def create_optional(
        self,
        value: int | str,
        prop_name: str,
        res_id: str,
        permissions: str | None = "prop-default",
        comment: str | None = None,
    ) -> IntValue | None:
        if not pd.isna(value):
            return self.create(
                value=value, prop_name=prop_name, res_id=res_id, permissions=permissions, comment=comment
            )
        return None


@dataclass
class IntValue:
    value: int | str
    prop_name: str
    permissions: str | None = "prop-default"
    comment: str | None = None

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
