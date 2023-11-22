from __future__ import annotations

import json
import sys
from dataclasses import asdict
from datetime import datetime
from logging import FileHandler
from pathlib import Path
from typing import Any, Union

from lxml import etree

from dsp_tools.commands.xmlupload.check_consistency_with_ontology import do_xml_consistency_check
from dsp_tools.commands.xmlupload.iri_resolver import IriResolver
from dsp_tools.commands.xmlupload.list_client import ListClient, ListClientLive
from dsp_tools.commands.xmlupload.models.permission import Permissions
from dsp_tools.commands.xmlupload.models.sipi import Sipi
from dsp_tools.commands.xmlupload.models.xmlpermission import XmlPermission
from dsp_tools.commands.xmlupload.models.xmlresource import BitstreamInfo, XMLResource
from dsp_tools.commands.xmlupload.ontology_client import OntologyClientLive
from dsp_tools.commands.xmlupload.project_client import ProjectClient, ProjectClientLive
from dsp_tools.commands.xmlupload.read_validate_xml_file import validate_and_parse_xml_file
from dsp_tools.commands.xmlupload.resource_create_client import ResourceCreateClient
from dsp_tools.commands.xmlupload.resource_multimedia import handle_bitstream
from dsp_tools.commands.xmlupload.stash.stash_circular_references import (
    identify_circular_references,
    stash_circular_references,
)
from dsp_tools.commands.xmlupload.stash.stash_models import Stash
from dsp_tools.commands.xmlupload.stash.upload_stashed_resptr_props import upload_stashed_resptr_props
from dsp_tools.commands.xmlupload.stash.upload_stashed_xml_texts import upload_stashed_xml_texts
from dsp_tools.commands.xmlupload.upload_config import DiagnosticsConfig, UploadConfig
from dsp_tools.commands.xmlupload.write_diagnostic_info import write_id2iri_mapping
from dsp_tools.models.exceptions import BaseError, UserError
from dsp_tools.models.projectContext import ProjectContext
from dsp_tools.utils.connection import Connection
from dsp_tools.utils.create_logger import get_logger
from dsp_tools.utils.json_ld_util import get_json_ld_context_for_project
from dsp_tools.utils.shared import login, try_network_action

logger = get_logger(__name__)


def xmlupload(
    input_file: Union[str, Path, etree._ElementTree[Any]],
    server: str,
    user: str,
    password: str,
    imgdir: str,
    sipi: str,
    config: UploadConfig = UploadConfig(),
) -> bool:
    """
    This function reads an XML file and imports the data described in it onto the DSP server.

    Args:
        input_file: path to the XML file or parsed ElementTree
        server: the DSP server where the data should be imported
        user: the user (e-mail) with which the data should be imported
        password: the password of the user with which the data should be imported
        imgdir: the image directory
        sipi: the sipi instance to be used
        config: the upload configuration

    Raises:
        BaseError: in case of permanent network or software failure
        UserError: in case of permanent network or software failure, or if the XML file is invalid

    Returns:
        True if all resources could be uploaded without errors; False if one of the resources could not be
        uploaded because there is an error in it
    """
    default_ontology, root, shortcode = validate_and_parse_xml_file(
        input_file=input_file,
        imgdir=imgdir,
        preprocessing_done=config.preprocessing_done,
    )

    config = config.with_server_info(
        server=server,
        shortcode=shortcode,
        onto_name=default_ontology,
    )

    # establish connection to DSP server
    con = login(server=server, user=user, password=password, dump=config.diagnostics.dump)
    sipi_server = Sipi(sipi, con.get_token())

    ontology_client = OntologyClientLive(
        con=con,
        shortcode=shortcode,
        default_ontology=default_ontology,
        save_location=config.diagnostics.save_location,
    )
    do_xml_consistency_check(onto_client=ontology_client, root=root)

    resources, permissions_lookup, stash = _prepare_upload(
        root=root,
        con=con,
        default_ontology=default_ontology,
        verbose=config.diagnostics.verbose,
    )

    project_client: ProjectClient = ProjectClientLive(con, config.shortcode)
    if default_ontology not in project_client.get_ontology_name_dict():
        raise UserError(
            f"The default ontology '{default_ontology}' "
            "specified in the XML file is not part of the project on the DSP server."
        )
    list_client: ListClient = ListClientLive(con, project_client.get_project_iri())

    iri_resolver, failed_uploads = _upload(
        resources=resources,
        imgdir=imgdir,
        sipi_server=sipi_server,
        permissions_lookup=permissions_lookup,
        con=con,
        stash=stash,
        config=config,
        project_client=project_client,
        list_client=list_client,
    )

    write_id2iri_mapping(iri_resolver.lookup, input_file, config.diagnostics)
    success = not failed_uploads
    if success:
        print(f"{datetime.now()}: All resources have successfully been uploaded.")
        logger.info("All resources have successfully been uploaded.")
    else:
        print(f"\n{datetime.now()}: WARNING: Could not upload the following resources: {failed_uploads}\n")
        logger.warning(f"Could not upload the following resources: {failed_uploads}")
    return success


