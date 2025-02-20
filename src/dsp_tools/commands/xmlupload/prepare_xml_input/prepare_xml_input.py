from __future__ import annotations

import warnings
from datetime import datetime

from loguru import logger
from lxml import etree

from dsp_tools.commands.xmlupload.models.deserialise.xmlpermission import XmlPermission
from dsp_tools.commands.xmlupload.models.deserialise.xmlresource import XMLResource
from dsp_tools.commands.xmlupload.models.lookup_models import IntermediaryLookups
from dsp_tools.commands.xmlupload.models.lookup_models import get_json_ld_context_for_project
from dsp_tools.commands.xmlupload.models.lookup_models import make_namespace_dict_from_onto_names
from dsp_tools.commands.xmlupload.models.permission import Permissions
from dsp_tools.commands.xmlupload.models.upload_clients import UploadClients
from dsp_tools.commands.xmlupload.models.upload_state import UploadState
from dsp_tools.commands.xmlupload.prepare_xml_input.check_consistency_with_ontology import (
    do_xml_consistency_check_with_ontology,
)
from dsp_tools.commands.xmlupload.prepare_xml_input.iiif_uri_validator import IIIFUriValidator
from dsp_tools.commands.xmlupload.prepare_xml_input.ontology_client import OntologyClient
from dsp_tools.commands.xmlupload.stash.stash_circular_references import identify_circular_references
from dsp_tools.commands.xmlupload.stash.stash_circular_references import stash_circular_references
from dsp_tools.commands.xmlupload.stash.stash_models import Stash
from dsp_tools.commands.xmlupload.transform_into_intermediary_classes import (
    transform_all_resources_into_intermediary_resources,
)
from dsp_tools.commands.xmlupload.upload_config import UploadConfig
from dsp_tools.models.custom_warnings import DspToolsUserWarning
from dsp_tools.models.exceptions import BaseError
from dsp_tools.models.exceptions import InputError
from dsp_tools.models.exceptions import UserError
from dsp_tools.models.projectContext import ProjectContext
from dsp_tools.utils.connection import Connection

LIST_SEPARATOR = "\n-    "


def get_upload_state(
    resources: list[XMLResource],
    clients: UploadClients,
    stash: Stash | None,
    config: UploadConfig,
    permissions_lookup: dict[str, Permissions],
) -> UploadState:
    """
    Transforms the XMLResources and creates the upload state.

    Args:
        resources: list of resources
        clients: clients to retrieve information from the API
        stash: Stashed links and texts
        config: upload config
        permissions_lookup: lookup for permissions

    Returns:
        Upload state

    Raises:
        InputError: If a resource could not be transformed, an error is raised.
    """
    project_onto_dict = clients.project_client.get_ontology_name_dict()
    listnode_lookup = clients.list_client.get_list_node_id_to_iri_lookup()
    project_context = get_json_ld_context_for_project(project_onto_dict)
    namespaces = make_namespace_dict_from_onto_names(project_onto_dict)
    intermediary_lookups = IntermediaryLookups(
        permissions=permissions_lookup, listnodes=listnode_lookup, namespaces=namespaces
    )
    result = transform_all_resources_into_intermediary_resources(resources, intermediary_lookups)
    if result.resource_failures:
        failures = [f"Resource ID: '{x.resource_id}', Message: {x.failure_msg}" for x in result.resource_failures]
        msg = (
            f"{datetime.now()}: WARNING: Unable to create the following resource(s):"
            f"{LIST_SEPARATOR}{LIST_SEPARATOR.join(failures)}"
        )
        raise InputError(msg)
    return UploadState(
        pending_resources=result.transformed_resources,
        pending_stash=stash,
        config=config,
        project_context=project_context,
    )


def prepare_upload_from_root(
    root: etree._Element,
    ontology_client: OntologyClient,
) -> tuple[list[XMLResource], dict[str, Permissions], Stash | None]:
    """Do the consistency check, resolve circular references, and return the resources and permissions."""
    do_xml_consistency_check_with_ontology(onto_client=ontology_client, root=root)
    return _resolve_circular_references(
        root=root,
        con=ontology_client.con,
        default_ontology=ontology_client.default_ontology,
    )


def _validate_iiif_uris(root: etree._Element) -> None:
    uris = [uri.strip() for node in root.iter(tag="iiif-uri") if (uri := node.text)]
    if problems := IIIFUriValidator(uris).validate():
        msg = problems.get_msg()
        warnings.warn(DspToolsUserWarning(msg))
        logger.warning(msg)


def _resolve_circular_references(
    root: etree._Element,
    con: Connection,
    default_ontology: str,
) -> tuple[list[XMLResource], dict[str, Permissions], Stash | None]:
    logger.info("Checking resources for circular references...")
    print(f"{datetime.now()}: Checking resources for circular references...")
    stash_lookup, upload_order = identify_circular_references(root)
    logger.info("Get data from XML...")
    resources, permissions_lookup = _get_data_from_xml(
        con=con,
        root=root,
        default_ontology=default_ontology,
    )
    sorting_lookup = {res.res_id: res for res in resources}
    resources = [sorting_lookup[res_id] for res_id in upload_order]
    logger.info("Stashing circular references...")
    print(f"{datetime.now()}: Stashing circular references...")
    stash = stash_circular_references(resources, stash_lookup, permissions_lookup)
    return resources, permissions_lookup, stash


def _get_data_from_xml(
    con: Connection,
    root: etree._Element,
    default_ontology: str,
) -> tuple[list[XMLResource], dict[str, Permissions]]:
    proj_context = _get_project_context_from_server(connection=con, shortcode=root.attrib["shortcode"])
    permissions = _extract_permissions_from_xml(root, proj_context)
    resources = _extract_resources_from_xml(root, default_ontology)
    permissions_lookup = {name: perm.get_permission_instance() for name, perm in permissions.items()}
    return resources, permissions_lookup


def _get_project_context_from_server(connection: Connection, shortcode: str) -> ProjectContext:
    """
    This function retrieves the project context previously uploaded on the server (json file)

    Args:
        connection: connection to the server
        shortcode: shortcode of the project

    Returns:
        Project context

    Raises:
        UserError: If the project was not previously uploaded on the server
    """
    try:
        proj_context = ProjectContext(con=connection, shortcode=shortcode)
    except BaseError:
        logger.opt(exception=True).error("Unable to retrieve project context from DSP server")
        raise UserError("Unable to retrieve project context from DSP server") from None
    return proj_context


def _extract_permissions_from_xml(root: etree._Element, proj_context: ProjectContext) -> dict[str, XmlPermission]:
    permission_ele = list(root.iter(tag="permissions"))
    permissions = [XmlPermission(permission, proj_context) for permission in permission_ele]
    return {permission.permission_id: permission for permission in permissions}


def _extract_resources_from_xml(root: etree._Element, default_ontology: str) -> list[XMLResource]:
    resources = list(root.iter(tag="resource"))
    return [XMLResource.from_node(res, default_ontology) for res in resources]
