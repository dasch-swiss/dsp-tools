from typing import Any

from dsp_tools.clients.group_user_clients import GroupClient


class GroupClientLive(GroupClient):
    api_url: str

    def get_all_groups(self) -> list[dict[str, Any]]:
        pass
