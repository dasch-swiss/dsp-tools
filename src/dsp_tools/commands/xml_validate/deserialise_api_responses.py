from typing import Any

from dsp_tools.commands.xml_validate.api_connection import ProjectClient
from dsp_tools.commands.xml_validate.models.api_response_deserialised import ListDeserialised


def deserialise_lists(project_client: ProjectClient) -> list[ListDeserialised]:
    """Get objects which contain the pertinent information of the lists from the API."""
    all_lists = _request_all_lists(project_client)
    return [_deserialise_one_list(x) for x in all_lists]


def _request_all_lists(project_client: ProjectClient) -> list[dict[str, Any]]:
    list_iris = project_client.get_list_iris()
    list_responses = []
    for list_iri in list_iris:
        list_responses.append(project_client.get_one_list(list_iri))
    return list_responses


def _deserialise_one_list(list_response: dict[str, Any]) -> ListDeserialised:
    """This can only handle one depth at the moment."""
    all_children = []
    for child in list_response["children"]:
        all_children.extend(_get_one_child(child))
    return ListDeserialised(list_name=list_response["listinfo"], nodes=all_children)


def _get_one_child(node: dict[str, Any]) -> list[str]:
    nodes = [node["name"]]
    for child in node["children"]:
        nodes.append(child["name"])
    return nodes
