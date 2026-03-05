from pathlib import Path

from loguru import logger
from yaspin import yaspin
from yaspin.spinners import Spinners

from dsp_tools.clients.authentication_client_live import AuthenticationClientLive
from dsp_tools.clients.exceptions import ProjectNotFoundError
from dsp_tools.clients.migration_clients import ExportId
from dsp_tools.clients.migration_clients import ImportId
from dsp_tools.clients.migration_clients_live import MigrationExportClientLive
from dsp_tools.clients.migration_clients_live import MigrationImportClientLive
from dsp_tools.commands.migration.config_file import parse_reference_json
from dsp_tools.commands.migration.models import MigrationConfig
from dsp_tools.commands.migration.models import MigrationInfo
from dsp_tools.commands.migration.models import ReferenceInfo
from dsp_tools.commands.migration.models import ServerInfo
from dsp_tools.setup.ansi_colors import BACKGROUND_BOLD_RED
from dsp_tools.setup.ansi_colors import RESET_TO_DEFAULT


def clean_up(info: MigrationInfo) -> bool:
    reference_info = parse_reference_json(info.config.reference_savepath)
    if not reference_info.project_iri:
        raise ProjectNotFoundError(
            f"The project IRI is not provided in the reference file at: {info.config.reference_savepath}. "
            f"It is required for this step."
        )
    return _execute_clean_up(info, reference_info)


def _execute_clean_up(info: MigrationInfo, reference_info: ReferenceInfo) -> bool:
    with yaspin(
        Spinners.bouncingBall,
        color="light_green",
        on_color="on_black",
        attrs=["bold", "blink"],
    ) as sp:
        start_msg = "Cleaning Up"
        logger.debug(start_msg)
        sp.text = start_msg
        _handle_source_server_clean_up(info.source, reference_info)
        _handle_target_server_clean_up(info.target, reference_info)
        handle_local_clean_up(info.config)
        logger.info("Clean-up finished")
        sp.ok("✔")
    return True


def _handle_source_server_clean_up(source_info: ServerInfo | None, reference_info: ReferenceInfo) -> None:
    if reference_info.export_id:
        if source_info is None:
            msg = (
                "An export id on the source server was provided. "
                "However, no source server info has been found in the config file. "
                "Clean-up on the server is not possible."
            )
            print(BACKGROUND_BOLD_RED + msg + RESET_TO_DEFAULT)
        else:
            logger.debug("Cleaning up source server.")
            _clean_up_source_server(source_info, reference_info.export_id, reference_info.project_iri)
    else:
        logger.debug("No export id found, skipping source server clean-up.")


def _clean_up_source_server(source_info: ServerInfo, export_id: ExportId, project_iri: str) -> None:
    auth = AuthenticationClientLive(source_info.server, source_info.user, source_info.password)
    client = MigrationExportClientLive(source_info.server, project_iri, auth)
    client.delete_export(export_id)


def _handle_target_server_clean_up(target_info: ServerInfo | None, reference_info: ReferenceInfo) -> None:
    if reference_info.import_id:
        if target_info is None:
            msg = (
                "An import id on the target server was provided. "
                "However, no target server info has been found in the config file. "
                "Clean-up on the server is not possible."
            )
            print(BACKGROUND_BOLD_RED + msg + RESET_TO_DEFAULT)
        else:
            logger.debug("Cleaning up target server.")
            _clean_up_target_server(target_info, reference_info.import_id, reference_info.project_iri)
    else:
        logger.debug("No import id found, skipping target server clean-up.")


def _clean_up_target_server(target_info: ServerInfo, import_id: ImportId, project_iri: str) -> None:
    auth = AuthenticationClientLive(target_info.server, target_info.user, target_info.password)
    client = MigrationImportClientLive(target_info.server, project_iri, auth)
    client.delete_import(import_id)


def handle_local_clean_up(config: MigrationConfig) -> None:
    if config.keep_local_export:
        logger.debug("Local clean-up is skipped because the user configured to keep the files.")
        return
    _delete_file_if_exists(config.export_savepath)
    _delete_file_if_exists(config.reference_savepath)


def _delete_file_if_exists(path: Path) -> None:
    if not path.exists():
        logger.warning(f"File not found, skipping deletion: {path}")
        return
    path.unlink()
    logger.debug(f"Deleted file: {path}")
