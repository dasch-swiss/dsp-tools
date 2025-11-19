from __future__ import annotations

import os
import warnings
from collections.abc import Collection
from dataclasses import dataclass
from dataclasses import field
from pathlib import Path
from typing import Union
from uuid import uuid4

import pandas as pd
from dotenv import load_dotenv
from loguru import logger
from lxml import etree

from dsp_tools.error.custom_warnings import DspToolsFutureWarning
from dsp_tools.error.xmllib_warnings import MessageInfo
from dsp_tools.error.xmllib_warnings_util import emit_xmllib_input_warning
from dsp_tools.utils.ansi_colors import BOLD_GREEN
from dsp_tools.utils.ansi_colors import BOLD_RED
from dsp_tools.utils.ansi_colors import RESET_TO_DEFAULT
from dsp_tools.utils.xml_parsing.parse_clean_validate_xml import validate_root_emit_user_message
from dsp_tools.xmllib.internal.constants import DASCH_SCHEMA
from dsp_tools.xmllib.internal.constants import XML_NAMESPACE_MAP
from dsp_tools.xmllib.internal.serialise_resource import serialise_resources
from dsp_tools.xmllib.models.dsp_base_resources import AudioSegmentResource
from dsp_tools.xmllib.models.dsp_base_resources import LinkResource
from dsp_tools.xmllib.models.dsp_base_resources import RegionResource
from dsp_tools.xmllib.models.dsp_base_resources import VideoSegmentResource
from dsp_tools.xmllib.models.internal.file_values import AuthorshipLookup
from dsp_tools.xmllib.models.internal.serialise_permissions import XMLPermissions
from dsp_tools.xmllib.models.permissions import Permissions
from dsp_tools.xmllib.models.res import Resource

type AnyResource = Union[Resource, RegionResource, LinkResource, VideoSegmentResource, AudioSegmentResource]

load_dotenv()


