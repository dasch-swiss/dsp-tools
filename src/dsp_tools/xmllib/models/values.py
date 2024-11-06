from __future__ import annotations

import warnings
from dataclasses import dataclass
from typing import Any
from typing import Protocol

from lxml import etree

from dsp_tools.models.custom_warnings import DspToolsUserWarning
from dsp_tools.utils.uri_util import is_uri
from dsp_tools.xmllib.models.config_options import Permissions
from dsp_tools.xmllib.value_checkers import is_bool_like
from dsp_tools.xmllib.value_checkers import is_color
from dsp_tools.xmllib.value_checkers import is_date
from dsp_tools.xmllib.value_checkers import is_decimal
from dsp_tools.xmllib.value_checkers import is_geoname
from dsp_tools.xmllib.value_checkers import is_integer
from dsp_tools.xmllib.value_checkers import is_string_like
from dsp_tools.xmllib.value_checkers import is_timestamp
from dsp_tools.xmllib.value_converters import convert_to_bool_string

XML_NAMESPACE_MAP = {None: "https://dasch.swiss/schema", "xsi": "http://www.w3.org/2001/XMLSchema-instance"}
DASCH_SCHEMA = "{https://dasch.swiss/schema}"


class Value(Protocol):
    value: Any
    prop_name: str
    permissions: Permissions
    comment: str | None
    resource_id: str | None

    def serialise(self) -> etree._Element:
        raise NotImplementedError

    def make_prop(self) -> etree._Element:
        raise NotImplementedError

    def make_element(self) -> etree._Element:
        raise NotImplementedError


