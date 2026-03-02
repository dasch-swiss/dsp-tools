import time
from pathlib import Path

from loguru import logger
from yaspin import yaspin
from yaspin.spinners import Spinners

from dsp_tools.clients.authentication_client_live import AuthenticationClientLive
from dsp_tools.clients.migration_clients import ExportId
from dsp_tools.clients.migration_clients import ExportImportStatus
from dsp_tools.clients.migration_clients import MigrationExportClient
from dsp_tools.clients.migration_clients_live import MigrationExportClientLive
from dsp_tools.clients.project_client_live import ProjectClientLive
from dsp_tools.commands.migration.config_file import write_or_update_reference_json
from dsp_tools.commands.migration.models import MigrationConfig
from dsp_tools.commands.migration.models import ServerInfo
from dsp_tools.error.exceptions import UnreachableCodeError
from dsp_tools.setup.ansi_colors import BACKGROUND_BOLD_RED
from dsp_tools.setup.ansi_colors import RESET_TO_DEFAULT

STATUS_CHECK_SLEEP_TIME = 60


def export(source_info: ServerInfo, config: MigrationConfig) -> bool:
    auth = AuthenticationClientLive(source_info.server, source_info.user, source_info.password)
    project_iri = ProjectClientLive(source_info.server, auth).get_project_iri(config.shortcode)
    client = MigrationExportClientLive(source_info.server, project_iri, auth)
    success, _ = _execute_export(client, config.reference_savepath)
    return success


def _execute_export(client: MigrationExportClient, reference_path: Path) -> tuple[bool, ExportId]:
    logger.debug("Starting Export of Project")
    export_id = client.post_export()
    logger.info(f"Export ID of project: {export_id.id_}")
    write_or_update_reference_json(reference_path, export_id=export_id)
    return _check_export_progress(client, export_id), export_id


def _check_export_progress(
    client: MigrationExportClient,
    export_id: ExportId,
    sleep_time: int = STATUS_CHECK_SLEEP_TIME,
) -> bool:
    with yaspin(
        Spinners.bouncingBall,
        color="light_green",
        on_color="on_black",
        attrs=["bold", "blink"],
    ) as sp:
        status_start_msg = "Exporting project"
        logger.debug(status_start_msg)
        sp.text = status_start_msg
        while True:
            status_check = client.get_status(export_id)
            match status_check:
                case ExportImportStatus.IN_PROGRESS:
                    logger.debug(f"Export in progress, sleep {sleep_time}")
                    time.sleep(sleep_time)
                case ExportImportStatus.COMPLETED:
                    logger.info("Export completed.")
                    sp.ok("✔")
                    return True
                case ExportImportStatus.FAILED:
                    err_msg = (
                        "EXPORT FAILED. Contact the DSP Engineering Team for help.\n"
                        "Please note, that the export history was not cleared on the server. "
                        "It will not be possible to start a new export until the history has been erased."
                    )
                    logger.error(err_msg)
                    sp.write(f"{BACKGROUND_BOLD_RED}{err_msg}{RESET_TO_DEFAULT}")
                    return False
                case _:
                    raise UnreachableCodeError()
