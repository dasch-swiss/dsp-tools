from __future__ import annotations

import pickle
import sys
import warnings
from datetime import datetime
from pathlib import Path
from typing import Never

from loguru import logger
from lxml import etree
from tqdm import tqdm

from dsp_tools.cli.args import ServerCredentials
from dsp_tools.commands.xmlupload.check_consistency_with_ontology import do_xml_consistency_check_with_ontology
from dsp_tools.commands.xmlupload.iiif_uri_validator import IIIFUriValidator
from dsp_tools.commands.xmlupload.list_client import ListClient
from dsp_tools.commands.xmlupload.list_client import ListClientLive
from dsp_tools.commands.xmlupload.models.deserialise.xmlpermission import XmlPermission
from dsp_tools.commands.xmlupload.models.deserialise.xmlresource import XMLResource
from dsp_tools.commands.xmlupload.models.ingest import AssetClient
from dsp_tools.commands.xmlupload.models.ingest import DspIngestClientLive
from dsp_tools.commands.xmlupload.models.namespace_context import get_json_ld_context_for_project
from dsp_tools.commands.xmlupload.models.namespace_context import make_namespace_dict_from_onto_names
from dsp_tools.commands.xmlupload.models.permission import Permissions
from dsp_tools.commands.xmlupload.models.upload_clients import UploadClients
from dsp_tools.commands.xmlupload.models.upload_state import UploadState
from dsp_tools.commands.xmlupload.ontology_client import OntologyClient
from dsp_tools.commands.xmlupload.ontology_client import OntologyClientLive
from dsp_tools.commands.xmlupload.project_client import ProjectClient
from dsp_tools.commands.xmlupload.project_client import ProjectClientLive
from dsp_tools.commands.xmlupload.read_validate_xml_file import check_if_bitstreams_exist
from dsp_tools.commands.xmlupload.read_validate_xml_file import validate_and_parse
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
from dsp_tools.models.exceptions import PermanentConnectionError
from dsp_tools.models.exceptions import PermanentTimeOutError
from dsp_tools.models.exceptions import UserError
from dsp_tools.models.exceptions import XmlUploadInterruptedError
from dsp_tools.models.projectContext import ProjectContext
from dsp_tools.utils.authentication_client import AuthenticationClient
from dsp_tools.utils.authentication_client_live import AuthenticationClientLive
from dsp_tools.utils.connection import Connection
from dsp_tools.utils.connection_live import ConnectionLive
from dsp_tools.utils.logger_config import WARNINGS_SAVEPATH


def xmlupload(
    input_file: Path,
    creds: ServerCredentials,
    imgdir: str,
    config: UploadConfig = UploadConfig(),
) -> bool:
    """
    This function reads an XML file and imports the data described in it onto the DSP server.

    Args:
        input_file: path to XML file containing the resources
        creds: the credentials to access the DSP server
        imgdir: the image directory
        config: the configuration for the upload

    Raises:
        BaseError: in case of permanent network or software failure
        UserError: in case of permanent network or software failure, or if the XML file is invalid
        InputError: in case of permanent network or software failure, or if the XML file is invalid

    Returns:
        True if all resources could be uploaded without errors; False if one of the resources could not be
        uploaded because there is an error in it
    """

    default_ontology, root, shortcode = _parse_xml(input_file=input_file, imgdir=imgdir)

    if not config.skip_iiif_validation:
        _validate_iiif_uris(root)

    auth = AuthenticationClientLive(server=creds.server, email=creds.user, password=creds.password)
    con = ConnectionLive(creds.server, auth)
    config = config.with_server_info(server=creds.server, shortcode=shortcode)

    ontology_client = OntologyClientLive(con=con, shortcode=shortcode, default_ontology=default_ontology)
    resources, permissions_lookup, stash = prepare_upload(root, ontology_client)

    clients = _get_live_clients(con, auth, creds, shortcode, imgdir)
    state = UploadState(resources, stash, config, permissions_lookup)

    return execute_upload(clients, state)


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


def _get_live_clients(
    con: Connection,
    auth: AuthenticationClient,
    creds: ServerCredentials,
    shortcode: str,
    imgdir: str,
) -> UploadClients:
    ingest_client: AssetClient
    ingest_client = DspIngestClientLive(creds.dsp_ingest_url, auth, shortcode, imgdir)
    project_client: ProjectClient = ProjectClientLive(con, shortcode)
    list_client: ListClient = ListClientLive(con, project_client.get_project_iri())
    return UploadClients(
        asset_client=ingest_client,
        project_client=project_client,
        list_client=list_client,
    )


def execute_upload(clients: UploadClients, upload_state: UploadState) -> bool:
    """Execute an upload from an upload state, and clean up afterwards.

    Args:
        clients: the clients needed for the upload
        upload_state: the initial state of the upload to execute

    Returns:
        True if all resources could be uploaded without errors; False if any resource could not be uploaded
    """
    _upload_resources(clients, upload_state)
    return _cleanup_upload(upload_state)


