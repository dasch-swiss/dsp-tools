import time

from loguru import logger

from dsp_tools.clients.authentication_client_live import AuthenticationClientLive
from dsp_tools.clients.migration_clients import ExportId
from dsp_tools.clients.migration_clients import ExportImportStatus
from dsp_tools.clients.migration_clients import MigrationExportClient
from dsp_tools.clients.migration_clients_live import MigrationExportClientLive
from dsp_tools.clients.project_client_live import ProjectClientLive
from dsp_tools.commands.migration.models import MigrationConfig
from dsp_tools.commands.migration.models import ServerInfo
from dsp_tools.error.exceptions import UnreachableCodeError
from dsp_tools.setup.ansi_colors import BACKGROUND_BOLD_RED
from dsp_tools.setup.ansi_colors import BOLD_GREEN
from dsp_tools.setup.ansi_colors import RESET_TO_DEFAULT

STATUS_CHECK_SLEEP_TIME = 60


def export(source_info: ServerInfo, config: MigrationConfig) -> tuple[bool, ExportId]:
    auth = AuthenticationClientLive(source_info.server, source_info.user, source_info.password)
    project_iri = ProjectClientLive(source_info.server, auth).get_project_iri(config.shortcode)
    client = MigrationExportClientLive(source_info.server, project_iri, auth)
    return _execute_export(client)


def _execute_export(client: MigrationExportClient) -> tuple[bool, ExportId]:
    start = "Starting Export of Project"
    logger.debug(start)
    print(start)
    export_id = client.post_export()
    logger.info(f"Export ID of project: {export_id.id_}")
    return _check_export_progress(client, export_id), export_id


def _check_export_progress(client: MigrationExportClient, export_id: ExportId) -> bool:
    status_start_msg = f"Start checking export status for the export with the id {export_id.id_}."
    logger.debug(status_start_msg)
    print(BOLD_GREEN, status_start_msg, RESET_TO_DEFAULT)
    while True:
        status_check = client.get_status(export_id)
        match status_check:
            case ExportImportStatus.IN_PROGRESS:
                logger.debug(f"Export in progress, sleep {STATUS_CHECK_SLEEP_TIME}")
                time.sleep(STATUS_CHECK_SLEEP_TIME)
            case ExportImportStatus.COMPLETED:
                completed = "Export completed."
                logger.info(completed)
                print(completed)
                return True
            case ExportImportStatus.FAILED:
                err_msg = (
                    "EXPORT FAILED. Contact the DSP Engineering Team for help.\n"
                    "Please note, that the export history was not cleared on the server. "
                    "It will not be possible to start a new export until the history has been erased."
                )
                logger.error(err_msg)
                print(BACKGROUND_BOLD_RED, err_msg, RESET_TO_DEFAULT)
                return False
            case _:
                raise UnreachableCodeError()
