from __future__ import annotations

import warnings
from dataclasses import dataclass
from typing import Any
from typing import Protocol

from dsp_tools.models.custom_warnings import DspToolsUserWarning
from dsp_tools.models.exceptions import InputError
from dsp_tools.utils.uri_util import is_uri
from dsp_tools.xmllib.models.config_options import Permissions
from dsp_tools.xmllib.value_checkers import check_richtext_syntax
from dsp_tools.xmllib.value_checkers import is_color
from dsp_tools.xmllib.value_checkers import is_date
from dsp_tools.xmllib.value_checkers import is_decimal
from dsp_tools.xmllib.value_checkers import is_geoname
from dsp_tools.xmllib.value_checkers import is_integer
from dsp_tools.xmllib.value_checkers import is_string_like
from dsp_tools.xmllib.value_checkers import is_timestamp
from dsp_tools.xmllib.value_converters import convert_to_bool


class Value(Protocol):
    value: Any
    prop_name: str
    permissions: Permissions
    comment: str | None
    resource_id: str | None


@dataclass
class BooleanValue(Value):
    value: Any
    prop_name: str
    permissions: Permissions = Permissions.PROJECT_SPECIFIC_PERMISSIONS
    comment: str | None = None
    resource_id: str | None = None

    def __post_init__(self) -> None:
        try:
            converted_bool = convert_to_bool(self.value)
            self.value = str(converted_bool).lower()
        except InputError:
            _warn_type_mismatch(
                expected_type="bool", value=self.value, prop_name=self.prop_name, res_id=self.resource_id
            )
            self.value = str(self.value)


@dataclass
class ColorValue(Value):
    value: Any
    prop_name: str
    permissions: Permissions = Permissions.PROJECT_SPECIFIC_PERMISSIONS
    comment: str | None = None
    resource_id: str | None = None

    def __post_init__(self) -> None:
        if not is_color(self.value):
            _warn_type_mismatch(
                expected_type="color", value=self.value, prop_name=self.prop_name, res_id=self.resource_id
            )


@dataclass
class DateValue(Value):
    value: str
    prop_name: str
    permissions: Permissions = Permissions.PROJECT_SPECIFIC_PERMISSIONS
    comment: str | None = None
    resource_id: str | None = None

    def __post_init__(self) -> None:
        if not is_date(self.value):
            _warn_type_mismatch(
                expected_type="date", value=self.value, prop_name=self.prop_name, res_id=self.resource_id
            )


@dataclass
class DecimalValue(Value):
    value: Any
    prop_name: str
    permissions: Permissions = Permissions.PROJECT_SPECIFIC_PERMISSIONS
    comment: str | None = None
    resource_id: str | None = None

    def __post_init__(self) -> None:
        if not is_decimal(self.value):
            _warn_type_mismatch(
                expected_type="decimal", value=self.value, prop_name=self.prop_name, res_id=self.resource_id
            )


@dataclass
class GeonameValue(Value):
    value: Any
    prop_name: str
    permissions: Permissions = Permissions.PROJECT_SPECIFIC_PERMISSIONS
    comment: str | None = None
    resource_id: str | None = None

    def __post_init__(self) -> None:
        if not is_geoname(self.value):
            _warn_type_mismatch(
                expected_type="geoname", value=self.value, prop_name=self.prop_name, res_id=self.resource_id
            )


@dataclass
class IntValue(Value):
    value: int | str
    prop_name: str
    permissions: Permissions = Permissions.PROJECT_SPECIFIC_PERMISSIONS
    comment: str | None = None
    resource_id: str | None = None

    def __post_init__(self) -> None:
        if not is_integer(self.value):
            _warn_type_mismatch(
                expected_type="integer", value=self.value, prop_name=self.prop_name, res_id=self.resource_id
            )


@dataclass
class LinkValue(Value):
    value: str
    prop_name: str
    permissions: Permissions = Permissions.PROJECT_SPECIFIC_PERMISSIONS
    comment: str | None = None
    resource_id: str | None = None

    def __post_init__(self) -> None:
        if not is_string_like(self.value):
            _warn_type_mismatch(
                expected_type="string", value=self.value, prop_name=self.prop_name, res_id=self.resource_id
            )


@dataclass
class ListValue(Value):
    value: Any
    list_name: Any
    prop_name: str
    permissions: Permissions = Permissions.PROJECT_SPECIFIC_PERMISSIONS
    comment: str | None = None
    resource_id: str | None = None

    def __post_init__(self) -> None:
        if not is_string_like(self.value) or not is_string_like(self.list_name):
            _warn_type_mismatch(
                expected_type="list", value=self.value, prop_name=self.prop_name, res_id=self.resource_id
            )


@dataclass
class SimpleText(Value):
    value: str
    prop_name: str
    permissions: Permissions = Permissions.PROJECT_SPECIFIC_PERMISSIONS
    comment: str | None = None
    resource_id: str | None = None

    def __post_init__(self) -> None:
        if not is_string_like(self.value):
            _warn_type_mismatch(
                expected_type="string", value=self.value, prop_name=self.prop_name, res_id=self.resource_id
            )


@dataclass
class Richtext(Value):
    value: str
    prop_name: str
    permissions: Permissions = Permissions.PROJECT_SPECIFIC_PERMISSIONS
    comment: str | None = None
    resource_id: str | None = None

    def __post_init__(self) -> None:
        if not is_string_like(self.value):
            _warn_type_mismatch(
                expected_type="string", value=self.value, prop_name=self.prop_name, res_id=self.resource_id
            )
        check_richtext_syntax(self.value)


@dataclass
class TimeValue(Value):
    value: str
    prop_name: str
    permissions: Permissions = Permissions.PROJECT_SPECIFIC_PERMISSIONS
    comment: str | None = None
    resource_id: str | None = None

    def __post_init__(self) -> None:
        if not is_timestamp(self.value):
            _warn_type_mismatch(
                expected_type="timestamp", value=self.value, prop_name=self.prop_name, res_id=self.resource_id
            )


@dataclass
class UriValue(Value):
    value: str
    prop_name: str
    permissions: Permissions = Permissions.PROJECT_SPECIFIC_PERMISSIONS
    comment: str | None = None
    resource_id: str | None = None

    def __post_init__(self) -> None:
        if not is_uri(self.value):
            _warn_type_mismatch(
                expected_type="uri", value=self.value, prop_name=self.prop_name, res_id=self.resource_id
            )


def _warn_type_mismatch(expected_type: str, value: Any, prop_name: str, res_id: str | None) -> None:
    """Emits a warning if a values is not in the expected format."""
    msg = f"At the following location a '{expected_type}' does not conform to the expected format.\n"
    msg += f"Resource: {res_id} | " if res_id else ""
    msg += f"Value: {value} | Property: {prop_name}"
    warnings.warn(DspToolsUserWarning(msg))
