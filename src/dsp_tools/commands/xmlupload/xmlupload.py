from __future__ import annotations

import pickle
import sys
import warnings
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from loguru import logger
from lxml import etree

from dsp_tools.cli.args import ServerCredentials
from dsp_tools.commands.xmlupload.check_consistency_with_ontology import do_xml_consistency_check_with_ontology
from dsp_tools.commands.xmlupload.iri_resolver import IriResolver
from dsp_tools.commands.xmlupload.list_client import ListClient
from dsp_tools.commands.xmlupload.list_client import ListClientLive
from dsp_tools.commands.xmlupload.models.deserialise.xmlpermission import XmlPermission
from dsp_tools.commands.xmlupload.models.deserialise.xmlresource import XMLResource
from dsp_tools.commands.xmlupload.models.ingest import AssetClient
from dsp_tools.commands.xmlupload.models.ingest import BulkIngestedAssetClient
from dsp_tools.commands.xmlupload.models.ingest import DspIngestClientLive
from dsp_tools.commands.xmlupload.models.namespace_context import get_json_ld_context_for_project
from dsp_tools.commands.xmlupload.models.permission import Permissions
from dsp_tools.commands.xmlupload.models.upload_state import UploadState
from dsp_tools.commands.xmlupload.ontology_client import OntologyClient
from dsp_tools.commands.xmlupload.ontology_client import OntologyClientLive
from dsp_tools.commands.xmlupload.project_client import ProjectClient
from dsp_tools.commands.xmlupload.project_client import ProjectClientLive
from dsp_tools.commands.xmlupload.read_validate_xml_file import validate_and_parse_xml_file
from dsp_tools.commands.xmlupload.resource_create_client import ResourceCreateClient
from dsp_tools.commands.xmlupload.stash.stash_circular_references import identify_circular_references
from dsp_tools.commands.xmlupload.stash.stash_circular_references import stash_circular_references
from dsp_tools.commands.xmlupload.stash.stash_models import Stash
from dsp_tools.commands.xmlupload.stash.upload_stashed_resptr_props import upload_stashed_resptr_props
from dsp_tools.commands.xmlupload.stash.upload_stashed_xml_texts import upload_stashed_xml_texts
from dsp_tools.commands.xmlupload.upload_config import UploadConfig
from dsp_tools.commands.xmlupload.write_diagnostic_info import write_id2iri_mapping
from dsp_tools.models.custom_warnings import DspToolsUserWarning
from dsp_tools.models.exceptions import BaseError
from dsp_tools.models.exceptions import PermanentTimeOutError
from dsp_tools.models.exceptions import UserError
from dsp_tools.models.exceptions import XmlUploadInterruptedError
from dsp_tools.models.projectContext import ProjectContext
from dsp_tools.utils.connection import Connection
from dsp_tools.utils.connection_live import ConnectionLive
from dsp_tools.utils.logger_config import logger_savepath


@dataclass(frozen=True)
class UploadClients:
    """"""

    asset_client: AssetClient
    project_client: ProjectClient
    list_client: ListClient


def xmlupload(
    input_file: str | Path | etree._ElementTree[Any],
    creds: ServerCredentials,
    imgdir: str,
    config: UploadConfig = UploadConfig(),
) -> bool:
    """
    This function reads an XML file and imports the data described in it onto the DSP server.

    Args:
        input_file: path to XML file containing the resources, or the XML tree itself
        creds: the credentials to access the DSP server
        imgdir: the image directory
        config: the upload configuration

    Raises:
        BaseError: in case of permanent network or software failure
        UserError: in case of permanent network or software failure, or if the XML file is invalid
        InputError: in case of permanent network or software failure, or if the XML file is invalid

    Returns:
        True if all resources could be uploaded without errors; False if one of the resources could not be
        uploaded because there is an error in it
    """

    default_ontology, root, shortcode = validate_and_parse_xml_file(
        input_file=input_file,
        imgdir=imgdir,
        preprocessing_done=config.media_previously_uploaded,
    )

    con = ConnectionLive(creds.server)
    con.login(creds.user, creds.password)
    config = config.with_server_info(server=creds.server, shortcode=shortcode)

    clients = _get_live_clients(con, creds, config, imgdir)

    ontology_client = OntologyClientLive(con=con, shortcode=shortcode, default_ontology=default_ontology)
    resources, permissions_lookup, stash = prepare_upload(root, ontology_client)

    return execute_upload(config, clients, resources, permissions_lookup, stash)


