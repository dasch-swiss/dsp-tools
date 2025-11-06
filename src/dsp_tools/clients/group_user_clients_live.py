from typing import Any

from dsp_tools.clients.group_user_clients import GroupClient


class GroupClientLive(GroupClient):
    api_url: str

    def get_all_groups(self) -> list[dict[str, Any]]:
        """Route: /admin/groups"""

        """
        response.json:
        {
        "groups": [
            {
                "id": "http://rdfh.ch/groups/4123/K6tppNTITqGY1nLvxdDL9A",
                "name": "testgroupEditors",
                "descriptions": [
                ],
                "project": {
                    "id": "http://rdfh.ch/projects/DPCEKkIjTYe9ApkgwBTWeg",
                    "shortname": "systematic-tp",
            }]}
        """

