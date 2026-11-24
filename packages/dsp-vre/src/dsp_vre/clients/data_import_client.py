from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Protocol

from dsp_vre.clients.authentication_client import AuthenticationClient


@dataclass(frozen=True)
class DataImportId:
    id_: str


class DataImportStatusValue(Enum):
    """
    The status of a bulk data import task.
    Separate from the migration `ExportImportStatus`, because the two server contracts change independently.
    """

    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass(frozen=True)
class DataImportStatus:
    id: DataImportId
    project_iri: str
    status: DataImportStatusValue
    error_message: str | None


@dataclass
class DataImportClient(Protocol):
    server: str
    project_iri: str
    auth: AuthenticationClient

    def post_import(self, payload_path: Path, on_behalf_of_user: str) -> DataImportId:
        """Upload a JSON-LD payload file and start a bulk data import on behalf of a project user."""

    def get_status(self, import_id: DataImportId) -> DataImportStatus:
        """Get the status of a bulk data import task."""

    def delete_import(self, import_id: DataImportId) -> None:
        """Delete a bulk data import task after it completed or failed."""
