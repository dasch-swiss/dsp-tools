from __future__ import annotations

from datetime import datetime

from loguru import logger
from rdflib import URIRef
from requests import ReadTimeout
from tqdm import tqdm

from dsp_tools.clients.connection import Connection
from dsp_tools.clients.connection_live import ConnectionLive
from dsp_tools.clients.fuseki_metrics import FusekiMetrics
from dsp_tools.clients.ingest import AssetClient
from dsp_tools.clients.legal_info_client import LegalInfoClient
from dsp_tools.clients.project_client_live import ProjectClientLive
from dsp_tools.clients.resource_client import ResourceClient
from dsp_tools.clients.resource_client_live import ResourceClientLive
from dsp_tools.commands.xmlupload.exceptions import XmlUploadInterruptedError
from dsp_tools.commands.xmlupload.handle_errors import handle_keyboard_interrupt
from dsp_tools.commands.xmlupload.handle_errors import handle_permanent_connection_error
from dsp_tools.commands.xmlupload.handle_errors import handle_permanent_timeout_or_keyboard_interrupt
from dsp_tools.commands.xmlupload.handle_errors import handle_upload_error
from dsp_tools.commands.xmlupload.handle_errors import inform_about_resource_creation_failure
from dsp_tools.commands.xmlupload.handle_errors import interrupt_if_indicated
from dsp_tools.commands.xmlupload.handle_errors import save_upload_state
from dsp_tools.commands.xmlupload.handle_errors import tidy_up_resource_creation_idempotent
from dsp_tools.commands.xmlupload.make_rdf_graph.jsonld_utils import serialise_jsonld_for_resource
from dsp_tools.commands.xmlupload.make_rdf_graph.make_resource_and_values import create_resource_with_values
from dsp_tools.commands.xmlupload.models.bitstream_info import BitstreamInfo
from dsp_tools.commands.xmlupload.models.lookup_models import IRILookups
from dsp_tools.commands.xmlupload.models.processed.res import ProcessedResource
from dsp_tools.commands.xmlupload.models.upload_clients import UploadClients
from dsp_tools.commands.xmlupload.models.upload_state import UploadState
from dsp_tools.commands.xmlupload.stash.upload_stashed_resptr_props import upload_stashed_resptr_props
from dsp_tools.commands.xmlupload.stash.upload_stashed_xml_texts import upload_stashed_xml_texts
from dsp_tools.commands.xmlupload.write_diagnostic_info import write_id2iri_mapping
from dsp_tools.error.exceptions import BadCredentialsError
from dsp_tools.error.exceptions import BaseError
from dsp_tools.error.exceptions import PermanentConnectionError
from dsp_tools.setup.ansi_colors import BOLD_YELLOW
from dsp_tools.setup.ansi_colors import RESET_TO_DEFAULT
from dsp_tools.setup.logger_config import WARNINGS_SAVEPATH
from dsp_tools.utils.exceptions import DspToolsRequestException
from dsp_tools.utils.fuseki_bloating import communicate_fuseki_bloating
from dsp_tools.utils.request_utils import log_request_failure_and_sleep
from dsp_tools.utils.request_utils import should_retry_request
from dsp_tools.utils.xml_parsing.models.parsed_resource import ParsedResource


def execute_upload(clients: UploadClients, upload_state: UploadState) -> bool:
    """Execute an upload from an upload state, and clean up afterwards.

    Args:
        clients: the clients needed for the upload
        upload_state: the initial state of the upload to execute

    Returns:
        True if all resources could be uploaded without errors; False if any resource could not be uploaded
    """
    logger.debug("Start uploading data")
    db_metrics = None
    if clients.legal_info_client.server == "http://0.0.0.0:3333":
        db_metrics = FusekiMetrics()
        db_metrics.try_get_start_size()
    upload_copyright_holders(upload_state.pending_resources, clients.legal_info_client)
    _upload_all_resources(clients, upload_state)
    if db_metrics is not None:
        db_metrics.try_get_end_size()
        communicate_fuseki_bloating(db_metrics)
    return cleanup_upload(upload_state)


def upload_copyright_holders(resources: list[ProcessedResource], legal_info_client: LegalInfoClient) -> None:
    logger.debug("Get and upload copyright holders")
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


def _upload_all_resources(clients: UploadClients, upload_state: UploadState) -> None:
    project_client = ProjectClientLive(clients.legal_info_client.server, clients.legal_info_client.auth)
    project_iri = project_client.get_project_iri(upload_state.config.shortcode)

    iri_lookup = IRILookups(
        project_iri=URIRef(project_iri),
        id_to_iri=upload_state.iri_resolver,
    )

    resource_client = ResourceClientLive(clients.legal_info_client.server, clients.legal_info_client.auth)

    progress_bar = tqdm(upload_state.pending_resources.copy(), desc="Creating Resources", dynamic_ncols=True)
    try:
        for creation_attempts_of_this_round, resource in enumerate(progress_bar):
            _execute_one_resource_upload(
                resource=resource,
                upload_state=upload_state,
                resource_client=resource_client,
                asset_client=clients.asset_client,
                iri_lookups=iri_lookup,
                creation_attempts_of_this_round=creation_attempts_of_this_round,
            )
            progress_bar.set_description(f"Creating Resources (failed: {len(upload_state.failed_uploads)})")
        if upload_state.pending_stash:
            con = ConnectionLive(clients.legal_info_client.server, clients.legal_info_client.auth)
            _upload_stash(upload_state, con)
    except XmlUploadInterruptedError as err:
        handle_upload_error(err, upload_state)


