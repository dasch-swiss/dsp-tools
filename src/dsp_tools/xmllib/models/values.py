from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from typing import Protocol

from dsp_tools.error.exceptions import InputError
from dsp_tools.error.xmllib_warnings_util import emit_xmllib_input_type_mismatch_warning
from dsp_tools.utils.data_formats.uri_util import is_uri
from dsp_tools.xmllib.models.config_options import Permissions
from dsp_tools.xmllib.value_checkers import check_richtext_syntax
from dsp_tools.xmllib.value_checkers import is_color
from dsp_tools.xmllib.value_checkers import is_date
from dsp_tools.xmllib.value_checkers import is_decimal
from dsp_tools.xmllib.value_checkers import is_geoname
from dsp_tools.xmllib.value_checkers import is_integer
from dsp_tools.xmllib.value_checkers import is_nonempty_value
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

    @classmethod
    def new(
        cls,
        value: Any,
        prop_name: str,
        permissions: Permissions,
        comment: str | None,
        resource_id: str | None,
    ) -> BooleanValue:
        try:
            val = str(convert_to_bool(value)).lower()
        except InputError:
            emit_xmllib_input_type_mismatch_warning(
                expected_type="bool", value=value, res_id=resource_id, prop_name=prop_name
            )
            val = str(value)
        return cls(value=val, prop_name=prop_name, permissions=permissions, comment=comment, resource_id=resource_id)


@dataclass
class ColorValue(Value):
    value: Any
    prop_name: str
    permissions: Permissions = Permissions.PROJECT_SPECIFIC_PERMISSIONS
    comment: str | None = None
    resource_id: str | None = None

    def __post_init__(self) -> None:
        if not is_color(self.value):
            emit_xmllib_input_type_mismatch_warning(
                expected_type="color", value=self.value, res_id=self.resource_id, prop_name=self.prop_name
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
            emit_xmllib_input_type_mismatch_warning(
                expected_type="date", value=self.value, res_id=self.resource_id, prop_name=self.prop_name
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
            emit_xmllib_input_type_mismatch_warning(
                expected_type="decimal", value=self.value, res_id=self.resource_id, prop_name=self.prop_name
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
            emit_xmllib_input_type_mismatch_warning(
                expected_type="geoname", value=self.value, res_id=self.resource_id, prop_name=self.prop_name
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
            emit_xmllib_input_type_mismatch_warning(
                expected_type="integer", value=self.value, res_id=self.resource_id, prop_name=self.prop_name
            )


@dataclass
class LinkValue(Value):
    value: str
    prop_name: str
    permissions: Permissions = Permissions.PROJECT_SPECIFIC_PERMISSIONS
    comment: str | None = None
    resource_id: str | None = None

    def __post_init__(self) -> None:
        if not is_nonempty_value(self.value):
            emit_xmllib_input_type_mismatch_warning(
                expected_type="string", value=self.value, res_id=self.resource_id, prop_name=self.prop_name
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
        if not is_nonempty_value(self.value):
            emit_xmllib_input_type_mismatch_warning(
                expected_type="list node", value=self.value, res_id=self.resource_id, prop_name=self.prop_name
            )
        if not is_nonempty_value(self.list_name):
            emit_xmllib_input_type_mismatch_warning(
                expected_type="list name", value=self.value, res_id=self.resource_id, prop_name=self.prop_name
            )


@dataclass
class SimpleText(Value):
    value: str
    prop_name: str
    permissions: Permissions = Permissions.PROJECT_SPECIFIC_PERMISSIONS
    comment: str | None = None
    resource_id: str | None = None

    def __post_init__(self) -> None:
        if not is_nonempty_value(self.value):
            emit_xmllib_input_type_mismatch_warning(
                expected_type="string", value=self.value, res_id=self.resource_id, prop_name=self.prop_name
            )


@dataclass
class Richtext(Value):
    value: str
    prop_name: str
    permissions: Permissions = Permissions.PROJECT_SPECIFIC_PERMISSIONS
    comment: str | None = None
    resource_id: str | None = None

    def __post_init__(self) -> None:
        if not is_nonempty_value(self.value):
            emit_xmllib_input_type_mismatch_warning(
                expected_type="string", value=self.value, res_id=self.resource_id, prop_name=self.prop_name
            )
        else:
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
            emit_xmllib_input_type_mismatch_warning(
                expected_type="timestamp", value=self.value, res_id=self.resource_id, prop_name=self.prop_name
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
            emit_xmllib_input_type_mismatch_warning(
                expected_type="uri", value=self.value, res_id=self.resource_id, prop_name=self.prop_name
            )
