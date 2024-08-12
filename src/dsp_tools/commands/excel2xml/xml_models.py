from __future__ import annotations

import warnings
from dataclasses import dataclass
from typing import Any

from lxml import etree

from dsp_tools.commands.excel2xml.xml_models_validation import is_string
from dsp_tools.models.custom_warnings import DspToolsUserWarning

xml_namespace_map = {None: "https://dasch.swiss/schema", "xsi": "http://www.w3.org/2001/XMLSchema-instance"}


@dataclass
class AllValues:
    values: list[Value]


@dataclass
class Value:
    value: Any
    property: str
    comment: str
    permissions: str

    def serialise(self) -> etree._Element:
        raise NotImplementedError

    def make_prop(self) -> etree._Element:
        raise NotImplementedError

    def make_element(self) -> etree._Element:
        raise NotImplementedError


@dataclass
class RichText(Value):
    value: str
    property: str
    comment: str
    permissions: str = "prop-default"
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
        return ele.append(self.make_element())

    def make_prop(self) -> etree._Element:
        return etree.Element(f"{{{xml_namespace_map[None]}}}text-prop", name=self.property, nsmap=xml_namespace_map)

    def make_element(self) -> etree._Element:
        attribs = {"encoding": "xml"}
        if self.permissions:
            attribs["permissions"] = self.permissions
        if self.comment:
            attribs["comment"] = self.comment
        return etree.Element(f"{{{xml_namespace_map[None]}}}text", attrib=attribs, nsmap=xml_namespace_map)


@dataclass
class TextArea(Value):
    value: str
    property: str
    comment: str
    permissions: str = "prop-default"
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
        return ele.append(self.make_element())

    def make_prop(self) -> etree._Element:
        return etree.Element(f"{{{xml_namespace_map[None]}}}text-prop", name=self.property, nsmap=xml_namespace_map)

    def make_element(self) -> etree._Element:
        attribs = {"encoding": "utf8"}
        if self.permissions:
            attribs["permissions"] = self.permissions
        if self.comment:
            attribs["comment"] = self.comment
        return etree.Element(f"{{{xml_namespace_map[None]}}}text", attrib=attribs, nsmap=xml_namespace_map)


@dataclass
class SimpleText(Value):
    value: str
    property: str
    comment: str
    permissions: str = "prop-default"

    def __post_init__(self) -> None:
        if not is_string(self.value):
            msg = f"The following value is not a valid string.\nValue: {self.value} | Property: {self.property}"
            warnings.warn(DspToolsUserWarning(msg))
            self.value = str(self.value)

    def serialise(self) -> etree._Element:
        ele = self.make_prop()
        return ele.append(self.make_element())

    def make_prop(self) -> etree._Element:
        return etree.Element(f"{{{xml_namespace_map[None]}}}text-prop", name=self.property, nsmap=xml_namespace_map)

    def make_element(self) -> etree._Element:
        attribs = {"encoding": "utf8"}
        if self.permissions:
            attribs["permissions"] = self.permissions
        if self.comment:
            attribs["comment"] = self.comment
        return etree.Element(f"{{{xml_namespace_map[None]}}}text", attrib=attribs, nsmap=xml_namespace_map)
