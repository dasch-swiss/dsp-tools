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
class MigrationExportClient(Protocol):
    project_iri: str
    auth: AuthenticationClient

    def get_status(self, export_id: str) -> ExportImportStatus:
        """Get the export status."""

    def post_export(self) -> str:
        """Start an export."""

    def get_download(self, export_id: str, destination: Path) -> None:
        """Download the export ZIP to the specified file path."""

    def delete_export(self, export_id: str) -> None:
        """Delete an export after completion or failure."""


@dataclass
class MigrationImportClient(Protocol):
    project_iri: str
    auth: AuthenticationClient

    def get_status(self, import_id: str) -> ExportImportStatus:
        """Get an import status."""

    def post_import(self, zip_path: Path) -> str:
        """Upload a ZIP file to import. Returns the import ID."""

    def delete_import(self, import_id: str) -> None:
        """Delete an import after completion or failure."""
