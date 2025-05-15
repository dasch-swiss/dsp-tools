from typing import Any
from typing import Protocol

from dsp_tools.clients.authentication_client import AuthenticationClient


class LegalInfoClient(Protocol):
    """
    Protocol class/interface for the legal info endpoint of the admin API.
    """

    server: str
    project_shortcode: str
    authentication_client: AuthenticationClient

    def post_copyright_holders(self, copyright_holders: list[str]) -> None:
        """Send a list of new copyright holders to the API"""

    def get_enabled_licenses(self) -> list[dict[str, Any]]:
        """Get a list of enabled licenses for the project."""
