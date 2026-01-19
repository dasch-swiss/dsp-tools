from typing import Any
from typing import Protocol

from dsp_tools.clients.authentication_client import AuthenticationClient


class PermissionsClient(Protocol):
    """Protocol for interacting with DSP-API permissions endpoints."""

    server: str
    auth: AuthenticationClient
    project_iri: str

    def get_project_doaps(self) -> list[dict[str, Any]]:
        """
        Get all default object access permissions (DOAPs) for the project.
        """

    def delete_doap(self, doap_iri: str) -> None:
        """
        Delete a default object access permission by IRI.
        """

    def create_new_doap(self, payload: dict[str, Any]) -> bool:
        """
        Create a new default object access permission.
        """