def _execute_one_resource_upload(
    resource: ProcessedResource,
    upload_state: UploadState,
    resource_client: ResourceClient,
    asset_client: AssetClient,
    iri_lookups: IRILookups,
    creation_attempts_of_this_round: int,
) -> None:
    media_info = None
    if resource.file_value:
        try:
            ingest_result = asset_client.get_bitstream_info(resource.file_value)
        except PermanentConnectionError as err:
            handle_permanent_connection_error(err)
        except KeyboardInterrupt:
            handle_keyboard_interrupt()
        if not ingest_result:
            upload_state.failed_uploads.append(resource.res_id)
            return
        media_info = ingest_result

    iri = None
    try:
        iri = _execute_one_resource_data_upload(resource, media_info, resource_client, iri_lookups)
    except (TimeoutError, ReadTimeout, KeyboardInterrupt) as err:
        handle_permanent_timeout_or_keyboard_interrupt(err, resource.res_id)
    except PermanentConnectionError as err:
        handle_permanent_connection_error(err)
    except Exception as err:  # noqa: BLE001 (blind-except)
        err_msg = err.message if isinstance(err, BaseError) else None
        inform_about_resource_creation_failure(resource, err_msg)

    try:
        tidy_up_resource_creation_idempotent(upload_state, iri, resource)
        interrupt_if_indicated(upload_state, creation_attempts_of_this_round)
    except KeyboardInterrupt:
        tidy_up_resource_creation_idempotent(upload_state, iri, resource)
        handle_keyboard_interrupt()


def _execute_one_resource_data_upload(
    resource: ProcessedResource,
    media_info: BitstreamInfo | None,
    resource_client: ResourceClient,
    iri_lookups: IRILookups,
) -> str | None:
    resource_graph = create_resource_with_values(
        resource=resource,
        bitstream_information=media_info,
        lookups=iri_lookups,
    )
    resource_dict = serialise_jsonld_for_resource(resource_graph)
    logger.info(f"Attempting to create resource {resource.res_id} (label: {resource.label})...")
    num_of_retries = 24
    for retry_counter in range(num_of_retries):
        try:
            creation_result = resource_client.post_resource(resource_dict, bool(media_info))
        except BadCredentialsError as err:
            raise err from None
        except DspToolsRequestException:
            log_request_failure_and_sleep("Connection Error", retry_counter, exc_info=True)
            continue
        if isinstance(creation_result, str):
            return creation_result
        if should_retry_request(creation_result):
            log_request_failure_and_sleep("Transient Error", retry_counter, exc_info=False)
            continue
        return None  # non-retryable error (4xx etc.)
    msg = f"Permanently unable to execute the network action. See {WARNINGS_SAVEPATH} for more information."
    raise PermanentConnectionError(msg)


def _upload_stash(
    upload_state: UploadState,
    con: Connection,
) -> None:
    if upload_state.pending_stash and upload_state.pending_stash.standoff_stash:
        upload_stashed_xml_texts(upload_state, con)
    if upload_state.pending_stash and upload_state.pending_stash.link_value_stash:
        upload_stashed_resptr_props(upload_state, con)


def cleanup_upload(upload_state: UploadState) -> bool:
    """
    Write the id2iri mapping to a file and print a message to the console.

    Args:
        upload_state: the current state of the upload

    Returns:
        success status (deduced from failed_uploads and non-applied stash)
    """
    write_id2iri_mapping(
        id2iri_mapping=upload_state.iri_resolver.lookup,
        shortcode=upload_state.config.shortcode,
        diagnostics=upload_state.config.diagnostics,
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
        msg = save_upload_state(upload_state)
        print(msg)

    upload_state.config.diagnostics.save_location.unlink(missing_ok=True)
    return success


def enable_unknown_license_if_any_are_missing(
    legal_info_client: LegalInfoClient, parsed_resources: list[ParsedResource]
) -> None:
    all_license_infos = [x.file_value.metadata.license_iri for x in parsed_resources if x.file_value]
    if not all(all_license_infos):
        legal_info_client.enable_unknown_license()
        msg = (
            "The files or iiif-uris in your data are missing some legal information. "
            "To facilitate an upload on a test environment we are adding dummy information.\n"
            "In order to be able to use the license 'unknown' in place of missing licenses, "
            "we are enabling it for your project."
        )
        print(BOLD_YELLOW, msg, RESET_TO_DEFAULT)
