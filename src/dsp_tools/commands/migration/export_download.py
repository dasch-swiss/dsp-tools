import time
from pathlib import Path
from typing import cast

from loguru import logger
from yaspin import yaspin
from yaspin.spinners import Spinners

from dsp_tools.clients.authentication_client_live import AuthenticationClientLive
from dsp_tools.clients.migration_clients import ExportId
from dsp_tools.clients.migration_clients import ExportImportStatus
from dsp_tools.clients.migration_clients import MigrationExportClient
from dsp_tools.clients.migration_clients_live import MigrationExportClientLive
from dsp_tools.clients.project_client_live import ProjectClientLive
from dsp_tools.commands.migration.config_file import parse_reference_json
from dsp_tools.commands.migration.config_file import write_or_update_reference_json
from dsp_tools.commands.migration.exceptions import MigrationDownloadFailureError
from dsp_tools.commands.migration.exceptions import MigrationExportFailureError
from dsp_tools.commands.migration.exceptions import MigrationReferenceInfoIncomplete
from dsp_tools.commands.migration.models import MigrationConfig
from dsp_tools.commands.migration.models import MigrationInfo
from dsp_tools.commands.migration.models import ServerInfo
from dsp_tools.error.exceptions import UnreachableCodeError
from dsp_tools.setup.ansi_colors import BACKGROUND_BOLD_RED
from dsp_tools.setup.ansi_colors import RESET_TO_DEFAULT

STATUS_CHECK_SLEEP_TIME = 5


def export_and_download(migration_info: MigrationInfo) -> str:
    source_server = cast(ServerInfo, migration_info.source)
    auth = AuthenticationClientLive(source_server.server, source_server.user, source_server.password)
    project_iri = ProjectClientLive(source_server.server, auth).get_project_iri(migration_info.config.shortcode)
    export_client = MigrationExportClientLive(source_server.server, project_iri, auth)

    export_success, export_id = _execute_export(export_client, migration_info.config.reference_savepath)
    if not export_success:
        raise MigrationExportFailureError()

    download_success = _execute_download(export_client, export_id, migration_info.config)
    if not download_success:
        raise MigrationDownloadFailureError()

    export_client.delete_export(export_id)

    return project_iri


def _execute_export(client: MigrationExportClient, reference_path: Path) -> tuple[bool, ExportId]:
    logger.debug("Starting Export of Project")
    export_id = client.post_export()
    logger.info(f"Export ID of project: {export_id.id_}")
    write_or_update_reference_json(reference_path, export_id=export_id, project_iri=client.project_iri)
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


def download(source_info: ServerInfo, config: MigrationConfig) -> bool:
    reference_info = parse_reference_json(config.reference_savepath)
    if reference_info.export_id is None or reference_info.export_id is None:
        raise MigrationReferenceInfoIncomplete("export_id and project_iri")
    auth = AuthenticationClientLive(source_info.server, source_info.user, source_info.password)
    client = MigrationExportClientLive(source_info.server, reference_info.project_iri, auth)
    success = _execute_download(client, reference_info.export_id, config)
    client.delete_export(reference_info.export_id)
    return success


def _execute_download(client: MigrationExportClient, export_id: ExportId, config: MigrationConfig) -> bool:
    write_or_update_reference_json(config.reference_savepath, project_iri=client.project_iri)
    with yaspin(
        Spinners.bouncingBall,
        color="light_green",
        on_color="on_black",
        attrs=["bold", "blink"],
    ) as sp:
        status_start_msg = "Downloading project"
        logger.debug(status_start_msg)
        sp.text = status_start_msg
        client.get_download(export_id, config.export_savepath)
        logger.info("Download completed.")
        sp.ok("✔")
    return True
