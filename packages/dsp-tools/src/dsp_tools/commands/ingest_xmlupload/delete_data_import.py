from pathlib import Path

from loguru import logger

from dsp_tools.cli.args import ServerCredentials
from dsp_tools.commands.ingest_xmlupload.bulk_import.payload_files import get_or_create_data_imports_folder
from dsp_tools.commands.ingest_xmlupload.exceptions import SystemAdminRequiredError
from dsp_tools.commands.xmlupload.upload_config import transform_server_url_to_foldername
from dsp_vre.clients.authentication_client_live import AuthenticationClientLive
from dsp_vre.clients.data_import_client import DataImportClient
from dsp_vre.clients.data_import_client import DataImportId
from dsp_vre.clients.data_import_client import DataImportStatusValue
from dsp_vre.clients.data_import_client_live import DataImportClientLive
from dsp_vre.clients.exceptions import BadCredentialsError
from dsp_vre.clients.exceptions import DataImportInProgressError
from dsp_vre.clients.exceptions import DataImportNotFoundError
from dsp_vre.clients.project_client_live import ProjectClientLive

COMMAND = "delete-data-import"


def delete_data_import(shortcode: str, import_id: str, creds: ServerCredentials) -> bool:
    """
    Deletes a bulk data import task from the server.
    A failed import's error message is written to the data imports folder first.

    Args:
        shortcode: shortcode of the project
        import_id: ID of the bulk data import
        creds: credentials for the DSP server

    Raises:
        SystemAdminRequiredError: if the login failed, or the user is not a system admin
        UserError: if the project does not exist, or the server rejects a request

    Returns:
        False if the import is still running, True otherwise
    """
    auth = AuthenticationClientLive(creds.server, creds.user, creds.password)
    project_iri = ProjectClientLive(creds.server, auth).get_project_iri(shortcode)
    client = DataImportClientLive(creds.server, project_iri, auth)
    error_folder = get_or_create_data_imports_folder(transform_server_url_to_foldername(creds.server))
    return _delete(client, shortcode, import_id, error_folder)


def _delete(client: DataImportClient, shortcode: str, import_id: str, error_folder: Path) -> bool:
    data_import_id = DataImportId(import_id)
    try:
        status = client.get_status(data_import_id)
        if status.status == DataImportStatusValue.IN_PROGRESS:
            _print_in_progress(import_id)
            return False
        if status.status == DataImportStatusValue.FAILED:
            _write_error_message(status.error_message, shortcode, import_id, error_folder)
        client.delete_import(data_import_id)
    except DataImportNotFoundError as err:
        logger.exception(err)
        print(f"The bulk data import '{import_id}' does not exist on the server. Nothing to delete.")
        return True
    except DataImportInProgressError as err:
        logger.exception(err)
        _print_in_progress(import_id)
        return False
    except BadCredentialsError as err:
        logger.exception(err)
        raise SystemAdminRequiredError(COMMAND) from None
    print(f"The bulk data import '{import_id}' was deleted from the server.")
    return True


def _print_in_progress(import_id: str) -> None:
    print(f"The bulk data import '{import_id}' is still running. A running import cannot be deleted.")


def _write_error_message(error_message: str | None, shortcode: str, import_id: str, error_folder: Path) -> None:
    target = error_folder / f"{shortcode}_{import_id}_error.txt"
    target.write_text(error_message or "", encoding="utf-8")
    print(f"The bulk data import failed. The error message was written to {target}")
