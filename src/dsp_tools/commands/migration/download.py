from pathlib import Path

from dsp_tools.clients.authentication_client_live import AuthenticationClientLive
from dsp_tools.clients.migration_clients import ExportId
from dsp_tools.clients.migration_clients import MigrationExportClient
from dsp_tools.clients.migration_clients_live import MigrationExportClientLive
from dsp_tools.clients.project_client_live import ProjectClientLive
from dsp_tools.commands.migration.models import MigrationConfig
from dsp_tools.commands.migration.models import ServerInfo


def download(source_info: ServerInfo, config: MigrationConfig, export_id: ExportId) -> bool:
    auth = AuthenticationClientLive(source_info.server, source_info.user, source_info.password)
    project_iri = ProjectClientLive(source_info.server, auth).get_project_iri(config.shortcode)
    client = MigrationExportClientLive(source_info.server, project_iri, auth)
    return _execute_download(client, export_id, config.export_savepath)


def _execute_download(client: MigrationExportClient, export_id: ExportId, export_savepath: Path) -> bool:
    client.get_download(export_id, export_savepath)
    return True
