from __future__ import annotations

import warnings
from dataclasses import dataclass
from typing import Any
from typing import Protocol

from lxml import etree

from dsp_tools.commands.xmllib.value_checkers import is_integer
from dsp_tools.commands.xmllib.value_checkers import is_string
from dsp_tools.models.custom_warnings import DspToolsUserWarning

XML_NAMESPACE_MAP = {None: "https://dasch.swiss/schema", "xsi": "http://www.w3.org/2001/XMLSchema-instance"}
DASCH_SCHEMA = "{https://dasch.swiss/schema}"


@dataclass
class Value(Protocol):
    value: Any
    prop_name: str
    permissions: str | None
    comment: str | None
    resource_id: str | None

    def serialise(self) -> etree._Element:
        raise NotImplementedError

    def make_prop(self) -> etree._Element:
        raise NotImplementedError

    def make_element(self) -> etree._Element:
        raise NotImplementedError


@dataclass
class BooleanValue:
    value: Any
    prop_name: str
    permissions: str | None = "prop-default"
    comment: str | None = None
    resource_id: str | None = None

    def serialise(self) -> etree._Element:
        raise NotImplementedError

    def make_prop(self) -> etree._Element:
        raise NotImplementedError

    def make_element(self) -> etree._Element:
        raise NotImplementedError


@dataclass
class ColorValue:
    value: Any
    prop_name: str
    permissions: str | None = "prop-default"
    comment: str | None = None
    resource_id: str | None = None

    def serialise(self) -> etree._Element:
        raise NotImplementedError

    def make_prop(self) -> etree._Element:
        raise NotImplementedError

    def make_element(self) -> etree._Element:
        raise NotImplementedError


@dataclass
class DateValue:
    value: Any
    prop_name: str
    permissions: str | None = "prop-default"
    comment: str | None = None
    resource_id: str | None = None

    def serialise(self) -> etree._Element:
        raise NotImplementedError

    def make_prop(self) -> etree._Element:
        raise NotImplementedError

    def make_element(self) -> etree._Element:
        raise NotImplementedError


@dataclass
class DecimalValue:
    value: Any
    prop_name: str
    permissions: str | None = "prop-default"
    comment: str | None = None
    resource_id: str | None = None

    def serialise(self) -> etree._Element:
        raise NotImplementedError

    def make_prop(self) -> etree._Element:
        raise NotImplementedError

    def make_element(self) -> etree._Element:
        raise NotImplementedError


@dataclass
class GeonameValue:
    value: Any
    prop_name: str
    permissions: str | None = "prop-default"
    comment: str | None = None
    resource_id: str | None = None

    def serialise(self) -> etree._Element:
        raise NotImplementedError

    def make_prop(self) -> etree._Element:
        raise NotImplementedError

    def make_element(self) -> etree._Element:
        raise NotImplementedError


@dataclass
class IntValue:
    value: int | str
    prop_name: str
    permissions: str | None = "prop-default"
    comment: str | None = None
    resource_id: str | None = None

    def __post_init__(self) -> None:
        if not is_integer(self.value):
            _warn_type_mismatch(expected_type="integer", value=self.value, prop_name=self.prop_name)

    def serialise(self) -> etree._Element:
        ele = self.make_prop()
        ele.append(self.make_element())
        return ele

    def make_prop(self) -> etree._Element:
        return etree.Element(f"{DASCH_SCHEMA}integer-prop", name=self.prop_name, nsmap=XML_NAMESPACE_MAP)

    def make_element(self) -> etree._Element:
        attribs = {}
        if self.permissions:
            attribs["permissions"] = self.permissions
        if self.comment:
            attribs["comment"] = self.comment
        ele = etree.Element(f"{DASCH_SCHEMA}integer", attrib=attribs, nsmap=XML_NAMESPACE_MAP)
        ele.text = str(self.value)
        return ele


