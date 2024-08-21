from __future__ import annotations

import warnings
from dataclasses import dataclass
from typing import Any

from lxml import etree

from dsp_tools.commands.xmllib.utils import is_string
from dsp_tools.models.custom_warnings import DspToolsUserWarning

XML_NAMESPACE_MAP = {None: "https://dasch.swiss/schema", "xsi": "http://www.w3.org/2001/XMLSchema-instance"}
DASCH_SCHEMA = "{https://dasch.swiss/schema}"


@dataclass
class Value:
    value: Any
    property: str
    permissions: str | None
    comment: str | None

    def serialise(self) -> etree._Element:
        raise NotImplementedError

    def make_prop(self) -> etree._Element:
        raise NotImplementedError

    def make_element(self) -> etree._Element:
        raise NotImplementedError


@dataclass
class Richtext(Value):
    value: str
    property: str
    permissions: str | None = "prop-default"
    comment: str | None = None
    preserve_linebreaks: bool = False

    def __post_init__(self) -> None:
        if not is_string(self.value):
            msg = f"The following value is not a valid string.\nValue: {self.value} | Property: {self.property}"
            warnings.warn(DspToolsUserWarning(msg))
            self.value = str(self.value)
        if self.preserve_linebreaks:
            self.value = self.value.replace("\n", "<br/>")

    def serialise(self) -> etree._Element:
        ele = self.make_prop()
        ele.append(self.make_element())
        return ele

    def make_prop(self) -> etree._Element:
        return etree.Element(f"{DASCH_SCHEMA}text-prop", name=self.property, nsmap=XML_NAMESPACE_MAP)

    def make_element(self) -> etree._Element:
        attribs = {"encoding": "xml"}
        if self.permissions:
            attribs["permissions"] = self.permissions
        if self.comment:
            attribs["comment"] = self.comment
        ele = etree.Element(f"{DASCH_SCHEMA}text", attrib=attribs, nsmap=XML_NAMESPACE_MAP)
        ele.text = self.value
        return ele


@dataclass
class Textarea(Value):
    value: str
    property: str
    permissions: str | None = "prop-default"
    comment: str | None = None

    def __post_init__(self) -> None:
        if not is_string(self.value):
            msg = f"The following value is not a valid string.\nValue: {self.value} | Property: {self.property}"
            warnings.warn(DspToolsUserWarning(msg))
            self.value = str(self.value)

    def serialise(self) -> etree._Element:
        ele = self.make_prop()
        ele.append(self.make_element())
        return ele

    def make_prop(self) -> etree._Element:
        return etree.Element(f"{DASCH_SCHEMA}text-prop", name=self.property, nsmap=XML_NAMESPACE_MAP)

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
class SimpleText(Value):
    value: str
    property: str
    permissions: str | None = "prop-default"
    comment: str | None = None

    def __post_init__(self) -> None:
        if not is_string(self.value):
            msg = f"The following value is not a valid string.\nValue: {self.value} | Property: {self.property}"
            warnings.warn(DspToolsUserWarning(msg))
            self.value = str(self.value)

    def serialise(self) -> etree._Element:
        ele = self.make_prop()
        ele.append(self.make_element())
        return ele

    def make_prop(self) -> etree._Element:
        return etree.Element(f"{DASCH_SCHEMA}text-prop", name=self.property, nsmap=XML_NAMESPACE_MAP)

    def make_element(self) -> etree._Element:
        attribs = {"encoding": "utf8"}
        if self.permissions:
            attribs["permissions"] = self.permissions
        if self.comment:
            attribs["comment"] = self.comment
        ele = etree.Element(f"{DASCH_SCHEMA}text", attrib=attribs, nsmap=XML_NAMESPACE_MAP)
        ele.text = self.value
        return ele