@dataclass
class XMLRoot:
    shortcode: str
    default_ontology: str
    resources: list[AnyResource] = field(default_factory=list)
    _res_id_to_type_lookup: dict[str, list[str]] = field(default_factory=dict)

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

        Warning:
            If the ID of the new resource is already used.

        Examples:
            ```python
            resource = xmllib.Resource.create_new(
                res_id="ID", restype=":ResourceType", label="label"
            )

            root = root.add_resource(resource)
            ```
        """
        if isinstance(resource, Resource):
            res_type = resource.restype
        else:
            res_type = resource.__class__.__name__
        if types_used := self._res_id_to_type_lookup.get(resource.res_id):
            existing_types = [f"'{x}'" for x in types_used]
            msg = (
                f"The ID for this resource of type '{res_type}' "
                f"is already used by resource(s) of the following type(s): {', '.join(existing_types)}."
            )
            info_msg = MessageInfo(
                message=msg,
                resource_id=resource.res_id,
                field="Resource ID",
            )
            emit_xmllib_input_warning(info_msg)
            self._res_id_to_type_lookup[resource.res_id].append(res_type)
        else:
            self._res_id_to_type_lookup[resource.res_id] = [res_type]
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

        Warning:
            If the ID of the new resource is already used.

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
        for res in resources:
            self.add_resource(res)
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

        Warning:
            If the ID of the new resource is already used.

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
            self.add_resource(resource)
        return self

    def write_file(self, filepath: str | Path, default_permissions: Permissions | None = None) -> None:
        """
        Write the finished XML to a file.

        Args:
            filepath: where to save the file
            default_permissions: This parameter is deprecated and has no effect.
                Default permissions can be set in the JSON project file.

        Warning:
            if the XML is not valid according to the schema

        Examples:
            ```python
            root.write_file("xml_file_name.xml")
            ```
        """

        if default_permissions:
            msg = (
                "You added a default permission. This has no effect. This functionality is deprecated, "
                "because project wide default permissions are set in the JSON project file. "
                "This parameter will be removed soon."
            )
            warnings.warn(DspToolsFutureWarning(msg))

        root = self.serialise()

        # The logging is only configured when using the CLI entry point.
        # If this is not disabled, then the statements will also be printed out on the terminal.
        logger.disable("dsp_tools")
        validate_root_emit_user_message(root, Path(filepath).parent)

        etree.indent(root, space="    ")
        xml_string = etree.tostring(
            root,
            encoding="unicode",
            pretty_print=True,
            doctype='<?xml version="1.0" encoding="UTF-8"?>',
        )
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(xml_string)
            print(f"The XML file was successfully saved to {filepath}.")
        if file_path := os.getenv("XMLLIB_WARNINGS_CSV_SAVEPATH"):
            df = pd.read_csv(file_path)
            if len(df) > 0:
                msg = f"{len(df)} warnings occurred, please consult '{file_path}' for details."
                print(BOLD_RED, msg, RESET_TO_DEFAULT)
            else:
                msg = "No warnings occurred during the runtime."
                print(BOLD_GREEN, msg, RESET_TO_DEFAULT)

    def serialise(self) -> etree._Element:
        """
        Create an `lxml.etree._Element` with the information in the root.
        If you wish to create a file, we recommend using the `write_file` method instead.

        Returns:
            The `XMLRoot` serialised as XML
        """
        root = self._make_root()
        root.extend(self._get_permissions())
        author_lookup = _make_authorship_lookup(self.resources)
        authorship = _serialise_authorship(author_lookup.lookup)
        root.extend(authorship)
        serialised_resources = serialise_resources(self.resources, author_lookup)
        root.extend(serialised_resources)
        return root

    def _get_permissions(self) -> list[etree._Element]:
        contains_old_permissions, contains_new_permissions = self._find_permission_types()
        if contains_old_permissions:
            msg = (
                "Your data contains old permissions. Please migrate to the new ones:\n"
                " - Permissions.OPEN            -> use Permissions.PUBLIC instead\n"
                " - Permissions.RESTRICTED      -> use Permissions.PRIVATE instead\n"
                " - Permissions.RESTRICTED_VIEW -> use Permissions.LIMITED_VIEW instead\n"
            )
            warnings.warn(msg, category=DspToolsFutureWarning)
        return XMLPermissions().serialise(contains_old_permissions, contains_new_permissions)

    def _find_permission_types(self) -> tuple[bool, bool]:
        contains_old_permissions = False
        contains_new_permissions = False
        for res in self.resources:
            if self._is_old(res.permissions):
                contains_old_permissions = True
            elif self._is_new(res.permissions):
                contains_new_permissions = True
            for val in res.values:
                if self._is_old(val.permissions):
                    contains_old_permissions = True
                elif self._is_new(val.permissions):
                    contains_new_permissions = True
            if isinstance(res, Resource):
                if res.file_value:
                    if self._is_old(res.file_value.metadata.permissions):
                        contains_old_permissions = True
                    elif self._is_new(res.file_value.metadata.permissions):
                        contains_new_permissions = True
            if contains_old_permissions and contains_new_permissions:
                # no need to continue, the end result won't change any more
                return True, True
        return contains_old_permissions, contains_new_permissions

    def _is_old(self, perm: Permissions) -> bool:
        return perm in [Permissions.OPEN, Permissions.RESTRICTED_VIEW, Permissions.RESTRICTED]

    def _is_new(self, perm: Permissions) -> bool:
        return perm in [Permissions.PUBLIC, Permissions.LIMITED_VIEW, Permissions.PRIVATE]

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
    authors = {x.metadata.authorship for x in file_vals if x.metadata.authorship}
    sorted_authors = sorted(authors)
    env_var = str(os.getenv("XMLLIB_AUTHORSHIP_ID_WITH_INTEGERS")).lower()
    if env_var == "true":
        auth_nums: list[int | str] = list(range(1, len(sorted_authors) + 1))
    else:
        auth_nums = [str(uuid4()) for _ in range(len(sorted_authors))]
    auth_ids = [f"authorship_{x}" for x in auth_nums]
    lookup = dict(zip(sorted_authors, auth_ids))
    return AuthorshipLookup(lookup)


def _serialise_authorship(authorship_lookup: dict[tuple[str, ...], str]) -> list[etree._Element]:
    to_serialise = [(auth, id_) for auth, id_ in authorship_lookup.items()]
    to_serialise = sorted(to_serialise, key=lambda x: x[0])
    return [_make_one_authorship_element(auth, id_) for auth, id_ in to_serialise]


def _make_one_authorship_element(authors: tuple[str, ...], author_id: str) -> etree._Element:
    def _make_one_author(author: str) -> etree._Element:
        ele = etree.Element(f"{DASCH_SCHEMA}author", nsmap=XML_NAMESPACE_MAP)
        ele.text = author
        return ele

    authorship_ele = etree.Element(f"{DASCH_SCHEMA}authorship", attrib={"id": author_id}, nsmap=XML_NAMESPACE_MAP)
    all_authors = [_make_one_author(x) for x in authors]
    authorship_ele.extend(all_authors)
    return authorship_ele
