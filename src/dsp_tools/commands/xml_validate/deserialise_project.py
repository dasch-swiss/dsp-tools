import json
from typing import Any

from dsp_tools.commands.xml_validate.models.project import ListDeserialised


def _get_project_ontology() -> Any:
    with open("testdata/xml-validate/from_api/onto.jsonld", "r", encoding="utf-8") as file:
        return json.load(file)


def get_deserialised_lists() -> ListDeserialised:
    """Get objects which contain the pertinent information of the lists from the API."""
    with open("testdata/xml-validate/from_api/onlyList.json", "r", encoding="utf-8") as file:
        data: dict[str, Any] = json.load(file)
    return _deserialise_one_list(data)


def _deserialise_one_list(list_response: dict[str, Any]) -> ListDeserialised:
    all_children = []
    for child in list_response["list"]["children"]:
        all_children.extend(_process_child_nodes(child))
    return ListDeserialised(
        list_name=list_response["list"]["listinfo"]["name"],
        iri=list_response["list"]["listinfo"]["id"],
        nodes=all_children,
    )


def _process_child_nodes(node: dict[str, Any]) -> list[str]:
    children = []
    all_nodes = [node]
    while all_nodes:
        current_node = all_nodes.pop(0)
        children.append(current_node["name"])
        all_nodes.extend(current_node.get("children", []))
    return children
