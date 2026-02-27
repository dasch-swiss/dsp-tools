from loguru import logger
from yaspin import yaspin
from yaspin.spinners import Spinners

from dsp_tools.clients.authentication_client_live import AuthenticationClientLive
from dsp_tools.clients.migration_clients import ExportId
from dsp_tools.clients.migration_clients import MigrationExportClient
from dsp_tools.clients.migration_clients_live import MigrationExportClientLive
from dsp_tools.clients.project_client_live import ProjectClientLive
from dsp_tools.commands.migration.exceptions import ExportZipExistsError
from dsp_tools.commands.migration.models import MigrationConfig
from dsp_tools.commands.migration.models import ServerInfo


def download(source_info: ServerInfo, config: MigrationConfig, export_id: ExportId) -> bool:
    auth = AuthenticationClientLive(source_info.server, source_info.user, source_info.password)
    project_iri = ProjectClientLive(source_info.server, auth).get_project_iri(config.shortcode)
    client = MigrationExportClientLive(source_info.server, project_iri, auth)
    success = _execute_download(client, export_id, config)
    msg = f"Download is completed, for the import refer to the project IRI: {project_iri}"
    logger.info(msg)
    print(msg)
    return success


def _execute_download(client: MigrationExportClient, export_id: ExportId, config: MigrationConfig) -> bool:
    # TODO: change check
    if config.export_savepath.exists():
        raise ExportZipExistsError(
            f"The export zip file already exists at '{config.export_savepath}'. Either rename or delete it."
        )
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
