import time
import warnings
from typing import Never

from loguru import logger

from dsp_tools.commands.ingest_xmlupload.bulk_import.payload_files import PayloadFiles
from dsp_tools.commands.ingest_xmlupload.bulk_import.payload_files import delete_payload_files
from dsp_tools.commands.ingest_xmlupload.exceptions import BulkImportExistsError
from dsp_tools.commands.ingest_xmlupload.exceptions import BulkImportNotEnabledError
from dsp_tools.commands.ingest_xmlupload.exceptions import BulkImportPreconditionError
from dsp_tools.commands.ingest_xmlupload.exceptions import BulkImportRunningError
from dsp_tools.commands.ingest_xmlupload.exceptions import BulkImportStatusUnknownError
from dsp_tools.commands.ingest_xmlupload.exceptions import OnBehalfOfUserMissingError
from dsp_tools.commands.ingest_xmlupload.exceptions import OnBehalfOfUserRejectedError
from dsp_tools.commands.ingest_xmlupload.exceptions import PayloadSendConnectionLostError
from dsp_tools.commands.ingest_xmlupload.exceptions import PayloadTooLargeError
from dsp_tools.commands.ingest_xmlupload.exceptions import SystemAdminRequiredError
from dsp_tools.commands.ingest_xmlupload.exceptions import describe_task_left_on_server
from dsp_tools.commands.xmlupload.upload_config import DiagnosticsConfig
from dsp_tools.commands.xmlupload.write_diagnostic_info import write_id2iri_mapping
from dsp_tools.error.custom_warnings import DspToolsUserWarning
from dsp_tools.utils.spinners import get_green_bouncy_ball_spinner
from dsp_vre.clients.data_import_client import DataImportClient
from dsp_vre.clients.data_import_client import DataImportId
from dsp_vre.clients.data_import_client import DataImportStatus
from dsp_vre.clients.data_import_client import DataImportStatusValue
from dsp_vre.clients.exceptions import BadCredentialsError
from dsp_vre.clients.exceptions import DataImportExistsError
from dsp_vre.clients.exceptions import DataImportNotEnabledError
from dsp_vre.clients.exceptions import DataImportPayloadTooLargeError
from dsp_vre.clients.exceptions import DataImportPreconditionError
from dsp_vre.clients.exceptions import DataImportRunningError
from dsp_vre.clients.exceptions import DspApiRequestError
from dsp_vre.clients.exceptions import DspVreBaseError
from dsp_vre.clients.exceptions import DspVreUserError
from dsp_vre.clients.exceptions import OnBehalfOfUserIneligibleError
from dsp_vre.clients.exceptions import OnBehalfOfUserNotFoundError


def run_import(
    client: DataImportClient,
    files: PayloadFiles,
    on_behalf_of_user: str,
    shortcode: str,
    id2iri_mapping: dict[str, str],
    diagnostics: DiagnosticsConfig,
    sleep_time: float = 5,
) -> bool:
    """
    Sends the payload file as bulk data import, waits until the server is done, and tidies up.
    The payload file and the minted mapping must already exist.

    Args:
        client: client of the bulk data import
        files: the files of this import
        on_behalf_of_user: email or username of the owner of the imported data
        shortcode: shortcode of the project
        id2iri_mapping: the minted mapping of internal IDs to IRIs
        diagnostics: where to write the mapping after a successful import
        sleep_time: seconds between two status requests

    Raises:
        UserError: if the server rejects the import, or the connection is lost while the import runs
        KeyboardInterrupt: if the user interrupts the import

    Returns:
        True if the import completed, False if it failed
    """
    import_id = _post(client, files, on_behalf_of_user, shortcode)
    status = _poll(client, import_id, files, shortcode, sleep_time)
    if status.status == DataImportStatusValue.COMPLETED:
        _on_completed(client, import_id, files, shortcode, id2iri_mapping, diagnostics)
        return True
    _on_failed(client, import_id, files, shortcode, status.error_message)
    return False


def _reraise_interrupt(msg: str) -> Never:
    warnings.warn(DspToolsUserWarning(msg))
    logger.exception(msg)
    raise KeyboardInterrupt(msg) from None