def _get_live_clients(
    con: Connection,
    creds: ServerCredentials,
    config: UploadConfig,
    imgdir: str,
) -> UploadClients:
    ingest_client: AssetClient
    if config.media_previously_uploaded:
        ingest_client = BulkIngestedAssetClient()
    else:
        ingest_client = DspIngestClientLive(
            dsp_ingest_url=creds.dsp_ingest_url,
            token=con.get_token(),
            shortcode=config.shortcode,
            imgdir=imgdir,
        )
    project_client: ProjectClient = ProjectClientLive(con, config.shortcode)
    list_client: ListClient = ListClientLive(con, project_client.get_project_iri())
    return UploadClients(
        asset_client=ingest_client,
        project_client=project_client,
        list_client=list_client,
    )


def execute_upload(
    config: UploadConfig,
    clients: UploadClients,
    resources: list[XMLResource],
    permissions_lookup: dict[str, Permissions],
    stash: Stash | None,
) -> bool:
    """"""
    upload_state = UploadState(resources, [], IriResolver(), stash, config, permissions_lookup)

    upload_resources(
        upload_state=upload_state,
        ingest_client=clients.asset_client,
        project_client=clients.project_client,
        list_client=clients.list_client,
    )

    return cleanup_upload(upload_state)


def prepare_upload(
    root: etree._Element,
    ontology_client: OntologyClient,
) -> tuple[list[XMLResource], dict[str, Permissions], Stash | None]:
    """"""
    do_xml_consistency_check_with_ontology(onto_client=ontology_client, root=root)
    return _resolve_circular_references(
        root=root,
        con=ontology_client.con,
        default_ontology=ontology_client.default_ontology,
    )


def cleanup_upload(upload_state: UploadState) -> bool:
    """
    Write the id2iri mapping to a file and print a message to the console.

    Args:
        upload_state: the current state of the upload

    Returns:
        success status (deduced from failed_uploads and non-applied stash)
    """
    write_id2iri_mapping(upload_state.iri_resolver.lookup, upload_state.config.diagnostics)
    has_stash_failed = upload_state.pending_stash and not upload_state.pending_stash.is_empty()
    if not upload_state.failed_uploads and not has_stash_failed:
        success = True
        print(f"{datetime.now()}: All resources have successfully been uploaded.")
        logger.info("All resources have successfully been uploaded.")
    else:
        success = False
        if upload_state.failed_uploads:
            res_msg = f"Could not upload the following resources: {upload_state.failed_uploads}"
            print(f"\n{datetime.now()}: WARNING: {res_msg}\n")
            print(f"For more information, see the log file: {logger_savepath}\n")
            logger.warning(res_msg)
        if has_stash_failed:
            stash_msg = f"Could not reapply the following stash items: {upload_state.pending_stash}"
            print(f"\n{datetime.now()}: WARNING: {stash_msg}\n")
            print(f"For more information, see the log file: {logger_savepath}\n")
            logger.warning(stash_msg)
        msg = _save_upload_state(upload_state)
        print(msg)

    upload_state.config.diagnostics.save_location.unlink(missing_ok=True)
    return success


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


