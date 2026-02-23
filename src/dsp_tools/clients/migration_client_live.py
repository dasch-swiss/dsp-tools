from dsp_tools.clients.authentication_client import AuthenticationClient
from dsp_tools.clients.migration_client import ExportImportStatus
from dsp_tools.clients.migration_client import MigrationExportClient
from dsp_tools.clients.migration_client import MigrationImportClient


class MigrationExportClientLive(MigrationExportClient):
    server: str
    project_iri: str
    auth: AuthenticationClient

    def post_export(self) -> str:
        """{self.server}/v3/projects/{projectIri}/exports"""

    def get_status(self, export_id: str) -> ExportImportStatus:
        """{self.server}/v3/projects/{projectIri}/exports/{exportId}"""

    def get_download(self, export_id: str) -> None:
        """{self.server}/v3/projects/{projectIri}/exports/{exportId}/download"""

    def delete_export(self) -> None:
        """{self.server}/v3/projects/{projectIri}/exports/{exportId}"""


class MigrationImportClientLive(MigrationImportClient):
    server: str
    project_iri: str
    auth: AuthenticationClient

    def post_import(self) -> str:
        """{self.server}/v3/projects/{projectIri}/imports"""

    def get_status(self, import_id: str) -> ExportImportStatus:
        """{self.server}/v3/projects/{projectIri}/imports/{importId}"""

    def delete_import(self, import_id: str) -> None:
        """{self.server}/v3/projects/{projectIri}/imports/{importId}"""
