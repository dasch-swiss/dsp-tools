from __future__ import annotations

import warnings
from dataclasses import dataclass
from dataclasses import field
from pathlib import Path

from lxml import etree

from dsp_tools.models.custom_warnings import DspToolsUserWarning
from dsp_tools.models.exceptions import BaseError
from dsp_tools.utils.xml_validation import validate_xml_file
from dsp_tools.xmllib.models.permissions import XMLPermissions
from dsp_tools.xmllib.models.resource import Resource

XML_NAMESPACE_MAP = {None: "https://dasch.swiss/schema", "xsi": "http://www.w3.org/2001/XMLSchema-instance"}
DASCH_SCHEMA = "{https://dasch.swiss/schema}"


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
            f"{DASCH_SCHEMA}knora",
            attrib={
                schema_location_key: schema_location_value,
                "shortcode": self.shortcode,
                "default-ontology": self.default_ontology,
            },
            nsmap=XML_NAMESPACE_MAP,
        )

    def add_resource(self, resource: Resource) -> XMLRoot:
        self.resources.append(resource)
        return self

    def add_resources(self, resources: list[Resource]) -> XMLRoot:
        self.resources.extend(resources)
        return self

    def add_resource_optional(self, resource: Resource | None) -> XMLRoot:
        if resource:
            self.resources.append(resource)
        return self

    def serialise(self) -> etree._Element:
        root = self.make_root()
        permissions = XMLPermissions().serialise()
        root.extend(permissions)
        serialised_resources = [x.serialise() for x in self.resources]
        root.extend(serialised_resources)
        return root

    def write_file(self, filepath: str | Path) -> None:
        """
        Write the finished XML to a file.

        Args:
            filepath: where to save the file

        Warning:
            if the XML is not valid, according to the schema
        """
        root = self.serialise()
        etree.indent(root, space="    ")
        xml_string = etree.tostring(
            root,
            encoding="unicode",
            pretty_print=True,
            doctype='<?xml version="1.0" encoding="UTF-8"?>',
        )
        xml_string = xml_string.replace(r"\'", "'")
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(xml_string)
        try:
            validate_xml_file(input_file=filepath)
            print(f"The XML file was successfully saved to {filepath}")
        except BaseError as err:
            msg = (
                f"The XML file was successfully saved to {filepath}, "
                f"but the following Schema validation error(s) occurred: {err.message}"
            )
            warnings.warn(DspToolsUserWarning(msg))
