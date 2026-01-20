from dataclasses import dataclass
from typing import Any
from typing import Protocol

from dsp_tools.clients.authentication_client import AuthenticationClient
from dsp_tools.utils.request_utils import ResponseCodeAndText


@dataclass
class PermissionsClient(Protocol):
    auth: AuthenticationClient
    project_iri: str

    def get_project_doaps(self) -> list[dict[str, Any]]:
        """
        Get all default object access permissions (DOAPs) for the project.
        """

    def delete_doap(self, doap_iri: str) -> ResponseCodeAndText | None:
        """
        Delete a default object access permission by IRI.
        """

    def create_new_doap(self, payload: dict[str, Any]) -> ResponseCodeAndText | None:
        """
        Create a new default object access permission.
        """
