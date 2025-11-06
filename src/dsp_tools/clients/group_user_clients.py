from typing import Any
from typing import Protocol


class GroupClient(Protocol):
    api_url: str

    def get_all_groups(self) -> list[dict[str, Any]]:
        """Get all the groups on this DSP-Server."""

    def create_new_group(self, group_dict: dict[str, Any]) -> str | None:
        """Create a new group."""