def _post(client: DataImportClient, files: PayloadFiles, on_behalf_of_user: str, shortcode: str) -> DataImportId:
    try:
        return client.post_import(files.payload, on_behalf_of_user)
    except DspVreUserError as err:
        logger.exception(err)
        mapped = _map_error(err, files, on_behalf_of_user, shortcode)
        delete_payload_files(files)
        raise mapped from None
    except DspApiRequestError as err:
        # The server may hold a task, so the files are kept.
        logger.exception(err)
        raise PayloadSendConnectionLostError(files.payload.stat().st_size) from None
    except KeyboardInterrupt:
        msg = (
            "The bulk data import was interrupted while the payload was sent. "
            "The server may hold a task. A new run reports it as an existing import with its ID.\n"
            f"The payload file is kept at: {files.payload}"
        )
        _reraise_interrupt(msg)


def _map_error(err: DspVreUserError, files: PayloadFiles, user: str, shortcode: str) -> Exception:  # noqa: PLR0911
    match err:
        case BadCredentialsError():
            return SystemAdminRequiredError("ingest-xmlupload")
        case OnBehalfOfUserNotFoundError():
            return OnBehalfOfUserMissingError(user)
        case OnBehalfOfUserIneligibleError():
            return OnBehalfOfUserRejectedError(user, err.reason)
        case DataImportPayloadTooLargeError():
            if err.size is not None and err.max_size is not None:
                return PayloadTooLargeError(err.size, err.max_size)
            return PayloadTooLargeError(files.payload.stat().st_size, None)
        case DataImportExistsError():
            return BulkImportExistsError(shortcode, err.import_id)
        case DataImportRunningError():
            return BulkImportRunningError()
        case DataImportPreconditionError():
            return BulkImportPreconditionError(err.error_code, err.message, files.payload.parent)
        case DataImportNotEnabledError():
            return BulkImportNotEnabledError()
        case _:
            return err


def _poll(
    client: DataImportClient, import_id: DataImportId, files: PayloadFiles, shortcode: str, sleep_time: float
) -> DataImportStatus:
    sp = get_green_bouncy_ball_spinner("Importing data")
    try:
        with sp:
            while True:
                status = client.get_status(import_id)
                match status.status:
                    case DataImportStatusValue.IN_PROGRESS:
                        logger.debug(f"Import in progress, sleep {sleep_time}")
                        time.sleep(sleep_time)
                    case DataImportStatusValue.COMPLETED:
                        sp.ok("✔")
                        return status
                    case DataImportStatusValue.FAILED:
                        sp.fail("✘")
                        return status
    except DspVreBaseError as err:
        logger.exception(err)
        raise BulkImportStatusUnknownError(str(err), shortcode, import_id.id_, files.payload, files.id2iri) from None
    except KeyboardInterrupt:
        msg = "The bulk data import was interrupted.\n" + describe_task_left_on_server(
            shortcode, import_id.id_, files.payload, files.id2iri
        )
        _reraise_interrupt(msg)


def _delete_task(client: DataImportClient, import_id: DataImportId, shortcode: str) -> None:
    try:
        client.delete_import(import_id)
    except DspVreBaseError as err:
        logger.exception(err)
        print(
            f"The bulk data import task '{import_id.id_}' could not be deleted from the server. "
            f"Remove it with: uvx dsp-tools delete-data-import {shortcode} {import_id.id_}"
        )


def _on_completed(
    client: DataImportClient,
    import_id: DataImportId,
    files: PayloadFiles,
    shortcode: str,
    id2iri_mapping: dict[str, str],
    diagnostics: DiagnosticsConfig,
) -> None:
    logger.info("Bulk data import completed.")
    write_id2iri_mapping(id2iri_mapping, shortcode, diagnostics)
    _delete_task(client, import_id, shortcode)
    delete_payload_files(files)


def _on_failed(
    client: DataImportClient,
    import_id: DataImportId,
    files: PayloadFiles,
    shortcode: str,
    error_message: str | None,
) -> None:
    logger.error(f"Bulk data import failed: {error_message}")
    try:
        files.error.write_text(error_message or "", encoding="utf-8")
        print(f"The bulk data import failed. The error message was written to {files.error}")
    finally:
        _delete_task(client, import_id, shortcode)
