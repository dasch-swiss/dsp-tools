from dsp_tools.clients.authentication_client_live import AuthenticationClientLive
from dsp_tools.clients.migration_clients import MigrationExportClient
from dsp_tools.clients.migration_clients import MigrationImportClient
from dsp_tools.clients.migration_clients_live import MigrationExportClientLive
from dsp_tools.clients.migration_clients_live import MigrationImportClientLive
from dsp_tools.clients.project_client_live import ProjectClientLive
from dsp_tools.commands.migration.download import execute_download
from dsp_tools.commands.migration.exceptions import MigrationDownloadFailureError
from dsp_tools.commands.migration.exceptions import MigrationExportFailureError
from dsp_tools.commands.migration.exceptions import MigrationImportFailureError
from dsp_tools.commands.migration.export import execute_export
from dsp_tools.commands.migration.import_zip import execute_import
from dsp_tools.commands.migration.models import MigrationConfig
from dsp_tools.commands.migration.models import MigrationInfo
from dsp_tools.commands.migration.models import ServerInfo


def migration(migration_info: MigrationInfo) -> bool:
    export_client = _get_export_client(migration_info.source, migration_info.config)

    export_success, export_id = execute_export(export_client, migration_info.config.reference_savepath)
    if not export_success:
        raise MigrationExportFailureError()

    download_success = execute_download(export_client, export_id, migration_info.config)
    if not download_success:
        raise MigrationDownloadFailureError()

    import_client = _get_import_client(migration_info.target, export_client.project_iri)

    import_success, import_id = execute_import(import_client, migration_info.config)
    if not import_success:
        raise MigrationImportFailureError()


def _get_export_client(source_info: ServerInfo, config: MigrationConfig) -> MigrationExportClient:
    auth = AuthenticationClientLive(source_info.server, source_info.user, source_info.password)
    project_iri = ProjectClientLive(source_info.server, auth).get_project_iri(config.shortcode)
    return MigrationExportClientLive(source_info.server, project_iri, auth)


def _get_import_client(target_info: ServerInfo, project_iri: str) -> MigrationImportClient:
    auth = AuthenticationClientLive(target_info.server, target_info.user, target_info.password)
    return MigrationImportClientLive(target_info.server, project_iri, auth)
