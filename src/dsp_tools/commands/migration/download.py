from loguru import logger
from yaspin import yaspin
from yaspin.spinners import Spinners

from dsp_tools.clients.authentication_client_live import AuthenticationClientLive
from dsp_tools.clients.migration_clients import ExportId
from dsp_tools.clients.migration_clients import MigrationExportClient
from dsp_tools.clients.migration_clients_live import MigrationExportClientLive
from dsp_tools.clients.project_client_live import ProjectClientLive
from dsp_tools.commands.migration.config_file import parse_reference_json
from dsp_tools.commands.migration.config_file import write_or_update_reference_json
from dsp_tools.commands.migration.exceptions import MigrationReferenceInfoIncomplete
from dsp_tools.commands.migration.models import MigrationConfig
from dsp_tools.commands.migration.models import ServerInfo


def download(source_info: ServerInfo, config: MigrationConfig) -> bool:
    reference_info = parse_reference_json(config.reference_savepath)
    if not reference_info.export_id:
        raise MigrationReferenceInfoIncomplete("export_id")
    auth = AuthenticationClientLive(source_info.server, source_info.user, source_info.password)
    project_iri = ProjectClientLive(source_info.server, auth).get_project_iri(config.shortcode)
    client = MigrationExportClientLive(source_info.server, project_iri, auth)
    return execute_download(client, reference_info.export_id, config)


def execute_download(client: MigrationExportClient, export_id: ExportId, config: MigrationConfig) -> bool:
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
