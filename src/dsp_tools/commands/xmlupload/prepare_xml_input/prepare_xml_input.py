from __future__ import annotations

import warnings
from datetime import datetime
from pathlib import Path

from loguru import logger
from lxml import etree

from dsp_tools.commands.xmlupload.models.deserialise.xmlpermission import XmlPermission
from dsp_tools.commands.xmlupload.models.deserialise.xmlresource import XMLResource
from dsp_tools.commands.xmlupload.models.permission import Permissions
from dsp_tools.commands.xmlupload.prepare_xml_input.check_consistency_with_ontology import (
    do_xml_consistency_check_with_ontology,
)
from dsp_tools.commands.xmlupload.prepare_xml_input.iiif_uri_validator import IIIFUriValidator
from dsp_tools.commands.xmlupload.prepare_xml_input.ontology_client import OntologyClient
from dsp_tools.commands.xmlupload.prepare_xml_input.read_validate_xml_file import check_if_bitstreams_exist
from dsp_tools.commands.xmlupload.prepare_xml_input.read_validate_xml_file import validate_and_parse
from dsp_tools.commands.xmlupload.stash.stash_circular_references import identify_circular_references
from dsp_tools.commands.xmlupload.stash.stash_circular_references import stash_circular_references
from dsp_tools.commands.xmlupload.stash.stash_models import Stash
from dsp_tools.models.custom_warnings import DspToolsUserWarning
from dsp_tools.models.exceptions import BaseError
from dsp_tools.models.exceptions import UserError
from dsp_tools.models.projectContext import ProjectContext
from dsp_tools.utils.connection import Connection


def _parse_xml(imgdir: str, input_file: Path) -> tuple[str, etree._Element, str]:
    """
    This function takes a path to an XML file.
    It validates the file against the XML schema.
    It checks if all the mentioned bitstream files are in the specified location.
    It retrieves the shortcode and default ontology from the XML file.

    Args:
        imgdir: directory to the bitstream files
        input_file: file that will be pased

    Returns:
        The ontology name, the parsed XML file and the shortcode of the project
    """
    root, shortcode, default_ontology = validate_and_parse(input_file)
    check_if_bitstreams_exist(root=root, imgdir=imgdir)
    logger.info(f"Validated and parsed the XML file. {shortcode=:} and {default_ontology=:}")
    return default_ontology, root, shortcode


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
