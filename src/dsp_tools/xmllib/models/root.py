from __future__ import annotations

import warnings
from collections.abc import Collection
from dataclasses import dataclass
from dataclasses import field
from pathlib import Path
from typing import TypeAlias
from typing import Union

from lxml import etree

from dsp_tools.models.custom_warnings import DspToolsUserWarning
from dsp_tools.models.exceptions import BaseError
from dsp_tools.utils.xml_validation import validate_xml_file
from dsp_tools.xmllib.models.dsp_base_resources import AnnotationResource
from dsp_tools.xmllib.models.dsp_base_resources import AudioSegmentResource
from dsp_tools.xmllib.models.dsp_base_resources import LinkResource
from dsp_tools.xmllib.models.dsp_base_resources import RegionResource
from dsp_tools.xmllib.models.dsp_base_resources import VideoSegmentResource
from dsp_tools.xmllib.models.permissions import XMLPermissions
from dsp_tools.xmllib.models.resource import Resource

# ruff: noqa: D101

XML_NAMESPACE_MAP = {None: "https://dasch.swiss/schema", "xsi": "http://www.w3.org/2001/XMLSchema-instance"}
DASCH_SCHEMA = "{https://dasch.swiss/schema}"

AnyResource: TypeAlias = Union[
    Resource, AnnotationResource, RegionResource, LinkResource, VideoSegmentResource, AudioSegmentResource
]


@dataclass
class XMLRoot:
    shortcode: str
    default_ontology: str
    resources: list[AnyResource] = field(default_factory=list)

    @staticmethod
    def create_new(shortcode: str, default_ontology: str) -> XMLRoot:
        """
        Create a new XML root, for one file.

        Args:
            shortcode: project shortcode
            default_ontology: name of the default ontology

        Returns:
            Instance of `XMLRoot`
        """
        return XMLRoot(shortcode=shortcode, default_ontology=default_ontology)

    def add_resource(self, resource: AnyResource) -> XMLRoot:
        """
        Add one resource to the root.

        Args:
            resource: any one of:
                    `Resource`,
                    `AnnotationResource`,
                    `RegionResource`,
                    `LinkResource`,
                    `VideoSegmentResource`,
                    `AudioSegmentResource`

        Returns:
            The original XMLRoot, with the added resource
        """
        self.resources.append(resource)
        return self

    def add_resource_multiple(self, resources: Collection[AnyResource]) -> XMLRoot:
        """
        Add a list of resources to the root.

        Args:
            resources: a list of:
                    `Resource`,
                    `AnnotationResource`,
                    `RegionResource`,
                    `LinkResource`,
                    `VideoSegmentResource`,
                    `AudioSegmentResource`
                    The types of the resources may be mixed.

        Returns:
            The original XMLRoot, with the added resource
        """
        self.resources.extend(resources)
        return self

    def add_resource_optional(self, resource: AnyResource | None) -> XMLRoot:
        """
        If the resource is not None, add it to the XMLRoot, otherwise return the XMLRoot unchanged.

        Args:
            resource: any one of:
                    `Resource`,
                    `AnnotationResource`,
                    `RegionResource`,
                    `LinkResource`,
                    `VideoSegmentResource`,
                    `AudioSegmentResource`

        Returns:
            The original XMLRoot, with the added value if it was not empty. Else the unchanged original XMLRoot.
        """
        if resource:
            self.resources.append(resource)
        return self

    def write_file(self, filepath: str | Path) -> None:
        """
        Write the finished XML to a file.

        Args:
            filepath: where to save the file

        Warning:
            if the XML is not valid according to the schema
        """
        root = self._serialise()
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

    def _make_root(self) -> etree._Element:
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

    def _serialise(self) -> etree._Element:
        root = self._make_root()
        permissions = XMLPermissions().serialise()
        root.extend(permissions)
        serialised_resources = [x.serialise() for x in self.resources]
        root.extend(serialised_resources)
        return root
