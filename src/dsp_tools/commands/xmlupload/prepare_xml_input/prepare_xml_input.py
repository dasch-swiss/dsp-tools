from __future__ import annotations

from datetime import datetime
from typing import cast

import regex
from loguru import logger
from lxml import etree

from dsp_tools.clients.connection import Connection
from dsp_tools.commands.xmlupload.models.deserialise.xmlpermission import XmlPermission
from dsp_tools.commands.xmlupload.models.intermediary.res import IntermediaryResource
from dsp_tools.commands.xmlupload.models.lookup_models import IntermediaryLookups
from dsp_tools.commands.xmlupload.models.lookup_models import make_namespace_dict_from_onto_names
from dsp_tools.commands.xmlupload.models.permission import Permissions
from dsp_tools.commands.xmlupload.models.upload_clients import UploadClients
from dsp_tools.commands.xmlupload.prepare_xml_input.transform_into_intermediary_classes import (
    transform_all_resources_into_intermediary_resources,
)
from dsp_tools.commands.xmlupload.stash.analyse_circular_reference_graph import generate_upload_order
from dsp_tools.commands.xmlupload.stash.create_info_for_graph import create_info_for_graph_from_intermediary_resources
from dsp_tools.commands.xmlupload.stash.stash_circular_references import stash_circular_references
from dsp_tools.commands.xmlupload.stash.stash_models import Stash
from dsp_tools.error.exceptions import BaseError
from dsp_tools.error.exceptions import InputError
from dsp_tools.legacy_models.projectContext import ProjectContext
from dsp_tools.utils.xml_parsing.get_parsed_resources import get_parsed_resources
from dsp_tools.utils.xml_parsing.models.parsed_resource import ParsedResource

LIST_SEPARATOR = "\n-    "


def get_intermediary_lookups(root: etree._Element, clients: UploadClients) -> IntermediaryLookups:
    proj_context = _get_project_context_from_server(
        connection=clients.project_client.con, shortcode=root.attrib["shortcode"]
    )
    permissions_lookup = _get_permissions_lookup(root, proj_context)
    authorship_lookup = _get_authorship_lookup(root)
    listnode_lookup = clients.list_client.get_list_node_id_to_iri_lookup()
    project_onto_dict = clients.project_client.get_ontology_name_dict()
    namespaces = make_namespace_dict_from_onto_names(project_onto_dict)
    return IntermediaryLookups(
        permissions=permissions_lookup,
        listnodes=listnode_lookup,
        namespaces=namespaces,
        authorships=authorship_lookup,
    )


def _get_permissions_lookup(root: etree._Element, proj_context: ProjectContext) -> dict[str, Permissions]:
    permission_ele = list(root.iter(tag="permissions"))
    permissions = [XmlPermission(permission, proj_context) for permission in permission_ele]
    permissions_dict = {permission.permission_id: permission for permission in permissions}
    permissions_lookup = {name: perm.get_permission_instance() for name, perm in permissions_dict.items()}
    return permissions_lookup


def _get_project_context_from_server(connection: Connection, shortcode: str) -> ProjectContext:
    try:
        proj_context = ProjectContext(con=connection, shortcode=shortcode)
    except BaseError:
        logger.exception("Unable to retrieve project context from DSP server")
        raise InputError("Unable to retrieve project context from DSP server") from None
    return proj_context


def _get_authorship_lookup(root: etree._Element) -> dict[str, list[str]]:
    def get_one_author(ele: etree._Element) -> str:
        # The xsd file ensures that the body of the element contains valid non-whitespace characters
        txt = cast(str, ele.text)
        txt = regex.sub(r"[\n\t]", " ", txt)
        txt = regex.sub(r" +", " ", txt)
        return txt.strip()

    authorship_lookup = {}
    for auth in root.iter(tag="authorship"):
        individual_authors = [get_one_author(child) for child in auth.iterchildren()]
        authorship_lookup[auth.attrib["id"]] = individual_authors
    return authorship_lookup


def get_resources_and_stash_for_upload(
    root: etree._Element, clients: UploadClients
) -> tuple[list[IntermediaryResource], Stash | None]:
    logger.info("Get data from XML...")
    parsed_resources, _ = get_parsed_resources(root, clients.legal_info_client.server)
    intermediary_lookups = get_intermediary_lookups(root=root, clients=clients)
    intermediary_resources = _get_intermediary_resources(parsed_resources, intermediary_lookups)
    return _get_stash_and_upload_order(intermediary_resources)


def _get_intermediary_resources(
    resources: list[ParsedResource], intermediary_lookups: IntermediaryLookups
) -> list[IntermediaryResource]:
    result = transform_all_resources_into_intermediary_resources(resources, intermediary_lookups)
    if result.resource_failures:
        failures = [f"Resource ID: '{x.resource_id}', Message: {x.failure_msg}" for x in result.resource_failures]
        msg = (
            f"{datetime.now()}: WARNING: Unable to create the following resource(s):"
            f"{LIST_SEPARATOR}{LIST_SEPARATOR.join(failures)}"
        )
        raise InputError(msg)
    return result.transformed_resources


def _get_stash_and_upload_order(
    resources: list[IntermediaryResource],
) -> tuple[list[IntermediaryResource], Stash | None]:
    info_for_graph = create_info_for_graph_from_intermediary_resources(resources)
    stash_lookup, upload_order = generate_upload_order(info_for_graph)
    sorting_lookup = {res.res_id: res for res in resources}
    sorted_resources = [sorting_lookup[res_id] for res_id in upload_order]
    stash = stash_circular_references(sorted_resources, stash_lookup)
    return sorted_resources, stash