def _prepare_upload(
    root: etree._Element,
    con: Connection,
    default_ontology: str,
    verbose: bool,
) -> tuple[list[XMLResource], dict[str, Permissions], Stash | None]:
    logger.info("Checking resources for circular references...")
    if verbose:
        print(f"{datetime.now()}: Checking resources for circular references...")
    stash_lookup, upload_order = identify_circular_references(root)
    logger.info("Get data from XML...")
    resources, permissions_lookup = _get_data_from_xml(
        con=con,
        root=root,
        default_ontology=default_ontology,
    )
    sorting_lookup = {res.id: res for res in resources}
    resources = [sorting_lookup[res_id] for res_id in upload_order]
    logger.info("Stashing circular references...")
    if verbose:
        print(f"{datetime.now()}: Stashing circular references...")
    stash = stash_circular_references(resources, stash_lookup, permissions_lookup)
    return resources, permissions_lookup, stash


def _upload(
    resources: list[XMLResource],
    imgdir: str,
    sipi_server: Sipi,
    permissions_lookup: dict[str, Permissions],
    con: Connection,
    stash: Stash | None,
    config: UploadConfig,
    project_client: ProjectClient,
    list_client: ListClient,
) -> tuple[IriResolver, list[str]]:
    # upload all resources, then update the resources with the stashed XML texts and resptrs
    failed_uploads: list[str] = []
    iri_resolver = IriResolver()
    try:
        iri_resolver, failed_uploads = _upload_resources(
            resources=resources,
            imgdir=imgdir,
            sipi_server=sipi_server,
            permissions_lookup=permissions_lookup,
            con=con,
            config=config,
            project_client=project_client,
            list_client=list_client,
            id_to_iri_resolver=iri_resolver,
        )
        nonapplied_stash = (
            _upload_stash(
                stash=stash,
                iri_resolver=iri_resolver,
                con=con,
                verbose=config.diagnostics.verbose,
                project_client=project_client,
            )
            if stash
            else None
        )
        if nonapplied_stash:
            msg = "Some stashed resptrs or XML texts could not be reapplied to their resources on the DSP server."
            logger.error(msg)
            raise BaseError(msg)
    except BaseException as err:  # pylint: disable=broad-except
        # The forseeable errors are already handled by the variables
        # failed_uploads, nonapplied_xml_texts, and nonapplied_resptr_props.
        # Here we catch the unforseeable exceptions, hence BaseException (=the base class of all exceptions)
        _handle_upload_error(
            err=err,
            iri_resolver=iri_resolver,
            failed_uploads=failed_uploads,
            stash=stash,
            diagnostics=config.diagnostics,
        )
    return iri_resolver, failed_uploads


def _get_data_from_xml(
    con: Connection,
    root: etree._Element,
    default_ontology: str,
) -> tuple[list[XMLResource], dict[str, Permissions]]:
    proj_context = _get_project_context_from_server(connection=con)
    permissions = _extract_permissions_from_xml(root, proj_context)
    resources = _extract_resources_from_xml(root, default_ontology)
    permissions_lookup = {name: perm.get_permission_instance() for name, perm in permissions.items()}
    return resources, permissions_lookup


