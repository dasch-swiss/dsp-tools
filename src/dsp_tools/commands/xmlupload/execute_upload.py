from http import HTTPStatus

from loguru import logger

from dsp_tools.clients.ingest import AssetClient
from dsp_tools.clients.resource_client import ResourceClient
from dsp_tools.commands.xmlupload.handle_errors import handle_keyboard_interrupt
from dsp_tools.commands.xmlupload.handle_errors import handle_permanent_connection_error
from dsp_tools.commands.xmlupload.handle_errors import handle_permanent_timeout_or_keyboard_interrupt
from dsp_tools.commands.xmlupload.handle_errors import inform_about_resource_creation_failure
from dsp_tools.commands.xmlupload.handle_errors import interrupt_if_indicated
from dsp_tools.commands.xmlupload.handle_errors import tidy_up_resource_creation_idempotent
from dsp_tools.commands.xmlupload.make_rdf_graph.jsonld_utils import serialise_jsonld_for_resource
from dsp_tools.commands.xmlupload.make_rdf_graph.make_resource_and_values import create_resource_with_values
from dsp_tools.commands.xmlupload.models.bitstream_info import BitstreamInfo
from dsp_tools.commands.xmlupload.models.lookup_models import IRILookups
from dsp_tools.commands.xmlupload.models.processed.res import ProcessedResource
from dsp_tools.commands.xmlupload.models.upload_state import UploadState
from dsp_tools.error.exceptions import BaseError
from dsp_tools.error.exceptions import PermanentConnectionError
from dsp_tools.error.exceptions import PermanentTimeOutError


def _execute_one_resource_upload(
    resource: ProcessedResource,
    upload_state: UploadState,
    resource_client: ResourceClient,
    ingest_client: AssetClient,
    iri_lookups: IRILookups,
    creation_attempts_of_this_round: int,
) -> None:
    media_info = None
    if resource.file_value:
        try:
            ingest_result = ingest_client.get_bitstream_info(resource.file_value)
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
        iri = _handle_one_resource_upload(resource, media_info, resource_client, iri_lookups, retry_count=0)
    except (PermanentTimeOutError, KeyboardInterrupt) as err:
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


def _handle_one_resource_upload(
    resource: ProcessedResource,
    media_info: BitstreamInfo | None,
    resource_client: ResourceClient,
    iri_lookups: IRILookups,
    retry_count: int,
) -> str | None:
    resource_graph = create_resource_with_values(
        resource=resource,
        bitstream_information=media_info,
        lookups=iri_lookups,
    )
    resource_dict = serialise_jsonld_for_resource(resource_graph)
    logger.info(f"Attempting to create resource {resource.res_id} (label: {resource.label})...")
    creation_result = resource_client.post_resource(resource_dict, bool(media_info))
    if isinstance(creation_result, str):
        return creation_result

    match creation_result.status_code:
        case HTTPStatus.INTERNAL_SERVER_ERROR | HTTPStatus.SERVICE_UNAVAILABLE | HTTPStatus.GATEWAY_TIMEOUT:
            if retry_count < 25:
                pass
                # TODO: here we must call itself again
        case _:
            # in any other cases we do not retry
            return None
