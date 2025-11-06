from typing import Any
from dsp_tools.clients.group_user_clients import GroupClient
from dsp_tools.commands.create.models.server_project_info import GroupNameToIriLookup

def get_group_to_iri_lookup(group_client: GroupClient, project_iri: str) -> GroupNameToIriLookup:
    all_groups = group_client.get_all_groups()
    return _construct_group_lookup(all_groups, project_iri)


def _construct_group_lookup(all_groups: list[dict[str, Any]], project_iri: str) -> GroupNameToIriLookup:
    pass
