from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from typing import Protocol

from dsp_tools.error.exceptions import InputError
from dsp_tools.error.xmllib_warnings_util import emit_xmllib_input_type_mismatch_warning
from dsp_tools.utils.data_formats.uri_util import is_uri
from dsp_tools.xmllib.internal_helpers import check_and_warn_potentially_empty_string
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

    def __post_init__(self) -> None:
        try:
            converted_bool = convert_to_bool(self.value)
            self.value = str(converted_bool).lower()
        except InputError:
            emit_xmllib_input_type_mismatch_warning(
                expected_type="bool", value=self.value, res_id=self.resource_id, prop_name=self.prop_name
            )
            self.value = str(self.value)
        if self.comment is not None:
            check_and_warn_potentially_empty_string(
                value=self.comment,
                res_id=self.resource_id,
                expected="string",
                prop_name=self.prop_name,
                field="comment on value",
            )


@dataclass
class ColorValue(Value):
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
    ) -> ColorValue:
        if not is_color(value):
            emit_xmllib_input_type_mismatch_warning(
                expected_type="color", value=value, res_id=resource_id, prop_name=prop_name
            )
        if comment is not None:
            check_and_warn_potentially_empty_string(
                value=comment,
                res_id=resource_id,
                expected="string",
                prop_name=prop_name,
                field="comment on value",
            )
        return cls(value=str(value), prop_name=prop_name, permissions=permissions, comment=comment)


@dataclass
class DateValue(Value):
    value: str
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
    ) -> DateValue:
        if not is_date(value):
            emit_xmllib_input_type_mismatch_warning(
                expected_type="date", value=value, res_id=resource_id, prop_name=prop_name
            )
        if comment is not None:
            check_and_warn_potentially_empty_string(
                value=comment,
                res_id=resource_id,
                expected="string",
                prop_name=prop_name,
                field="comment on value",
            )
        return cls(value=str(value), prop_name=prop_name, permissions=permissions, comment=comment)


@dataclass
class DecimalValue(Value):
    value: str | float | int
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
    ) -> DecimalValue:
        if not is_decimal(value):
            emit_xmllib_input_type_mismatch_warning(
                expected_type="decimal", value=value, res_id=resource_id, prop_name=prop_name
            )
        if comment is not None:
            check_and_warn_potentially_empty_string(
                value=comment,
                res_id=resource_id,
                expected="string",
                prop_name=prop_name,
                field="comment on value",
            )
        return cls(value=str(value), prop_name=prop_name, permissions=permissions, comment=comment)


@dataclass
class GeonameValue(Value):
    value: str
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
    ) -> GeonameValue:
        if not is_geoname(value):
            emit_xmllib_input_type_mismatch_warning(
                expected_type="geoname", value=value, res_id=resource_id, prop_name=prop_name
            )
        if comment is not None:
            check_and_warn_potentially_empty_string(
                value=comment,
                res_id=resource_id,
                expected="string",
                prop_name=prop_name,
                field="comment on value",
            )
        return cls(value=str(value), prop_name=prop_name, permissions=permissions, comment=comment)


@dataclass
class IntValue(Value):
    value: int | str
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
    ) -> IntValue:
        if not is_integer(value):
            emit_xmllib_input_type_mismatch_warning(
                expected_type="integer", value=value, res_id=resource_id, prop_name=prop_name
            )
        if comment is not None:
            check_and_warn_potentially_empty_string(
                value=comment,
                res_id=resource_id,
                expected="string",
                prop_name=prop_name,
                field="comment on value",
            )
        return cls(value=str(value), prop_name=prop_name, permissions=permissions, comment=comment)


@dataclass
class LinkValue(Value):
    value: str
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
    ) -> LinkValue:
        if not is_nonempty_value(value):
            emit_xmllib_input_type_mismatch_warning(
                expected_type="string", value=value, res_id=resource_id, prop_name=prop_name
            )
        if comment is not None:
            check_and_warn_potentially_empty_string(
                value=comment,
                res_id=resource_id,
                expected="string",
                prop_name=prop_name,
                field="comment on value",
            )
        return cls(value=str(value), prop_name=prop_name, permissions=permissions, comment=comment)


@dataclass
class ListValue(Value):
    value: Any
    list_name: Any
    prop_name: str
    permissions: Permissions = Permissions.PROJECT_SPECIFIC_PERMISSIONS
    comment: str | None = None
    resource_id: str | None = None

    @classmethod
    def new(
        cls,
        value: Any,
        list_name: Any,
        prop_name: str,
        permissions: Permissions,
        comment: str | None,
        resource_id: str | None,
    ) -> ListValue:
        if not is_nonempty_value(value):
            emit_xmllib_input_type_mismatch_warning(
                expected_type="list node", value=value, res_id=resource_id, prop_name=prop_name
            )
        if not is_nonempty_value(value):
            emit_xmllib_input_type_mismatch_warning(
                expected_type="list name", value=list_name, res_id=resource_id, prop_name=prop_name
            )
        if comment is not None:
            check_and_warn_potentially_empty_string(
                value=comment,
                res_id=resource_id,
                expected="string",
                prop_name=prop_name,
                field="comment on value",
            )
        return cls(
            value=str(value), list_name=str(list_name), prop_name=prop_name, permissions=permissions, comment=comment
        )


@dataclass
class SimpleText(Value):
    value: str
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
    ) -> SimpleText:
        check_and_warn_potentially_empty_string(
            value=value,
            res_id=resource_id,
            expected="string",
            prop_name=prop_name,
        )
        if comment is not None:
            check_and_warn_potentially_empty_string(
                value=comment,
                res_id=resource_id,
                expected="string",
                prop_name=prop_name,
                field="comment on value",
            )
        return cls(value=str(value), prop_name=prop_name, permissions=permissions, comment=comment)


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
        if self.comment is not None:
            check_and_warn_potentially_empty_string(
                value=self.comment,
                res_id=self.resource_id,
                expected="string",
                prop_name=self.prop_name,
                field="comment on value",
            )


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
        if self.comment is not None:
            check_and_warn_potentially_empty_string(
                value=self.comment,
                res_id=self.resource_id,
                expected="string",
                prop_name=self.prop_name,
                field="comment on value",
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
        if self.comment is not None:
            check_and_warn_potentially_empty_string(
                value=self.comment,
                res_id=self.resource_id,
                expected="string",
                prop_name=self.prop_name,
                field="comment on value",
            )