def _upload_stash(
    stash: Stash,
    iri_resolver: IriResolver,
    con: Connection,
    verbose: bool,
    project_client: ProjectClient,
) -> Stash | None:
    if stash.standoff_stash:
        nonapplied_standoff = upload_stashed_xml_texts(
            verbose=verbose,
            iri_resolver=iri_resolver,
            con=con,
            stashed_xml_texts=stash.standoff_stash,
        )
    else:
        nonapplied_standoff = None
    context = get_json_ld_context_for_project(project_client.get_ontology_name_dict())
    if stash.link_value_stash:
        nonapplied_resptr_props = upload_stashed_resptr_props(
            verbose=verbose,
            iri_resolver=iri_resolver,
            con=con,
            stashed_resptr_props=stash.link_value_stash,
            context=context,
        )
    else:
        nonapplied_resptr_props = None
    return Stash.make(nonapplied_standoff, nonapplied_resptr_props)


def _get_project_context_from_server(connection: Connection) -> ProjectContext:
    """
    This function retrieves the project context previously uploaded on the server (json file)

    Args:
        connection: connection to the server

    Returns:
        Project context

    Raises:
        UserError: If the project was not previously uploaded on the server
    """
    try:
        proj_context: ProjectContext = try_network_action(lambda: ProjectContext(con=connection))
    except BaseError:
        logger.error(
            "Unable to retrieve project context from DSP server",
            exc_info=True,
        )
        raise UserError("Unable to retrieve project context from DSP server") from None
    return proj_context


def _extract_permissions_from_xml(root: etree._Element, proj_context: ProjectContext) -> dict[str, XmlPermission]:
    permission_ele = list(root.iter(tag="permissions"))
    permissions = [XmlPermission(permission, proj_context) for permission in permission_ele]
    return {permission.id: permission for permission in permissions}


def _extract_resources_from_xml(root: etree._Element, default_ontology: str) -> list[XMLResource]:
    resources = list(root.iter(tag="resource"))
    return [XMLResource(res, default_ontology) for res in resources]


def _upload_resources(
    resources: list[XMLResource],
    imgdir: str,
    sipi_server: Sipi,
    permissions_lookup: dict[str, Permissions],
    con: Connection,
    config: UploadConfig,
    project_client: ProjectClient,
    list_client: ListClient,
    id_to_iri_resolver: IriResolver,
) -> tuple[IriResolver, list[str]]:
    """
    Iterates through all resources and tries to upload them to DSP.
    If a temporary exception occurs, the action is repeated until success,
    and if a permanent exception occurs, the resource is skipped.

    Args:
        resources: list of XMLResources to upload to DSP
        imgdir: folder containing the multimedia files
        sipi_server: Sipi instance
        permissions_lookup: maps permission strings to Permission objects
        con: connection to DSP
        config: the upload configuration
        project_client: a client for HTTP communication with the DSP-API
        list_client: a client for HTTP communication with the DSP-API
        id_to_iri_resolver: a resolver for internal IDs to IRIs

    Returns:
        id2iri_mapping, failed_uploads
    """
    failed_uploads: list[str] = []

    project_iri = project_client.get_project_iri()
    json_ld_context = get_json_ld_context_for_project(project_client.get_ontology_name_dict())
    listnode_lookup = list_client.get_list_node_id_to_iri_lookup()

    resource_create_client = ResourceCreateClient(
        con=con,
        project_iri=project_iri,
        id_to_iri_resolver=id_to_iri_resolver,
        json_ld_context=json_ld_context,
        permissions_lookup=permissions_lookup,
        listnode_lookup=listnode_lookup,
    )

    for i, resource in enumerate(resources):
        bitstream_information = None
        if bitstream := resource.bitstream:
            bitstream_information = handle_bitstream(
                resource=resource,
                bitstream=bitstream,
                preprocessing_done=config.preprocessing_done,
                permissions_lookup=permissions_lookup,
                sipi_server=sipi_server,
                imgdir=imgdir,
            )
            if not bitstream_information:
                failed_uploads.append(resource.id)
                continue

        res = _create_resource(resource, bitstream_information, resource_create_client)
        if not res:
            failed_uploads.append(resource.id)
            continue
        iri, label = res
        id_to_iri_resolver.update(resource.id, iri)

        resource_designation = f"'{label}' (ID: '{resource.id}', IRI: '{iri}')"
        print(f"{datetime.now()}: Created resource {i+1}/{len(resources)}: {resource_designation}")
        logger.info(f"Created resource {i+1}/{len(resources)}: {resource_designation}")

    return id_to_iri_resolver, failed_uploads


