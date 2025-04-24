from __future__ import annotations

import pickle
import sys
import warnings
from datetime import datetime
from pathlib import Path
from typing import Never

from loguru import logger
from rdflib import URIRef
from tqdm import tqdm

from dsp_tools.cli.args import ServerCredentials
from dsp_tools.clients.authentication_client import AuthenticationClient
from dsp_tools.clients.authentication_client_live import AuthenticationClientLive
from dsp_tools.clients.connection import Connection
from dsp_tools.clients.connection_live import ConnectionLive
from dsp_tools.clients.legal_info_client import LegalInfoClient
from dsp_tools.clients.legal_info_client_live import LegalInfoClientLive
from dsp_tools.commands.xmlupload.make_rdf_graph.make_resource_and_values import create_resource_with_values
from dsp_tools.commands.xmlupload.models.ingest import AssetClient
from dsp_tools.commands.xmlupload.models.ingest import DspIngestClientLive
from dsp_tools.commands.xmlupload.models.lookup_models import IRILookups
from dsp_tools.commands.xmlupload.models.processed.res import ProcessedResource
from dsp_tools.commands.xmlupload.models.upload_clients import UploadClients
from dsp_tools.commands.xmlupload.models.upload_state import UploadState
from dsp_tools.commands.xmlupload.prepare_xml_input.check_if_link_targets_exist import check_if_link_targets_exist
from dsp_tools.commands.xmlupload.prepare_xml_input.list_client import ListClient
from dsp_tools.commands.xmlupload.prepare_xml_input.list_client import ListClientLive
from dsp_tools.commands.xmlupload.prepare_xml_input.prepare_xml_input import get_processed_resources_for_upload
from dsp_tools.commands.xmlupload.prepare_xml_input.prepare_xml_input import get_stash_and_upload_order
from dsp_tools.commands.xmlupload.prepare_xml_input.read_validate_xml_file import check_if_bitstreams_exist
from dsp_tools.commands.xmlupload.prepare_xml_input.read_validate_xml_file import preliminary_validation_of_root
from dsp_tools.commands.xmlupload.project_client import ProjectClient
from dsp_tools.commands.xmlupload.project_client import ProjectClientLive
from dsp_tools.commands.xmlupload.resource_create_client import ResourceCreateClient
from dsp_tools.commands.xmlupload.stash.upload_stashed_resptr_props import upload_stashed_resptr_props
from dsp_tools.commands.xmlupload.stash.upload_stashed_xml_texts import upload_stashed_xml_texts
from dsp_tools.commands.xmlupload.upload_config import UploadConfig
from dsp_tools.commands.xmlupload.write_diagnostic_info import write_id2iri_mapping
from dsp_tools.config.logger_config import WARNINGS_SAVEPATH
from dsp_tools.error.custom_warnings import DspToolsFutureWarning
from dsp_tools.error.custom_warnings import DspToolsUserWarning
from dsp_tools.error.exceptions import BaseError
from dsp_tools.error.exceptions import PermanentConnectionError
from dsp_tools.error.exceptions import PermanentTimeOutError
from dsp_tools.error.exceptions import XmlUploadInterruptedError
from dsp_tools.utils.xml_parsing.parse_clean_validate_xml import parse_and_clean_xml_file


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
        InputError: in case of permanent network or software failure, or if the XML file is invalid
        InputError: in case of permanent network or software failure, or if the XML file is invalid

    Returns:
        True if all resources could be uploaded without errors; False if one of the resources could not be
        uploaded because there is an error in it
    """

    root = parse_and_clean_xml_file(input_file)
    shortcode = root.attrib["shortcode"]

    auth = AuthenticationClientLive(server=creds.server, email=creds.user, password=creds.password)
    con = ConnectionLive(creds.server, auth)
    config = config.with_server_info(server=creds.server, shortcode=shortcode)
    clients = _get_live_clients(con, auth, creds, shortcode, imgdir)

    check_if_bitstreams_exist(root, imgdir)
    preliminary_validation_of_root(root, con, config)
    processed_resources = get_processed_resources_for_upload(root, clients)
    check_if_link_targets_exist(processed_resources)
    sorted_resources, stash = get_stash_and_upload_order(processed_resources)
    state = UploadState(
        pending_resources=sorted_resources,
        pending_stash=stash,
        config=config,
    )

    return execute_upload(clients, state)


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
    legal_info_client: LegalInfoClient = LegalInfoClientLive(creds.server, shortcode, auth)
    return UploadClients(
        asset_client=ingest_client,
        project_client=project_client,
        list_client=list_client,
        legal_info_client=legal_info_client,
    )


def execute_upload(clients: UploadClients, upload_state: UploadState) -> bool:
    """Execute an upload from an upload state, and clean up afterwards.

    Args:
        clients: the clients needed for the upload
        upload_state: the initial state of the upload to execute

    Returns:
        True if all resources could be uploaded without errors; False if any resource could not be uploaded
    """
    _warn_about_future_mandatory_legal_info(upload_state.pending_resources)
    _upload_copyright_holders(upload_state.pending_resources, clients.legal_info_client)
    _upload_resources(clients, upload_state)
    return _cleanup_upload(upload_state)


def _warn_about_future_mandatory_legal_info(resources: list[ProcessedResource]) -> None:
    missing_info = []
    counter = 0
    for res in resources:
        if res.file_value:
            counter += 1
            if not res.file_value.metadata.all_legal_info():
                missing_info.append(res.file_value.value)
        elif res.iiif_uri:
            counter += 1
            if not res.iiif_uri.metadata.all_legal_info():
                missing_info.append(res.iiif_uri.value)
    if counter == 0 or not missing_info:
        return None
    if len(missing_info) == counter:
        number = "All"
    else:
        number = f"{len(missing_info)} of {counter}"
    msg = (
        f"{number} bitstreams and iiif-uris in your XML are lacking the legal info "
        f"(copyright holders, license and authorship). "
        "Soon this information will be mandatory for all files."
    )
    if len(missing_info) < 100:
        msg += f" The following files are affected:\n-   {'\n-   '.join(missing_info)}"
    warnings.warn(DspToolsFutureWarning(msg))


def _upload_copyright_holders(resources: list[ProcessedResource], legal_info_client: LegalInfoClient) -> None:
    copyright_holders = _get_copyright_holders(resources)
    legal_info_client.post_copyright_holders(copyright_holders)


def _get_copyright_holders(resources: list[ProcessedResource]) -> list[str]:
    copyright_holders = set()
    for res in resources:
        if res.file_value:
            copyright_holders.add(res.file_value.metadata.copyright_holder)
        elif res.iiif_uri:
            copyright_holders.add(res.iiif_uri.metadata.copyright_holder)
    return [x for x in copyright_holders if x]


def _cleanup_upload(upload_state: UploadState) -> bool:
    """
    Write the id2iri mapping to a file and print a message to the console.

    Args:
        upload_state: the current state of the upload

    Returns:
        success status (deduced from failed_uploads and non-applied stash)
    """
    write_id2iri_mapping(
        upload_state.iri_resolver.lookup, upload_state.config.shortcode, upload_state.config.diagnostics
    )
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

    iri_lookup = IRILookups(
        project_iri=URIRef(project_iri),
        id_to_iri=upload_state.iri_resolver,
    )

    resource_create_client = ResourceCreateClient(
        con=clients.project_client.con,
    )
    progress_bar = tqdm(upload_state.pending_resources.copy(), desc="Creating Resources", dynamic_ncols=True)
    try:
        for creation_attempts_of_this_round, resource in enumerate(progress_bar):
            _upload_one_resource(
                upload_state=upload_state,
                resource=resource,
                ingest_client=clients.asset_client,
                resource_create_client=resource_create_client,
                iri_lookups=iri_lookup,
                creation_attempts_of_this_round=creation_attempts_of_this_round,
            )
            progress_bar.set_description(f"Creating Resources (failed: {len(upload_state.failed_uploads)})")
        if upload_state.pending_stash:
            _upload_stash(upload_state, clients.project_client)
    except XmlUploadInterruptedError as err:
        _handle_upload_error(err, upload_state)


def _upload_stash(
    upload_state: UploadState,
    project_client: ProjectClient,
) -> None:
    if upload_state.pending_stash and upload_state.pending_stash.standoff_stash:
        upload_stashed_xml_texts(upload_state, project_client.con)
    if upload_state.pending_stash and upload_state.pending_stash.link_value_stash:
        upload_stashed_resptr_props(upload_state, project_client.con)


def _upload_one_resource(
    upload_state: UploadState,
    resource: ProcessedResource,
    ingest_client: AssetClient,
    resource_create_client: ResourceCreateClient,
    iri_lookups: IRILookups,
    creation_attempts_of_this_round: int,
) -> None:
    media_info = None
    if resource.file_value:
        try:
            ingest_result = ingest_client.get_bitstream_info(resource.file_value)
        except PermanentConnectionError as err:
            _handle_permanent_connection_error(err)
        except KeyboardInterrupt:
            _handle_keyboard_interrupt()
        if not ingest_result:
            upload_state.failed_uploads.append(resource.res_id)
            return
        media_info = ingest_result

    iri = None
    try:
        serialised_resource = create_resource_with_values(
            resource=resource, bitstream_information=media_info, lookups=iri_lookups
        )
        logger.info(f"Attempting to create resource {resource.res_id} (label: {resource.label})...")
        iri = resource_create_client.create_resource(serialised_resource, bool(media_info))
    except (PermanentTimeOutError, KeyboardInterrupt) as err:
        _handle_permanent_timeout_or_keyboard_interrupt(err, resource.res_id)
    except PermanentConnectionError as err:
        _handle_permanent_connection_error(err)
    except Exception as err:  # noqa: BLE001 (blind-except)
        err_msg = err.message if isinstance(err, BaseError) else None
        _inform_about_resource_creation_failure(resource, err_msg)

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
    msg += f"\nSee {WARNINGS_SAVEPATH} for more information."
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
    resource: ProcessedResource,
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


def _inform_about_resource_creation_failure(resource: ProcessedResource, err_msg: str | None) -> None:
    log_msg = f"Unable to create resource '{resource.label}' ({resource.res_id})\n"
    if err_msg:
        log_msg += err_msg
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
        logger.error(msg)
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
