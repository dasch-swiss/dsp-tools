from __future__ import annotations

import warnings
from collections import defaultdict
from dataclasses import dataclass
from dataclasses import field
from pathlib import Path
from typing import Any

from lxml import etree

from dsp_tools.commands.excel2xml.excel2xml_lib import append_permissions
from dsp_tools.commands.excel2xml.excel2xml_lib import write_xml
from dsp_tools.commands.excel2xml.xml_models_utils import is_string
from dsp_tools.models.custom_warnings import DspToolsUserWarning
from dsp_tools.models.exceptions import InputError
from dsp_tools.utils.uri_util import is_iiif_uri

xml_namespace_map = {None: "https://dasch.swiss/schema", "xsi": "http://www.w3.org/2001/XMLSchema-instance"}


@dataclass
class XMLRoot:
    shortcode: str
    default_ontology: str
    resources: list[Resource] = field(default_factory=list)

    def make_root(self) -> etree._Element:
        schema_url = (
            "https://raw.githubusercontent.com/dasch-swiss/dsp-tools/main/src/dsp_tools/resources/schema/data.xsd"
        )
        schema_location_key = str(etree.QName("http://www.w3.org/2001/XMLSchema-instance", "schemaLocation"))
        schema_location_value = f"https://dasch.swiss/schema {schema_url}"
        return etree.Element(
            f"{{{xml_namespace_map[None]}}}knora",
            attrib={
                schema_location_key: schema_location_value,
                "shortcode": self.shortcode,
                "default-ontology": self.default_ontology,
            },
            nsmap=xml_namespace_map,
        )

    def serialise(self) -> etree._Element:
        root = self.make_root()
        root = append_permissions(root)
        serialised_resources = [x.serialise() for x in self.resources]
        root.extend(serialised_resources)
        return root

    def write_file(self, filepath: str | Path) -> None:
        root = self.serialise()
        write_xml(root, filepath)


@dataclass
class Resource:
    res_id: str
    restype: str
    label: str
    permissions: str = "res-default"
    values: list[Value] = field(default_factory=list)
    iiif_uri: str | None = None
    filepath: str | None = None

    def __post_init__(self) -> None:
        if not is_string(str(self.label)):
            msg = (
                f"The label of a resource should be a string.\n"
                f"The label '{self.label}' of the resource with the ID {self.res_id} is not a string."
            )
            warnings.warn(DspToolsUserWarning(msg))

    def serialise(self) -> etree._Element:
        res_ele = self._make_resource_ele()
        if (file_ele := self._make_file_ele()) is not None:
            res_ele.append(file_ele)
        res_ele.extend(self._serialise_values())
        return res_ele

    def _make_resource_ele(self) -> etree._Element:
        attribs = {"label": self.label, "restype": self.restype, "id": self.res_id}
        if self.permissions:
            attribs["permissions"] = self.permissions
        return etree.Element(f"{{{xml_namespace_map[None]}}}resource", attrib=attribs, nsmap=xml_namespace_map)

    def _make_file_ele(self) -> etree._Element | None:
        if self.iiif_uri and self.filepath:
            raise InputError(
                "A resource can only have a iiif-uri or a filepath.\n"
                f"The resource with the ID '{self.res_id}' has both."
            )
        if self.filepath:
            prop_ = etree.Element(
                f"{{{xml_namespace_map[None]}}}bitstream",
                permissions=self.permissions,
                nsmap=xml_namespace_map,
            )
            prop_.text = str(self.filepath)
            return prop_
        if self.iiif_uri:
            if not is_iiif_uri(self.iiif_uri):
                msg = (
                    f"Failed validation in iiif-uri tag of resource '{self.res_id}': "
                    f"The URI: '{self.iiif_uri}' does not conform to the specifications."
                )
                warnings.warn(DspToolsUserWarning(msg))
            prop_ = etree.Element(
                f"{{{xml_namespace_map[None]}}}iiif-uri",
                permissions=self.permissions,
                nsmap=xml_namespace_map,
            )
            prop_.text = self.iiif_uri
            return prop_
        return None

    def _serialise_values(self) -> list[etree._Element]:
        grouped = defaultdict(list)
        for val in self.values:
            grouped[val.property].append(val)
        return [self._combine_values(prop_values) for prop_values in grouped.values()]

    def _combine_values(self, prop_values: list[Value]) -> etree._Element:
        prop_ = prop_values[0].make_prop()
        prop_eles = [x.make_element() for x in prop_values]
        prop_.extend(prop_eles)
        return prop_


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
class RichText(Value):
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
        return etree.Element(f"{{{xml_namespace_map[None]}}}text-prop", name=self.property, nsmap=xml_namespace_map)

    def make_element(self) -> etree._Element:
        attribs = {"encoding": "xml"}
        if self.permissions:
            attribs["permissions"] = self.permissions
        if self.comment:
            attribs["comment"] = self.comment
        ele = etree.Element(f"{{{xml_namespace_map[None]}}}text", attrib=attribs, nsmap=xml_namespace_map)
        ele.text = self.value
        return ele


@dataclass
class TextArea(Value):
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
        return etree.Element(f"{{{xml_namespace_map[None]}}}text-prop", name=self.property, nsmap=xml_namespace_map)

    def make_element(self) -> etree._Element:
        attribs = {"encoding": "utf8"}
        if self.permissions:
            attribs["permissions"] = self.permissions
        if self.comment:
            attribs["comment"] = self.comment
        ele = etree.Element(f"{{{xml_namespace_map[None]}}}text", attrib=attribs, nsmap=xml_namespace_map)
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
        return etree.Element(f"{{{xml_namespace_map[None]}}}text-prop", name=self.property, nsmap=xml_namespace_map)

    def make_element(self) -> etree._Element:
        attribs = {"encoding": "utf8"}
        if self.permissions:
            attribs["permissions"] = self.permissions
        if self.comment:
            attribs["comment"] = self.comment
        ele = etree.Element(f"{{{xml_namespace_map[None]}}}text", attrib=attribs, nsmap=xml_namespace_map)
        ele.text = self.value
        return ele
