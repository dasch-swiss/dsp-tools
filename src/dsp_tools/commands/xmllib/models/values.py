from __future__ import annotations

import warnings
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from typing import Protocol

import regex
from lxml import etree

from dsp_tools.commands.xmllib.utils import is_string
from dsp_tools.models.custom_warnings import DspToolsUserWarning

XML_NAMESPACE_MAP = {None: "https://dasch.swiss/schema", "xsi": "http://www.w3.org/2001/XMLSchema-instance"}
DASCH_SCHEMA = "{https://dasch.swiss/schema}"


@dataclass
class Value(Protocol):
    value: Any
    prop_name: str
    permissions: str | None
    comment: str | None

    def serialise(self) -> etree._Element:
        raise NotImplementedError

    def make_prop(self) -> etree._Element:
        raise NotImplementedError

    def make_element(self) -> etree._Element:
        raise NotImplementedError


@dataclass
class SimpleText(Value):
    value: str
    prop_name: str
    permissions: str | None = "prop-default"
    comment: str | None = None

    def __post_init__(self) -> None:
        if not is_string(self.value):
            msg = f"The following value is not a valid string.\nValue: {self.value} | Property: {self.prop_name}"
            warnings.warn(DspToolsUserWarning(msg))
            self.value = str(self.value)

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
class LinkValue(Value):
    value: str
    prop_name: str
    permissions: str | None = "prop-default"
    comment: str | None = None

    def __post_init__(self) -> None:
        if not is_string(self.value):
            msg = f"The following value is not a valid string.\nValue: {self.value} | Property: {self.prop_name}"
            warnings.warn(DspToolsUserWarning(msg))
            self.value = str(self.value)

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
class IntValue(Value):
    value: int | str
    prop_name: str
    permissions: str | None = "prop-default"
    comment: str | None = None

    def __post_init__(self) -> None:
        msg = (
            f"The following value is not a valid integer.\n"
            f"Type: {type(self.value)} | Value: {self.value} | Property: {self.prop_name}"
        )
        if isinstance(self.value, str):
            if not regex.search(r"^\d+$", self.value):
                warnings.warn(DspToolsUserWarning(msg))
        elif not isinstance(self.value, int):
            warnings.warn(DspToolsUserWarning(msg))

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
class AbstractFileValue(Protocol):
    value: str | Path
    permissions: str | None
    comment: str | None = None

    def serialise(self) -> etree._Element:
        raise NotImplementedError


@dataclass
class FileValue(AbstractFileValue):
    value: str | Path
    permissions: str | None = "prop-default"
    comment: str | None = None

    def serialise(self) -> etree._Element:
        attribs = {}
        if self.permissions:
            attribs["permissions"] = self.permissions
        if self.comment:
            attribs["comment"] = self.comment
        ele = etree.Element(f"{DASCH_SCHEMA}bitstream", attrib=attribs, nsmap=XML_NAMESPACE_MAP)
        ele.text = str(self.value)
        return ele


@dataclass
class IIIFUri(AbstractFileValue):
    value: str | Path
    permissions: str | None = "prop-default"
    comment: str | None = None

    def serialise(self) -> etree._Element:
        attribs = {}
        if self.permissions:
            attribs["permissions"] = self.permissions
        if self.comment:
            attribs["comment"] = self.comment
        ele = etree.Element(f"{DASCH_SCHEMA}iiif-uri", attrib=attribs, nsmap=XML_NAMESPACE_MAP)
        ele.text = str(self.value)
        return ele