@dataclass
class BooleanValue(Value):
    value: Any
    prop_name: str
    permissions: Permissions = Permissions.PROJECT_SPECIFIC_PERMISSIONS
    comment: str | None = None
    resource_id: str | None = None

    def __post_init__(self) -> None:
        if not is_bool_like(self.value):
            _warn_type_mismatch(
                expected_type="bool", value=self.value, prop_name=self.prop_name, res_id=self.resource_id
            )
        self.value = convert_to_bool_string(self.value)

    def serialise(self) -> etree._Element:
        ele = self.make_prop()
        ele.append(self.make_element())
        return ele

    def make_prop(self) -> etree._Element:
        return etree.Element(f"{DASCH_SCHEMA}boolean-prop", name=self.prop_name, nsmap=XML_NAMESPACE_MAP)

    def make_element(self) -> etree._Element:
        attribs = (
            {"permissions": self.permissions.value}
            if self.permissions != Permissions.PROJECT_SPECIFIC_PERMISSIONS
            else {}
        )
        if self.comment:
            attribs["comment"] = self.comment
        ele = etree.Element(f"{DASCH_SCHEMA}boolean", attrib=attribs, nsmap=XML_NAMESPACE_MAP)
        ele.text = str(self.value)
        return ele


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

    def serialise(self) -> etree._Element:
        ele = self.make_prop()
        ele.append(self.make_element())
        return ele

    def make_prop(self) -> etree._Element:
        return etree.Element(f"{DASCH_SCHEMA}color-prop", name=self.prop_name, nsmap=XML_NAMESPACE_MAP)

    def make_element(self) -> etree._Element:
        attribs = (
            {"permissions": self.permissions.value}
            if self.permissions != Permissions.PROJECT_SPECIFIC_PERMISSIONS
            else {}
        )
        if self.comment:
            attribs["comment"] = self.comment
        ele = etree.Element(f"{DASCH_SCHEMA}color", attrib=attribs, nsmap=XML_NAMESPACE_MAP)
        ele.text = str(self.value)
        return ele


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

    def serialise(self) -> etree._Element:
        ele = self.make_prop()
        ele.append(self.make_element())
        return ele

    def make_prop(self) -> etree._Element:
        return etree.Element(f"{DASCH_SCHEMA}date-prop", name=self.prop_name, nsmap=XML_NAMESPACE_MAP)

    def make_element(self) -> etree._Element:
        attribs = (
            {"permissions": self.permissions.value}
            if self.permissions != Permissions.PROJECT_SPECIFIC_PERMISSIONS
            else {}
        )
        if self.comment:
            attribs["comment"] = self.comment
        ele = etree.Element(f"{DASCH_SCHEMA}date", attrib=attribs, nsmap=XML_NAMESPACE_MAP)
        ele.text = str(self.value)
        return ele


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

    def serialise(self) -> etree._Element:
        ele = self.make_prop()
        ele.append(self.make_element())
        return ele

    def make_prop(self) -> etree._Element:
        return etree.Element(f"{DASCH_SCHEMA}decimal-prop", name=self.prop_name, nsmap=XML_NAMESPACE_MAP)

    def make_element(self) -> etree._Element:
        attribs = (
            {"permissions": self.permissions.value}
            if self.permissions != Permissions.PROJECT_SPECIFIC_PERMISSIONS
            else {}
        )
        if self.comment:
            attribs["comment"] = self.comment
        ele = etree.Element(f"{DASCH_SCHEMA}decimal", attrib=attribs, nsmap=XML_NAMESPACE_MAP)
        ele.text = str(self.value)
        return ele


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

    def serialise(self) -> etree._Element:
        ele = self.make_prop()
        ele.append(self.make_element())
        return ele

    def make_prop(self) -> etree._Element:
        return etree.Element(f"{DASCH_SCHEMA}geoname-prop", name=self.prop_name, nsmap=XML_NAMESPACE_MAP)

    def make_element(self) -> etree._Element:
        attribs = (
            {"permissions": self.permissions.value}
            if self.permissions != Permissions.PROJECT_SPECIFIC_PERMISSIONS
            else {}
        )
        if self.comment:
            attribs["comment"] = self.comment
        ele = etree.Element(f"{DASCH_SCHEMA}geoname", attrib=attribs, nsmap=XML_NAMESPACE_MAP)
        ele.text = str(self.value)
        return ele


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

    def serialise(self) -> etree._Element:
        ele = self.make_prop()
        ele.append(self.make_element())
        return ele

    def make_prop(self) -> etree._Element:
        return etree.Element(f"{DASCH_SCHEMA}integer-prop", name=self.prop_name, nsmap=XML_NAMESPACE_MAP)

    def make_element(self) -> etree._Element:
        attribs = (
            {"permissions": self.permissions.value}
            if self.permissions != Permissions.PROJECT_SPECIFIC_PERMISSIONS
            else {}
        )
        if self.comment:
            attribs["comment"] = self.comment
        ele = etree.Element(f"{DASCH_SCHEMA}integer", attrib=attribs, nsmap=XML_NAMESPACE_MAP)
        ele.text = str(self.value)
        return ele


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

    def serialise(self) -> etree._Element:
        ele = self.make_prop()
        ele.append(self.make_element())
        return ele

    def make_prop(self) -> etree._Element:
        return etree.Element(f"{DASCH_SCHEMA}resptr-prop", name=self.prop_name, nsmap=XML_NAMESPACE_MAP)

    def make_element(self) -> etree._Element:
        attribs = (
            {"permissions": self.permissions.value}
            if self.permissions != Permissions.PROJECT_SPECIFIC_PERMISSIONS
            else {}
        )
        if self.comment:
            attribs["comment"] = self.comment
        ele = etree.Element(f"{DASCH_SCHEMA}resptr", attrib=attribs, nsmap=XML_NAMESPACE_MAP)
        ele.text = self.value
        return ele


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

    def serialise(self) -> etree._Element:
        ele = self.make_prop()
        ele.append(self.make_element())
        return ele

    def make_prop(self) -> etree._Element:
        return etree.Element(
            f"{DASCH_SCHEMA}list-prop", name=self.prop_name, list=self.list_name, nsmap=XML_NAMESPACE_MAP
        )

    def make_element(self) -> etree._Element:
        attribs = (
            {"permissions": self.permissions.value}
            if self.permissions != Permissions.PROJECT_SPECIFIC_PERMISSIONS
            else {}
        )
        if self.comment:
            attribs["comment"] = self.comment
        ele = etree.Element(f"{DASCH_SCHEMA}list", attrib=attribs, nsmap=XML_NAMESPACE_MAP)
        ele.text = self.value
        return ele


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

    def serialise(self) -> etree._Element:
        ele = self.make_prop()
        ele.append(self.make_element())
        return ele

    def make_prop(self) -> etree._Element:
        return etree.Element(f"{DASCH_SCHEMA}text-prop", name=self.prop_name, nsmap=XML_NAMESPACE_MAP)

    def make_element(self) -> etree._Element:
        attribs = {"encoding": "utf8"}
        if self.permissions != Permissions.PROJECT_SPECIFIC_PERMISSIONS:
            attribs["permissions"] = self.permissions.value
        if self.comment:
            attribs["comment"] = self.comment
        ele = etree.Element(f"{DASCH_SCHEMA}text", attrib=attribs, nsmap=XML_NAMESPACE_MAP)
        ele.text = self.value
        return ele


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

    def serialise(self) -> etree._Element:
        ele = self.make_prop()
        ele.append(self.make_element())
        return ele

    def make_prop(self) -> etree._Element:
        return etree.Element(f"{DASCH_SCHEMA}text-prop", name=self.prop_name, nsmap=XML_NAMESPACE_MAP)

    def make_element(self) -> etree._Element:
        attribs = {"encoding": "xml"}
        if self.permissions != Permissions.PROJECT_SPECIFIC_PERMISSIONS:
            attribs["permissions"] = self.permissions.value
        if self.comment:
            attribs["comment"] = self.comment
        ele = etree.Element(f"{DASCH_SCHEMA}text", attrib=attribs, nsmap=XML_NAMESPACE_MAP)
        ele.text = self.value
        return ele


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

    def serialise(self) -> etree._Element:
        ele = self.make_prop()
        ele.append(self.make_element())
        return ele

    def make_prop(self) -> etree._Element:
        return etree.Element(f"{DASCH_SCHEMA}time-prop", name=self.prop_name, nsmap=XML_NAMESPACE_MAP)

    def make_element(self) -> etree._Element:
        attribs = (
            {"permissions": self.permissions.value}
            if self.permissions != Permissions.PROJECT_SPECIFIC_PERMISSIONS
            else {}
        )
        if self.comment:
            attribs["comment"] = self.comment
        ele = etree.Element(f"{DASCH_SCHEMA}time", attrib=attribs, nsmap=XML_NAMESPACE_MAP)
        ele.text = self.value
        return ele


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

    def serialise(self) -> etree._Element:
        ele = self.make_prop()
        ele.append(self.make_element())
        return ele

    def make_prop(self) -> etree._Element:
        return etree.Element(f"{DASCH_SCHEMA}uri-prop", name=self.prop_name, nsmap=XML_NAMESPACE_MAP)

    def make_element(self) -> etree._Element:
        attribs = (
            {"permissions": self.permissions.value}
            if self.permissions != Permissions.PROJECT_SPECIFIC_PERMISSIONS
            else {}
        )
        if self.comment:
            attribs["comment"] = self.comment
        ele = etree.Element(f"{DASCH_SCHEMA}uri", attrib=attribs, nsmap=XML_NAMESPACE_MAP)
        ele.text = self.value
        return ele


def _warn_type_mismatch(expected_type: str, value: Any, prop_name: str, res_id: str | None) -> None:
    """Emits a warning if a values is not in the expected format."""
    msg = f"At the following location a '{expected_type}' does not conform to the expected format.\n"
    msg += f"Resource: {res_id} | " if res_id else ""
    msg += f"Value: {value} | Property: {prop_name}"
    warnings.warn(DspToolsUserWarning(msg))
