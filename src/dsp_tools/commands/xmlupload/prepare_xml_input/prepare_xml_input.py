from __future__ import annotations

import warnings
from datetime import datetime
from typing import cast

import regex
from loguru import logger
from lxml import etree

from dsp_tools.clients.connection import Connection
from dsp_tools.commands.xmlupload.models.deserialise.xmlpermission import XmlPermission
from dsp_tools.commands.xmlupload.models.deserialise.xmlresource import XMLResource
from dsp_tools.commands.xmlupload.models.intermediary.res import IntermediaryResource
from dsp_tools.commands.xmlupload.models.lookup_models import IntermediaryLookups
from dsp_tools.commands.xmlupload.models.lookup_models import make_namespace_dict_from_onto_names
from dsp_tools.commands.xmlupload.models.permission import Permissions
from dsp_tools.commands.xmlupload.models.upload_clients import UploadClients
from dsp_tools.commands.xmlupload.prepare_xml_input.iiif_uri_validator import IIIFUriValidator
from dsp_tools.commands.xmlupload.prepare_xml_input.transform_xmlresource_into_intermediary_classes import (
    transform_all_resources_into_intermediary_resources,
)
from dsp_tools.commands.xmlupload.stash.analyse_circular_reference_graph import generate_upload_order
from dsp_tools.commands.xmlupload.stash.create_info_for_graph import create_info_for_graph_from_intermediary_resources
from dsp_tools.commands.xmlupload.stash.stash_circular_references import stash_circular_references
from dsp_tools.commands.xmlupload.stash.stash_models import Stash
from dsp_tools.error.custom_warnings import DspToolsUserWarning
from dsp_tools.error.exceptions import BaseError
from dsp_tools.error.exceptions import InputError
from dsp_tools.legacy_models.projectContext import ProjectContext

LIST_SEPARATOR = "\n-    "


def get_intermediary_lookups(root: etree._Element, con: Connection, clients: UploadClients) -> IntermediaryLookups:
    proj_context = _get_project_context_from_server(connection=con, shortcode=root.attrib["shortcode"])
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


def prepare_upload_from_root(
    root: etree._Element, default_ontology: str, intermediary_lookups: IntermediaryLookups
) -> tuple[list[IntermediaryResource], Stash | None]:
    """Do the consistency check, resolve circular references, and return the resources and permissions."""
    logger.info("Get data from XML...")
    resources = _extract_resources_from_xml(root, default_ontology)
    transformed_resources = _get_transformed_resources(resources, intermediary_lookups)
    info_for_graph = create_info_for_graph_from_intermediary_resources(transformed_resources)
    stash_lookup, upload_order = generate_upload_order(info_for_graph)
    sorting_lookup = {res.res_id: res for res in transformed_resources}
    sorted_resources = [sorting_lookup[res_id] for res_id in upload_order]
    stash = stash_circular_references(sorted_resources, stash_lookup)
    return sorted_resources, stash


def _get_transformed_resources(
    resources: list[XMLResource], intermediary_lookups: IntermediaryLookups
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


def validate_iiif_uris(root: etree._Element) -> None:
    uris = [uri.strip() for node in root.iter(tag="iiif-uri") if (uri := node.text)]
    if problems := IIIFUriValidator(uris).validate():
        msg = problems.get_msg()
        warnings.warn(DspToolsUserWarning(msg))
        logger.warning(msg)


def _extract_resources_from_xml(root: etree._Element, default_ontology: str) -> list[XMLResource]:
    resources = list(root.iter(tag="resource"))
    return [XMLResource.from_node(res, default_ontology) for res in resources]