def upload_resources(
    upload_state: UploadState,
    ingest_client: AssetClient,
    project_client: ProjectClient,
    list_client: ListClient,
) -> None:
    """
    Actual upload of all resources to DSP.

    Args:
        upload_state: the current state of the upload
        ingest_client: ingest server client
        project_client: a client for HTTP communication with the DSP-API
        list_client: a client for HTTP communication with the DSP-API
    """
    try:
        _upload_resources(
            upload_state=upload_state,
            ingest_client=ingest_client,
            project_client=project_client,
            list_client=list_client,
        )
        if upload_state.pending_stash:
            _upload_stash(upload_state, project_client)
    except XmlUploadInterruptedError as err:
        _handle_upload_error(err, upload_state)


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
    upload_state: UploadState,
    project_client: ProjectClient,
) -> None:
    if upload_state.pending_stash and upload_state.pending_stash.standoff_stash:
        upload_stashed_xml_texts(upload_state, project_client.con)
    context = get_json_ld_context_for_project(project_client.get_ontology_name_dict())
    if upload_state.pending_stash and upload_state.pending_stash.link_value_stash:
        upload_stashed_resptr_props(upload_state, project_client.con, context)


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
        proj_context = ProjectContext(con=connection)
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
    return [XMLResource(res, default_ontology) for res in resources]


def _upload_resources(
    upload_state: UploadState,
    ingest_client: AssetClient,
    project_client: ProjectClient,
    list_client: ListClient,
) -> None:
    """
    Iterates through all resources and tries to upload them to DSP.
    If a temporary exception occurs, the action is repeated until success,
    and if a permanent exception occurs, the resource is skipped.

    Args:
        upload_state: the current state of the upload
        ingest_client: ingest server client
        project_client: a client for HTTP communication with the DSP-API
        list_client: a client for HTTP communication with the DSP-API

    Raises:
        BaseException: in case of an unhandled exception during resource creation
        XmlUploadInterruptedError: if the number of resources created is equal to the interrupt_after value
    """
    project_iri = project_client.get_project_iri()
    project_onto_dict = project_client.get_ontology_name_dict()
    listnode_lookup = list_client.get_list_node_id_to_iri_lookup()

    resource_create_client = ResourceCreateClient(
        con=project_client.con,
        project_iri=project_iri,
        iri_resolver=upload_state.iri_resolver,
        project_onto_dict=project_onto_dict,
        permissions_lookup=upload_state.permissions_lookup,
        listnode_lookup=listnode_lookup,
        media_previously_ingested=upload_state.config.media_previously_uploaded,
    )

    for creation_attempts_of_this_round, resource in enumerate(upload_state.pending_resources.copy()):
        _upload_one_resource(
            upload_state=upload_state,
            resource=resource,
            ingest_client=ingest_client,
            resource_create_client=resource_create_client,
            creation_attempts_of_this_round=creation_attempts_of_this_round,
        )


def _upload_one_resource(
    upload_state: UploadState,
    resource: XMLResource,
    ingest_client: AssetClient,
    resource_create_client: ResourceCreateClient,
    creation_attempts_of_this_round: int,
) -> None:
    try:
        if resource.bitstream:
            success, media_info = ingest_client.get_bitstream_info(
                resource.bitstream, upload_state.permissions_lookup, resource.label, resource.res_id
            )
        else:
            success, media_info = True, None

        if not success:
            upload_state.failed_uploads.append(resource.res_id)
            return
    except KeyboardInterrupt:
        raise XmlUploadInterruptedError("KeyboardInterrupt during media file upload") from None

    iri = None
    try:
        iri = resource_create_client.create_resource(resource, media_info)
    except (PermanentTimeOutError, KeyboardInterrupt) as err:
        warnings.warn(DspToolsUserWarning(f"{type(err).__name__}: Tidying up, then exit..."))
        msg = (
            f"There was a {type(err).__name__} while trying to create resource '{resource.res_id}'.\n"
            f"It is unclear if the resource '{resource.res_id}' was created successfully or not.\n"
            f"Please check manually in the DSP-APP or DB.\n"
            f"In case of successful creation, call 'resume-xmlupload' with the flag "
            f"'--skip-first-resource' to prevent duplication.\n"
            f"If not, a normal 'resume-xmlupload' can be started."
        )
        logger.error(msg)
        raise XmlUploadInterruptedError(msg) from None
    except Exception as err:  # noqa: BLE001 (blind-except)
        err_msg = err.message if isinstance(err, BaseError) else None
        _handle_resource_creation_failure(resource, err_msg)

    try:
        _tidy_up_resource_creation_idempotent(upload_state, iri, resource)
        _interrupt_if_indicated(upload_state, creation_attempts_of_this_round)
    except KeyboardInterrupt:
        warnings.warn(DspToolsUserWarning("KeyboardInterrupt: Tidying up, then exit..."))
        _tidy_up_resource_creation_idempotent(upload_state, iri, resource)
        raise XmlUploadInterruptedError("KeyboardInterrupt during tidy up") from None


