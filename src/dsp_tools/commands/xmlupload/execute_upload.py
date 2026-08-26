from __future__ import annotations

from datetime import datetime

from loguru import logger
from rdflib import URIRef
from requests import ReadTimeout
from tqdm import tqdm

from dsp_tools.clients.fuseki_metrics import FusekiMetrics
from dsp_tools.clients.ingest import AssetClient
from dsp_tools.clients.legal_info_client import LegalInfoClient
from dsp_tools.clients.project_client_live import ProjectClientLive
from dsp_tools.clients.resource_client import ResourceClient
from dsp_tools.clients.resource_client_live import ResourceClientLive
from dsp_tools.clients.value_client_live import ValueClientLive
from dsp_tools.commands.xmlupload.exceptions import XmlUploadInterruptedError
from dsp_tools.commands.xmlupload.handle_errors import handle_keyboard_interrupt
from dsp_tools.commands.xmlupload.handle_errors import handle_keyboard_interrupt_during_creation
from dsp_tools.commands.xmlupload.handle_errors import handle_permanent_connection_error
from dsp_tools.commands.xmlupload.handle_errors import handle_permanent_timeout
from dsp_tools.commands.xmlupload.handle_errors import inform_about_resource_creation_failure
from dsp_tools.commands.xmlupload.handle_errors import interruption_is_indicated
from dsp_tools.commands.xmlupload.handle_errors import persist_state_for_resume
from dsp_tools.commands.xmlupload.handle_errors import save_upload_state
from dsp_tools.commands.xmlupload.handle_errors import tidy_up_resource_creation_idempotent
from dsp_tools.commands.xmlupload.make_rdf_graph.jsonld_utils import serialise_jsonld_for_resource
from dsp_tools.commands.xmlupload.make_rdf_graph.make_resource_and_values import create_resource_with_values
from dsp_tools.commands.xmlupload.models.bitstream_info import BitstreamInfo
from dsp_tools.commands.xmlupload.models.lookup_models import IRILookups
from dsp_tools.commands.xmlupload.models.processed.file_values import ProcessedFileBitstream
from dsp_tools.commands.xmlupload.models.processed.res import ProcessedResource
from dsp_tools.commands.xmlupload.models.upload_clients import UploadClients
from dsp_tools.commands.xmlupload.models.upload_state import UploadState
from dsp_tools.commands.xmlupload.stash.upload_stashed_resptr_props import upload_stashed_resptr_props
from dsp_tools.commands.xmlupload.stash.upload_stashed_xml_texts import upload_stashed_xml_texts
from dsp_tools.commands.xmlupload.write_diagnostic_info import write_id2iri_mapping
from dsp_tools.error.exceptions import BadCredentialsError
from dsp_tools.error.exceptions import BaseError
from dsp_tools.error.exceptions import PermanentConnectionError
from dsp_tools.setup.logger_config import WARNINGS_SAVEPATH
from dsp_tools.utils.exceptions import DspToolsRequestException
from dsp_tools.utils.fuseki_bloating import communicate_fuseki_bloating
from dsp_tools.utils.request_utils import log_request_failure_and_sleep
from dsp_tools.utils.request_utils import should_retry_request


def execute_upload(clients: UploadClients, upload_state: UploadState) -> bool:
    """Execute an upload from an upload state, and clean up afterwards.

    Args:
        clients: the clients needed for the upload
        upload_state: the initial state of the upload to execute

    Returns:
        True if all resources could be uploaded without errors,
        or if the upload was interrupted as requested with '--interrupt-after';
        False if any resource could not be uploaded
    """
    logger.debug("Start uploading data")
    db_metrics = None
    if clients.legal_info_client.server == "http://0.0.0.0:3333":
        db_metrics = FusekiMetrics()
        db_metrics.try_get_start_size()
    upload_copyright_holders(upload_state.pending_resources, clients.legal_info_client)
    if _upload_all_resources(clients, upload_state):
        # the upload was interrupted as requested by the user: the state is saved, so it can be resumed
        return True
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
    return [x for x in copyright_holders if x]


def _upload_all_resources(clients: UploadClients, upload_state: UploadState) -> bool:
    """
    Create all pending resources, then re-apply the pending stash.

    Args:
        clients: the clients needed for the upload
        upload_state: the current state of the upload

    Raises:
        XmlUploadInterruptedError: if the connection to the DSP server was permanently lost
        BadCredentialsError: if the DSP server rejected the credentials
        KeyboardInterrupt: if the user interrupted the upload

    Returns:
        True if the upload was interrupted because the number of resources
        requested with '--interrupt-after' has been created
    """
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
            )
            progress_bar.set_description(f"Creating Resources (failed: {len(upload_state.failed_uploads)})")
            if interruption_is_indicated(upload_state, creation_attempts_of_this_round):
                _report_planned_interruption(upload_state)
                return True
        if upload_state.pending_stash:
            _upload_stash(upload_state, resource_client)
    except (XmlUploadInterruptedError, BadCredentialsError, KeyboardInterrupt):
        # the upload cannot continue, but it can be resumed later, so the state must be saved.
        # The error itself is reported and logged by entry_point.py.
        persist_state_for_resume(upload_state)
        raise
    return False


