from typing import cast

from dsp_tools.clients.authentication_client_live import AuthenticationClientLive
from dsp_tools.clients.migration_clients_live import MigrationImportClientLive
from dsp_tools.commands.migration.clean_up import handle_local_clean_up
from dsp_tools.commands.migration.exceptions import MigrationImportFailureError
from dsp_tools.commands.migration.export_download import export_and_download
from dsp_tools.commands.migration.import_zip import execute_import
from dsp_tools.commands.migration.models import MigrationInfo
from dsp_tools.commands.migration.models import ServerInfo


def migration(migration_info: MigrationInfo) -> bool:
    project_iri = export_and_download(migration_info)

    _import(migration_info, project_iri)

    handle_local_clean_up(migration_info.config)
    return True


def _import(migration_info: MigrationInfo, project_iri: str) -> None:
    target_server = cast(ServerInfo, migration_info.target)
    auth = AuthenticationClientLive(target_server.server, target_server.user, target_server.password)
    import_client = MigrationImportClientLive(target_server.server, project_iri, auth)

    import_success, import_id = execute_import(import_client, migration_info.config)
    if not import_success:
        raise MigrationImportFailureError()

    import_client.delete_import(import_id)