def _interrupt_if_indicated(upload_state: UploadState, creation_attempts_of_this_round: int) -> None:
    # if the interrupt_after value is not set, the upload will not be interrupted
    interrupt_after = upload_state.config.interrupt_after or 999_999_999
    if creation_attempts_of_this_round + 1 >= interrupt_after:
        msg = f"Interrupted: Maximum number of resources was reached ({upload_state.config.interrupt_after})"
        raise XmlUploadInterruptedError(msg)


def _tidy_up_resource_creation_idempotent(
    upload_state: UploadState,
    iri: str | None,
    resource: XMLResource,
) -> None:
    previous_successful = len(upload_state.iri_resolver.lookup)
    previous_failed = len(upload_state.failed_uploads)
    upcoming = len(upload_state.pending_resources)
    current_res = previous_successful + previous_failed + 1
    total_res = previous_successful + previous_failed + upcoming
    if iri:
        # resource creation succeeded: update the iri_resolver
        upload_state.iri_resolver.lookup[resource.res_id] = iri
        msg = f"Created resource {current_res}/{total_res}: '{resource.label}' (ID: '{resource.res_id}', IRI: '{iri}')"
        print(f"{datetime.now()}: {msg}")
        logger.info(msg)
    else:  # noqa: PLR5501
        # resource creation failed gracefully: register it as failed
        if resource.res_id not in upload_state.failed_uploads:
            upload_state.failed_uploads.append(resource.res_id)

    if resource in upload_state.pending_resources:
        upload_state.pending_resources.remove(resource)


def _handle_resource_creation_failure(resource: XMLResource, err_msg: str | None) -> None:
    msg = f"{datetime.now()}: WARNING: Unable to create resource '{resource.label}' (ID: '{resource.res_id}')"
    if err_msg:
        msg = f"{msg}: {err_msg}"
    print(msg)
    log_msg = (
        f"Unable to create resource '{resource.label}' ({resource.res_id})\n"
        f"Resource details:\n{vars(resource)}\n"
        f"Property details:\n" + "\n".join([str(vars(prop)) for prop in resource.properties])
    )
    logger.exception(log_msg)


def _handle_upload_error(err: BaseException, upload_state: UploadState) -> None:
    """
    In case the xmlupload must be interrupted,
    e.g. because of an error that could not be handled,
    or due to keyboard interrupt,
    this method ensures
    that all information about what is already in DSP
    is written into diagnostic files.

    It then quits the Python interpreter with exit code 1.

    Args:
        err: the error that was the cause of the abort
        upload_state: the current state of the upload
    """
    if isinstance(err, XmlUploadInterruptedError):
        msg = "\n==========================================\n" + err.message + "\n"
        exit_code = 0
    else:
        msg = (
            f"\n==========================================\n"
            f"{datetime.now()}: xmlupload must be aborted because of an error.\n"
            f"Error message: '{err}'\n"
            f"For more information, see the log file: {logger_savepath}\n"
        )
        exit_code = 1

    msg += _save_upload_state(upload_state)

    if failed := upload_state.failed_uploads:
        msg += f"Independently from this, there were some resources that could not be uploaded: {failed}\n"

    if exit_code == 1:
        logger.exception(msg)
    else:
        logger.info(msg)
    print(msg)

    sys.exit(exit_code)


def _save_upload_state(upload_state: UploadState) -> str:
    save_location = upload_state.config.diagnostics.save_location
    save_location.unlink(missing_ok=True)
    save_location.touch(exist_ok=True)
    with open(save_location, "wb") as file:
        pickle.dump(upload_state, file)
    logger.info(f"Saved the current upload state to {save_location}")
    return f"Saved the current upload state to {save_location}.\n"