def _create_resource(
    resource: XMLResource,
    bitstream_information: BitstreamInfo | None,
    resource_create_client: ResourceCreateClient,
) -> tuple[str, str] | None:
    try:
        return resource_create_client.create_resource(resource, bitstream_information)
    except BaseError as err:
        err_msg = err.orig_err_msg_from_api or err.message
        print(f"{datetime.now()}: WARNING: Unable to create resource '{resource.label}' ({resource.id}): {err_msg}")
        log_msg = (
            f"Unable to create resource '{resource.label}' ({resource.id})\n"
            f"Resource details:\n{vars(resource)}\n"
            f"Property details:\n" + "\n".join([str(vars(prop)) for prop in resource.properties])
        )
        logger.warning(log_msg, exc_info=True)
        return None
    except Exception as err:  # pylint: disable=broad-except
        msg = f"Unable to create resource '{resource.label}' ({resource.id})"
        print(f"{datetime.now()}: WARNING: {msg}: {err}")
        log_msg = (
            f"Unable to create resource '{resource.label}' ({resource.id})\n"
            f"Resource details:\n{vars(resource)}\n"
            f"Property details:\n" + "\n".join([str(vars(prop)) for prop in resource.properties])
        )
        logger.exception(log_msg)
        return None


def _handle_upload_error(
    err: BaseException,
    iri_resolver: IriResolver,
    failed_uploads: list[str],
    stash: Stash | None,
    diagnostics: DiagnosticsConfig,
) -> None:
    """
    In case the xmlupload must be interrupted,
    e.g. because of an error that could not be handled,
    or due to keyboard interrupt,
    this method ensures
    that all information about what is already in DSP
    is written into diagnostic files.

    It then quits the Python interpreter with exit code 1.

    Args:
        err: error that was the cause of the abort
        iri_resolver: a resolver for internal IDs to IRIs
        failed_uploads: resources that caused an error when uploading to DSP
        stash: an object that contains all stashed links that could not be reapplied to their resources
        diagnostics: the diagnostics configuration
    """
    logfiles = ", ".join([handler.baseFilename for handler in logger.handlers if isinstance(handler, FileHandler)])
    print(
        f"\n==========================================\n"
        f"{datetime.now()}: xmlupload must be aborted because of an error.\n"
        f"Error message: '{err}'\n"
        f"For more information, see the log file: {logfiles}\n"
    )
    logger.error("xmlupload must be aborted because of an error", exc_info=err)

    timestamp = diagnostics.timestamp_str
    servername = diagnostics.server_as_foldername

    if iri_resolver.non_empty():
        id2iri_mapping_file = f"{diagnostics.save_location}/{timestamp}_id2iri_mapping_{servername}.json"
        with open(id2iri_mapping_file, "x", encoding="utf-8") as f:
            json.dump(iri_resolver.lookup, f, ensure_ascii=False, indent=4)
        print(f"The mapping of internal IDs to IRIs was written to {id2iri_mapping_file}")
        logger.info(f"The mapping of internal IDs to IRIs was written to {id2iri_mapping_file}")

    if stash:
        filename = _save_stash_as_json(
            stash=stash,
            save_location=diagnostics.save_location,
            timestamp_str=timestamp,
            servername=servername,
        )
        msg = (
            f"There are stashed links that could not be reapplied to the resources they were stripped from. "
            f"They were saved to {filename}\n"
        )
        print(msg)
        logger.info(msg)

    # print the resources that threw an error when they were tried to be uploaded
    if failed_uploads:
        msg = f"Independently of this error, there were some resources that could not be uploaded: {failed_uploads}"
        print(msg)
        logger.info(msg)

    sys.exit(1)


def _save_stash_as_json(
    stash: Stash,
    save_location: Path,
    timestamp_str: str,
    servername: str,
) -> str:
    filename = f"{save_location}/{timestamp_str}_stashed_links_{servername}.json"
    with open(filename, "x", encoding="utf-8") as file:
        json.dump(
            obj=asdict(stash),
            fp=file,
            ensure_ascii=False,
            indent=4,
        )
    return filename
