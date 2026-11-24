from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Protocol

from dsp_vre.clients.authentication_client import AuthenticationClient


@dataclass(frozen=True)
class DataImportId:
    id_: str


class DataImportStatusValue(Enum):
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
        """Upload a JSON-LD payload file and start the import. The data is attributed to the on-behalf-of user."""

    def get_status(self, import_id: DataImportId) -> DataImportStatus:
        """Get the status of an import."""

    def delete_import(self, import_id: DataImportId) -> None:
        """Delete an import after completion or failure."""
