from dsp_tools.clients.authentication_client import AuthenticationClient
from dsp_tools.clients.migration_client import ExportImportStatus
from dsp_tools.clients.migration_client import MigrationExportClient
from dsp_tools.clients.migration_client import MigrationImportClient

STATUS_MAPPER = {
    "in_progress": ExportImportStatus.IN_PROGRESS,
    "completed": ExportImportStatus.COMPLETED,
    "failed": ExportImportStatus.FAILED,
}



class MigrationExportClientLive(MigrationExportClient):
    server: str
    project_iri: str
    auth: AuthenticationClient

    def post_export(self) -> str:
        """
        {self.server}/v3/projects/{projectIri}/exports
        Status good: 202

        """

    def get_status(self, export_id: str) -> ExportImportStatus:
        """{self.server}/v3/projects/{projectIri}/exports/{exportId}
        Status good: 200"""

    def get_download(self, export_id: str) -> None:
        """{self.server}/v3/projects/{projectIri}/exports/{exportId}/download
        Status good: 200"""

    def delete_export(self) -> None:
        """{self.server}/v3/projects/{projectIri}/exports/{exportId}
        Status good: 204"""


class MigrationImportClientLive(MigrationImportClient):
    server: str
    project_iri: str
    auth: AuthenticationClient

    def post_import(self) -> str:
        """{self.server}/v3/projects/{projectIri}/imports
        Status good: 202"""

    def get_status(self, import_id: str) -> ExportImportStatus:
        """{self.server}/v3/projects/{projectIri}/imports/{importId}
        Status good: 200"""

    def delete_import(self, import_id: str) -> None:
        """{self.server}/v3/projects/{projectIri}/imports/{importId}
        Status good: 204"""
