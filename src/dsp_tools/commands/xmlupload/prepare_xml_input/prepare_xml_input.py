from __future__ import annotations

from typing import Any

from loguru import logger
from lxml import etree

from dsp_tools.clients.connection import Connection
from dsp_tools.clients.connection_live import ConnectionLive
from dsp_tools.clients.list_client import ListGetClient
from dsp_tools.clients.list_client import ListInfo
from dsp_tools.commands.xmlupload.exceptions import UnableToRetrieveProjectInfoError
from dsp_tools.commands.xmlupload.models.lookup_models import XmlReferenceLookups
from dsp_tools.commands.xmlupload.models.processed.res import ProcessedResource
from dsp_tools.commands.xmlupload.models.upload_clients import UploadClients
from dsp_tools.commands.xmlupload.stash.analyse_circular_reference_graph import generate_upload_order
from dsp_tools.commands.xmlupload.stash.create_info_for_graph import create_info_for_graph_from_processed_resources
from dsp_tools.commands.xmlupload.stash.stash_circular_references import stash_circular_references
from dsp_tools.commands.xmlupload.stash.stash_models import Stash
from dsp_tools.error.exceptions import BaseError
from dsp_tools.legacy_models.projectContext import ProjectContext
from dsp_tools.utils.xml_parsing.get_lookups import get_authorship_lookup
from dsp_tools.utils.xml_parsing.get_lookups import get_permissions_lookup
from dsp_tools.utils.xml_parsing.get_parsed_resources import get_parsed_resources
from dsp_tools.utils.xml_parsing.models.parsed_resource import ParsedResource

LIST_SEPARATOR = "\n-    "


def get_parsed_resources_and_mappers(
    root: etree._Element, clients: UploadClients
) -> tuple[list[ParsedResource], XmlReferenceLookups]:
    logger.debug("Get ParsedResource and XML-Lookups from root")
    print("Parsing XML file for upload.")
    parsed_resources = get_parsed_resources(root, clients.legal_info_client.server)
    processed_lookups = _get_xml_reference_lookups(root=root, clients=clients)
    return parsed_resources, processed_lookups


def _get_xml_reference_lookups(root: etree._Element, clients: UploadClients) -> XmlReferenceLookups:
    con = ConnectionLive(clients.legal_info_client.server, clients.legal_info_client.authentication_client)
    proj_context = _get_project_context_from_server(connection=con, shortcode=root.attrib["shortcode"])
    permissions_lookup = get_permissions_lookup(root, proj_context)
    authorship_lookup = get_authorship_lookup(root)
    listnode_lookup = _get_list_node_to_iri_lookup(clients.list_client)
    return XmlReferenceLookups(
        permissions=permissions_lookup,
        listnodes=listnode_lookup,
        authorships=authorship_lookup,
    )


def _get_project_context_from_server(connection: Connection, shortcode: str) -> ProjectContext:
    try:
        proj_context = ProjectContext(con=connection, shortcode=shortcode)
    except BaseError:
        logger.exception("Unable to retrieve project context from DSP server")
        raise UnableToRetrieveProjectInfoError("Unable to retrieve project context from DSP server") from None
    return proj_context


def get_stash_and_upload_order(
    resources: list[ProcessedResource],
) -> tuple[list[ProcessedResource], Stash | None]:
    logger.debug("Get stash and upload order")
    info_for_graph = create_info_for_graph_from_processed_resources(resources)
    stash_lookup, upload_order = generate_upload_order(info_for_graph)
    sorting_lookup = {res.res_id: res for res in resources}
    sorted_resources = [sorting_lookup[res_id] for res_id in upload_order]
    stash = stash_circular_references(sorted_resources, stash_lookup)
    return sorted_resources, stash


def _get_list_node_to_iri_lookup(list_client: ListGetClient) -> dict[tuple[str, str], str]:
    all_info = list_client.get_all_lists_and_nodes()
    return _reformat_all_lists(all_info)


def _reformat_all_lists(all_info: list[ListInfo]) -> dict[tuple[str, str], str]:
    complete_lookup = {}
    for li in all_info:
        complete_lookup.update(_reformat_one_list(li))
    return complete_lookup


def _reformat_one_list(list_info: ListInfo) -> dict[tuple[str, str], str]:
    list_name = list_info.listinfo["name"]
    list_iri = list_info.listinfo["id"]
    is_nested = _has_nested_children(list_info.children)

    # Start with list itself and IRI lookup
    result = {
        (list_name, list_name): list_iri,
        ("", list_iri): list_iri,
    }

    # Recursively extract all nodes
    all_nodes = _extract_all_nodes(list_info.children)

    # Add tuple mappings for all nodes
    for node_name, node_iri in all_nodes:
        if is_nested:
            # Nested list: (list-name, node-name)
            result[(list_name, node_name)] = node_iri
        else:
            # Flat list: (node-name, list-name)
            result[(node_name, list_name)] = node_iri
        # IRI lookup
        result[("", node_iri)] = node_iri

    return result


def _has_nested_children(children: list[dict[str, Any]]) -> bool:
    """Check if any child has nested children."""
    for child in children:
        if "children" in child:
            return True
    return False


def _extract_all_nodes(children: list[dict[str, Any]]) -> list[tuple[str, str]]:
    nodes = []
    for child in children:
        node_name = child["name"]
        node_iri = child["id"]
        nodes.append((node_name, node_iri))
        if "children" in child:
            nodes.extend(_extract_all_nodes(child["children"]))
    return nodes
