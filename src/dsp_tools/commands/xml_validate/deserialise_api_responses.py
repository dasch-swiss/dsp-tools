from typing import Any

from dsp_tools.commands.xml_validate.api_connection import ProjectClient
from dsp_tools.commands.xml_validate.models.api_response_deserialised import ListDeserialised


def get_deserialised_lists(project_client: ProjectClient) -> ListDeserialised:
    """Get objects which contain the pertinent information of the lists from the API."""
    all_lists = project_client.get_one_list()
    return _deserialise_one_list(all_lists)


def _deserialise_one_list(list_response: dict[str, Any]) -> ListDeserialised:
    all_children = []
    for child in list_response["list"]["children"]:
        all_children.extend(_process_child_nodes(child))
    return ListDeserialised(list_name=list_response["list"]["listinfo"]["name"], nodes=all_children)


def _process_child_nodes(node: dict[str, Any]) -> list[str]:
    children = []
    all_nodes = [node]
    while all_nodes:
        current_node = all_nodes.pop(0)
        children.append(current_node["name"])
        all_nodes.extend(current_node.get("children", []))
    return children
