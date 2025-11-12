from typing import Any
from typing import Protocol

from dsp_tools.clients.authentication_client import AuthenticationClient


class GroupClient(Protocol):
    api_url: str
    auth: AuthenticationClient

    def get_all_groups(self) -> list[dict[str, Any]]:
        """Get all the groups on this DSP-Server."""

    def create_new_group(self, group_dict: dict[str, Any]) -> str | None:
        """Create a new group."""
