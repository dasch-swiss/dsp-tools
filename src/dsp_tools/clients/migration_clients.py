from dataclasses import dataclass
from enum import Enum
from enum import auto
from pathlib import Path
from typing import Protocol

from dsp_tools.clients.authentication_client import AuthenticationClient


class ExportImportStatus(Enum):
    IN_PROGRESS = auto()
    COMPLETED = auto()
    FAILED = auto()


@dataclass
class ExportId:
    id_: str


@dataclass
class MigrationExportClient(Protocol):
    server: str
    project_iri: str
    auth: AuthenticationClient

    def get_status(self, export_id: ExportId) -> ExportImportStatus:
        """Get the export status."""

    def post_export(self, skip_assets: bool) -> ExportId:
        """Start an export."""

    def get_download(self, export_id: ExportId, destination: Path) -> None:
        """Download the export ZIP to the specified file path."""

    def delete_export(self, export_id: ExportId) -> None:
        """Delete an export after completion or failure."""


@dataclass
class ImportId:
    id_: str


@dataclass
class MigrationImportClient(Protocol):
    server: str
    project_iri: str
    auth: AuthenticationClient

    def get_status(self, import_id: ImportId) -> ExportImportStatus:
        """Get an import status."""

    def post_import(self, zip_path: Path) -> ImportId:
        """Upload a ZIP file to import. Returns the import ID."""

    def delete_import(self, import_id: ImportId) -> None:
        """Delete an import after completion or failure."""