@dataclass
class LinkValue:
    value: str
    prop_name: str
    permissions: str | None = "prop-default"
    comment: str | None = None
    resource_id: str | None = None

    def __post_init__(self) -> None:
        if not is_string(self.value):
            _warn_type_mismatch(expected_type="string", value=self.value, prop_name=self.prop_name)

    def serialise(self) -> etree._Element:
        ele = self.make_prop()
        ele.append(self.make_element())
        return ele

    def make_prop(self) -> etree._Element:
        return etree.Element(f"{DASCH_SCHEMA}resptr-prop", name=self.prop_name, nsmap=XML_NAMESPACE_MAP)

    def make_element(self) -> etree._Element:
        attribs = {}
        if self.permissions:
            attribs["permissions"] = self.permissions
        if self.comment:
            attribs["comment"] = self.comment
        ele = etree.Element(f"{DASCH_SCHEMA}resptr", attrib=attribs, nsmap=XML_NAMESPACE_MAP)
        ele.text = self.value
        return ele


@dataclass
class ListValue:
    value: Any
    list_name: Any
    prop_name: str
    permissions: str | None = "prop-default"
    comment: str | None = None
    resource_id: str | None = None

    def serialise(self) -> etree._Element:
        raise NotImplementedError

    def make_prop(self) -> etree._Element:
        raise NotImplementedError

    def make_element(self) -> etree._Element:
        raise NotImplementedError


@dataclass
class SimpleText:
    value: str
    prop_name: str
    permissions: str | None = "prop-default"
    comment: str | None = None
    resource_id: str | None = None

    def __post_init__(self) -> None:
        if not is_string(self.value):
            _warn_type_mismatch(expected_type="string", value=self.value, prop_name=self.prop_name)

    def serialise(self) -> etree._Element:
        ele = self.make_prop()
        ele.append(self.make_element())
        return ele

    def make_prop(self) -> etree._Element:
        return etree.Element(f"{DASCH_SCHEMA}text-prop", name=self.prop_name, nsmap=XML_NAMESPACE_MAP)

    def make_element(self) -> etree._Element:
        attribs = {"encoding": "utf8"}
        if self.permissions:
            attribs["permissions"] = self.permissions
        if self.comment:
            attribs["comment"] = self.comment
        ele = etree.Element(f"{DASCH_SCHEMA}text", attrib=attribs, nsmap=XML_NAMESPACE_MAP)
        ele.text = self.value
        return ele


@dataclass
class Richtext:
    value: Any
    prop_name: str
    permissions: str | None = "prop-default"
    comment: str | None = None
    resource_id: str | None = None

    def serialise(self) -> etree._Element:
        raise NotImplementedError

    def make_prop(self) -> etree._Element:
        raise NotImplementedError

    def make_element(self) -> etree._Element:
        raise NotImplementedError


@dataclass
class TimeValue:
    value: Any
    prop_name: str
    permissions: str | None = "prop-default"
    comment: str | None = None
    resource_id: str | None = None

    def serialise(self) -> etree._Element:
        raise NotImplementedError

    def make_prop(self) -> etree._Element:
        raise NotImplementedError

    def make_element(self) -> etree._Element:
        raise NotImplementedError


@dataclass
class UriValue:
    value: Any
    prop_name: str
    permissions: str | None = "prop-default"
    comment: str | None = None
    resource_id: str | None = None

    def serialise(self) -> etree._Element:
        raise NotImplementedError

    def make_prop(self) -> etree._Element:
        raise NotImplementedError

    def make_element(self) -> etree._Element:
        raise NotImplementedError


def _warn_type_mismatch(expected_type: str, value: Any, prop_name: str, res_id: str | None) -> None:
    """Emits a warning if a values is not in the expected format."""
    msg = f"At the following location a '{expected_type}' does not conform to the expected format.\n"
    msg += f"Resource: {res_id} | " if res_id else ""
    msg += f"Value: {value} | Property: {prop_name}"
    warnings.warn(DspToolsUserWarning(msg))
