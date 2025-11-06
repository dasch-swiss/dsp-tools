from typing import Any
from typing import Protocol


class GroupClient(Protocol):
    api_url: str

    def get_all_groups(self) -> list[dict[str, Any]]:
        """Get all the groups on this DSP-Server."""