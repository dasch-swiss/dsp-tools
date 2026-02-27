import time

from loguru import logger
from yaspin import yaspin
from yaspin.spinners import Spinners

from dsp_tools.clients.authentication_client_live import AuthenticationClientLive
from dsp_tools.clients.migration_clients import ExportImportStatus
from dsp_tools.clients.migration_clients import ImportId
from dsp_tools.clients.migration_clients import MigrationImportClient
from dsp_tools.clients.migration_clients_live import MigrationImportClientLive
from dsp_tools.commands.migration.exceptions import ExportZipNotFoundError
from dsp_tools.commands.migration.models import MigrationConfig
from dsp_tools.commands.migration.models import ServerInfo
from dsp_tools.error.exceptions import UnreachableCodeError
from dsp_tools.setup.ansi_colors import BACKGROUND_BOLD_RED
from dsp_tools.setup.ansi_colors import RESET_TO_DEFAULT

STATUS_CHECK_SLEEP_TIME = 60


def import_zip(target_info: ServerInfo, config: MigrationConfig, project_iri: str) -> bool:
    auth = AuthenticationClientLive(target_info.server, target_info.user, target_info.password)
    client = MigrationImportClientLive(target_info.server, project_iri, auth)
    success, import_id = _execute_import(client, config)
    print(f"Import is completed, for further use refer to the ID: {import_id.id_}")
    return success


def _execute_import(client: MigrationImportClient, config: MigrationConfig) -> tuple[bool, ImportId]:
    logger.debug("Starting Import of Project")
    # TODO: change check
    if not config.export_savepath.exists():
        raise ExportZipNotFoundError(f"The export zip file does not exists at '{config.export_savepath}'.")
    import_id = client.post_import(config.export_savepath)
    logger.info(f"Import ID of project: {import_id.id_}")
    return _check_import_progress(client, import_id), import_id


def _check_import_progress(
    client: MigrationImportClient,
    import_id: ImportId,
    sleep_time: int = STATUS_CHECK_SLEEP_TIME,
) -> bool:
    with yaspin(
        Spinners.bouncingBall,
        color="light_green",
        on_color="on_black",
        attrs=["bold", "blink"],
    ) as sp:
        status_start_msg = "Importing project"
        logger.debug(status_start_msg)
        sp.text = status_start_msg
        while True:
            status_check = client.get_status(import_id)
            match status_check:
                case ExportImportStatus.IN_PROGRESS:
                    logger.debug(f"Import in progress, sleep {sleep_time}")
                    time.sleep(sleep_time)
                case ExportImportStatus.COMPLETED:
                    logger.info("Import completed.")
                    sp.ok("✔")
                    return True
                case ExportImportStatus.FAILED:
                    err_msg = (
                        "IMPORT FAILED. Contact the DSP Engineering Team for help.\n"
                        "Please note, that the import history was not cleared on the server. "
                        "It will not be possible to start a new import until the history has been erased."
                    )
                    logger.error(err_msg)
                    sp.write(f"{BACKGROUND_BOLD_RED}{err_msg}{RESET_TO_DEFAULT}")
                    return False
                case _:
                    raise UnreachableCodeError()