def _report_planned_interruption(upload_state: UploadState) -> None:
    msg = f"Interrupted: Maximum number of resources was reached ({upload_state.config.interrupt_after})"
    logger.info(msg)
    print(f"\n{datetime.now()}: {msg}")
    persist_state_for_resume(upload_state)


def _execute_one_resource_upload(
    resource: ProcessedResource,
    upload_state: UploadState,
    resource_client: ResourceClient,
    asset_client: AssetClient,
    iri_lookups: IRILookups,
) -> None:
    media_info = None
    if file_found := resource.file_value:
        if isinstance(file_found.value, ProcessedFileBitstream):
            try:
                ingest_result = asset_client.get_bitstream_info(file_found.value, file_found.metadata.permissions)
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
    except (TimeoutError, ReadTimeout) as err:
        handle_permanent_timeout(err, resource.res_id)
    except KeyboardInterrupt:
        handle_keyboard_interrupt_during_creation(resource.res_id)
    except PermanentConnectionError as err:
        handle_permanent_connection_error(err)
    except BadCredentialsError:
        # The credentials will not become valid by uploading the next resource, so the upload must stop.
        # The resource stays pending, so that 'resume-xmlupload' retries it once the credentials are fixed.
        raise
    except Exception as err:  # noqa: BLE001 (blind-except)
        err_msg = err.message if isinstance(err, BaseError) else None
        inform_about_resource_creation_failure(resource, err_msg)

    try:
        tidy_up_resource_creation_idempotent(upload_state, iri, resource)
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
        except DspToolsRequestException:
            # the traceback was already logged when the request exception was converted
            log_request_failure_and_sleep("Connection Error", retry_counter, exc_info=False)
            continue
        if isinstance(creation_result, str):
            return creation_result
        if should_retry_request(creation_result):
            log_request_failure_and_sleep("Transient Error", retry_counter, exc_info=False)
            continue
        return None  # non-retryable error (4xx etc.)
    msg = f"Permanently unable to execute the network action. See {WARNINGS_SAVEPATH} for more information."
    raise PermanentConnectionError(msg)


def _upload_stash(upload_state: UploadState, resource_client: ResourceClient) -> None:
    val_client = ValueClientLive(resource_client.server, resource_client.auth)
    if upload_state.pending_stash and upload_state.pending_stash.standoff_stash:
        upload_stashed_xml_texts(upload_state, val_client, resource_client)
    if upload_state.pending_stash and upload_state.pending_stash.link_value_stash:
        upload_stashed_resptr_props(upload_state, val_client)


def cleanup_upload(upload_state: UploadState) -> bool:
    """
    Write the id2iri mapping to a file and report the upload outcome to the console.

    The upload state (pickle file) is only persisted when the upload can actually be resumed,
    i.e. when there is a stash that could not be re-applied (resuming re-applies the pending stash).
    Failed uploads are not retried on resume, so on their own they do not produce a pickle file:
    they only produce a warning that points to the logs.

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
    has_failures = len(upload_state.failed_uploads) > 0
    has_stash = bool(upload_state.pending_stash and not upload_state.pending_stash.is_empty())

    if not has_failures and not has_stash:
        print(f"{datetime.now()}: All resources have successfully been uploaded.")
        logger.info("All resources have successfully been uploaded.")
        upload_state.config.diagnostics.save_location.unlink(missing_ok=True)
        return True

    _report_incomplete_upload(upload_state, has_failures=has_failures, has_stash=has_stash)
    return False


def _report_incomplete_upload(upload_state: UploadState, *, has_failures: bool, has_stash: bool) -> None:
    # A stash can be re-applied by 'resume-xmlupload', so it is worth persisting the upload state.
    # Failed uploads are not retried on resume, so they alone do not justify a pickle file.
    save_pickle = has_stash

    if has_failures:
        failed_msg = f"Could not upload the following resources: {upload_state.failed_uploads}"
        logger.warning(failed_msg)
        print(f"\n{datetime.now()}: WARNING: {failed_msg}\n")
    if has_stash and upload_state.pending_stash:
        # The console only gets the count; the resource/property combinations go to the log file,
        # which can hold the full (potentially long) list without cluttering the terminal.
        stash_items = upload_state.pending_stash.all_items()
        combinations = [f"{item.res_id} / {item.value.prop_iri}" for item in stash_items]
        logger.warning(f"Could not reapply the following stashed values (resource / property): {combinations}")
        print(
            f"\n{datetime.now()}: WARNING: Could not reapply {len(stash_items)} stashed values, "
            f"see log for detailed information.\n"
        )
    print(f"See {WARNINGS_SAVEPATH} for more information\n")

    if save_pickle:
        print(save_upload_state(upload_state))
    else:
        upload_state.config.diagnostics.save_location.unlink(missing_ok=True)