def prepare_upload(
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
    uris = [uri for node in root.iter(tag="iiif-uri") if (uri := node.text)]
    if problems := IIIFUriValidator(uris).validate():
        msg = problems.get_msg()
        warnings.warn(DspToolsUserWarning(msg))
        logger.warning(msg)


def _cleanup_upload(upload_state: UploadState) -> bool:
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
            print(f"See {WARNINGS_SAVEPATH} for more information\n")
            logger.warning(res_msg)
        if has_stash_failed:
            stash_msg = f"Could not reapply the following stash items: {upload_state.pending_stash}"
            print(f"\n{datetime.now()}: WARNING: {stash_msg}\n")
            print(f"See {WARNINGS_SAVEPATH} for more information\n")
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


def _upload_resources(clients: UploadClients, upload_state: UploadState) -> None:
    """
    Iterates through all resources and tries to upload them to DSP.
    If a temporary exception occurs, the action is repeated until success,
    and if a permanent exception occurs, the resource is skipped.

    Args:
        clients: the clients needed for the upload
        upload_state: the current state of the upload

    Raises:
        BaseException: in case of an unhandled exception during resource creation
        XmlUploadInterruptedError: if the number of resources created is equal to the interrupt_after value
    """
    project_iri = clients.project_client.get_project_iri()
    project_onto_dict = clients.project_client.get_ontology_name_dict()
    listnode_lookup = clients.list_client.get_list_node_id_to_iri_lookup()
    project_context = get_json_ld_context_for_project(project_onto_dict)
    namespaces = make_namespace_dict_from_onto_names(project_onto_dict)
    resource_create_client = ResourceCreateClient(
        con=clients.project_client.con,
        project_iri=project_iri,
        iri_resolver=upload_state.iri_resolver,
        jsonld_context=project_context,
        namespaces=namespaces,
        permissions_lookup=upload_state.permissions_lookup,
        listnode_lookup=listnode_lookup,
        media_previously_ingested=upload_state.config.media_previously_uploaded,
    )

    progress_bar = tqdm(upload_state.pending_resources.copy(), desc="Creating Resources", dynamic_ncols=True)
    try:
        for creation_attempts_of_this_round, resource in enumerate(progress_bar):
            _upload_one_resource(
                upload_state=upload_state,
                resource=resource,
                ingest_client=clients.asset_client,
                resource_create_client=resource_create_client,
                creation_attempts_of_this_round=creation_attempts_of_this_round,
            )
            progress_bar.set_description(f"Creating Resources (failed: {len(upload_state.failed_uploads)})")
        if upload_state.pending_stash:
            _upload_stash(upload_state, clients.project_client)
    except XmlUploadInterruptedError as err:
        _handle_upload_error(err, upload_state)


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


def _upload_stash(
    upload_state: UploadState,
    project_client: ProjectClient,
) -> None:
    if upload_state.pending_stash and upload_state.pending_stash.standoff_stash:
        upload_stashed_xml_texts(upload_state, project_client.con)
    context = get_json_ld_context_for_project(project_client.get_ontology_name_dict())
    if upload_state.pending_stash and upload_state.pending_stash.link_value_stash:
        upload_stashed_resptr_props(upload_state, project_client.con, context)


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
    except PermanentConnectionError as err:
        _handle_permanent_connection_error(err)
    except KeyboardInterrupt:
        _handle_keyboard_interrupt()

    iri = None
    try:
        iri = resource_create_client.create_resource(resource, media_info)
    except (PermanentTimeOutError, KeyboardInterrupt) as err:
        _handle_permanent_timeout_or_keyboard_interrupt(err, resource.res_id)
    except PermanentConnectionError as err:
        _handle_permanent_connection_error(err)
    except Exception as err:  # noqa: BLE001 (blind-except)
        err_msg = err.message if isinstance(err, BaseError) else None
        _handle_resource_creation_failure(resource, err_msg)

    try:
        _tidy_up_resource_creation_idempotent(upload_state, iri, resource)
        _interrupt_if_indicated(upload_state, creation_attempts_of_this_round)
    except KeyboardInterrupt:
        _tidy_up_resource_creation_idempotent(upload_state, iri, resource)
        _handle_keyboard_interrupt()


def _handle_permanent_connection_error(err: PermanentConnectionError) -> Never:
    msg = "Lost connection to DSP server, probably because the server is down. "
    msg += f"Please continue later with 'resume-xmlupload'. Reason for this failure: {err.message}"
    logger.error(msg)
    raise XmlUploadInterruptedError(msg) from None


def _handle_keyboard_interrupt() -> Never:
    warnings.warn(DspToolsUserWarning("xmlupload manually interrupted. Tidying up, then exit..."))
    msg = "xmlupload manually interrupted. Please continue later with 'resume-xmlupload'"
    raise XmlUploadInterruptedError(msg) from None


def _handle_permanent_timeout_or_keyboard_interrupt(
    err: PermanentTimeOutError | KeyboardInterrupt, res_id: str
) -> Never:
    warnings.warn(DspToolsUserWarning(f"{type(err).__name__}: Tidying up, then exit..."))
    msg = (
        f"There was a {type(err).__name__} while trying to create resource '{res_id}'.\n"
        f"It is unclear if the resource '{res_id}' was created successfully or not.\n"
        f"Please check manually in the DSP-APP or DB.\n"
        f"In case of successful creation, call 'resume-xmlupload' with the flag "
        f"'--skip-first-resource' to prevent duplication.\n"
        f"If not, a normal 'resume-xmlupload' can be started."
    )
    logger.error(msg)
    raise XmlUploadInterruptedError(msg) from None


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
            f"See {WARNINGS_SAVEPATH} for more information\n"
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
