from __future__ import annotations

from collections.abc import Collection
from dataclasses import dataclass
from dataclasses import field
from pathlib import Path
from typing import Union
from uuid import uuid4

from loguru import logger
from lxml import etree

from dsp_tools.error.exceptions import BaseError
from dsp_tools.error.xmllib_warnings import MessageInfo
from dsp_tools.error.xmllib_warnings_util import emit_xmllib_input_warning
from dsp_tools.utils.xml_parsing.parse_clean_validate_xml import parse_and_validate_xml_file
from dsp_tools.xmllib.internal.constants import DASCH_SCHEMA
from dsp_tools.xmllib.internal.constants import XML_NAMESPACE_MAP
from dsp_tools.xmllib.internal.serialise_resource import serialise_resources
from dsp_tools.xmllib.models.dsp_base_resources import AudioSegmentResource
from dsp_tools.xmllib.models.dsp_base_resources import LinkResource
from dsp_tools.xmllib.models.dsp_base_resources import RegionResource
from dsp_tools.xmllib.models.dsp_base_resources import VideoSegmentResource
from dsp_tools.xmllib.models.internal.file_values import AuthorshipLookup
from dsp_tools.xmllib.models.internal.serialise_permissions import XMLPermissions
from dsp_tools.xmllib.models.res import Resource

type AnyResource = Union[Resource, RegionResource, LinkResource, VideoSegmentResource, AudioSegmentResource]


# ruff: noqa: D101


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

        Examples:
            ```python
            root = xmllib.XMLRoot.create_new(
                shortcode="0000",
                default_ontology="onto"
            )
            ```
        """
        return XMLRoot(shortcode=shortcode, default_ontology=default_ontology)

    def add_resource(self, resource: AnyResource) -> XMLRoot:
        """
        Add one resource to the root.

        Args:
            resource: any one of:
                    `Resource`,
                    `RegionResource`,
                    `LinkResource`,
                    `VideoSegmentResource`,
                    `AudioSegmentResource`

        Returns:
            The original XMLRoot, with the added resource

        Examples:
            ```python
            resource = xmllib.Resource.create_new(
                res_id="ID", restype=":ResourceType", label="label"
            )

            root = root.add_resource(resource)
            ```
        """
        self.resources.append(resource)
        return self

    def add_resource_multiple(self, resources: Collection[AnyResource]) -> XMLRoot:
        """
        Add a list of resources to the root.

        Args:
            resources: a list of:
                    `Resource`,
                    `RegionResource`,
                    `LinkResource`,
                    `VideoSegmentResource`,
                    `AudioSegmentResource`
                    The types of the resources may be mixed.

        Returns:
            The original XMLRoot, with the added resource

        Examples:
            ```python
            resource_1 = xmllib.Resource.create_new(
                res_id="ID_1", restype=":ResourceType", label="label 1"
            )
            resource_2 = xmllib.Resource.create_new(
                res_id="ID_2", restype=":ResourceType", label="label 2"
            )

            root = root.add_resource_multiple([resource_1, resource_2])
            ```
        """
        self.resources.extend(resources)
        return self

    def add_resource_optional(self, resource: AnyResource | None) -> XMLRoot:
        """
        If the resource is not None, add it to the XMLRoot, otherwise return the XMLRoot unchanged.

        Args:
            resource: any one of:
                    `Resource`,
                    `RegionResource`,
                    `LinkResource`,
                    `VideoSegmentResource`,
                    `AudioSegmentResource`

        Returns:
            The original XMLRoot, with the added value if it was not empty. Else the unchanged original XMLRoot.

        Examples:
            ```python
            resource = xmllib.Resource.create_new(
                res_id="ID", restype=":ResourceType", label="label"
            )

            root = root.add_resource_optional(resource)
            ```

            ```python
            root = root.add_resource_optional(None)
            ```
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

        Examples:
            ```python
            root.write_file("xml_file_name.xml")
            ```
        """
        root = self.serialise()
        etree.indent(root, space="    ")
        xml_string = etree.tostring(
            root,
            encoding="unicode",
            pretty_print=True,
            doctype='<?xml version="1.0" encoding="UTF-8"?>',
        )
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(xml_string)
        try:
            logger.disable("dsp_tools")
            parse_and_validate_xml_file(input_file=filepath)
            print(f"The XML file was successfully saved to {filepath}")
        except BaseError as err:
            msg = (
                f"The XML file was successfully saved to {filepath}, "
                f"but the following Schema validation error(s) occurred: {err.message}"
            )
            emit_xmllib_input_warning(MessageInfo(msg))

    def serialise(self) -> etree._Element:
        """
        Create an `lxml.etree._Element` with the information in the root.
        If you wish to create a file, we recommend using the `write_file` method instead.

        Returns:
            The `XMLRoot` serialised as XML
        """
        root = self._make_root()
        permissions = XMLPermissions().serialise()
        root.extend(permissions)
        author_lookup = _make_authorship_lookup(self.resources)
        authorship = _serialise_authorship(author_lookup.lookup)
        root.extend(authorship)
        serialised_resources = serialise_resources(self.resources, author_lookup)
        root.extend(serialised_resources)
        return root

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


def _make_authorship_lookup(resources: list[AnyResource]) -> AuthorshipLookup:
    filtered_resources = [x for x in resources if isinstance(x, Resource)]
    file_vals = [x.file_value for x in filtered_resources if x.file_value]
    authors = {x.metadata.authorship for x in file_vals}
    lookup = {}
    for auth in authors:
        lookup[auth] = f"authorship_{uuid4()!s}"
    return AuthorshipLookup(lookup)


def _serialise_authorship(authorship_lookup: dict[tuple[str, ...], str]) -> list[etree._Element]:
    return [_make_one_authorship_element(auth, id_) for auth, id_ in authorship_lookup.items()]


def _make_one_authorship_element(authors: tuple[str, ...], author_id: str) -> etree._Element:
    def _make_one_author(author: str) -> etree._Element:
        ele = etree.Element(f"{DASCH_SCHEMA}author", nsmap=XML_NAMESPACE_MAP)
        ele.text = author
        return ele

    authorship_ele = etree.Element(f"{DASCH_SCHEMA}authorship", attrib={"id": author_id}, nsmap=XML_NAMESPACE_MAP)
    all_authors = [_make_one_author(x) for x in authors]
    authorship_ele.extend(all_authors)
    return authorship_ele
