from typing import Any

from dsp_tools.commands.create.models.parsed_project import ParsedList
from dsp_tools.commands.create.models.parsed_project import ParsedListNode
from dsp_tools.commands.create.models.parsed_project import ParsedNodeInfo


def parse_list_section(lists: list[dict[str, Any]]) -> list[ParsedList]:
    return [_parse_one_list(one_list) for one_list in lists]


def _parse_one_list(one_list: dict[str, Any]) -> ParsedList:
    list_info = _parse_node_info(one_list)
    children = _parse_nodes_and_children(one_list["nodes"]) if "nodes" in one_list else []
    return ParsedList(list_info=list_info, children=children)


def _parse_node_info(one_node: dict[str, Any]) -> ParsedNodeInfo:
    return ParsedNodeInfo(
        name=one_node["name"],
        labels=one_node["labels"],
        comments=one_node.get("comments"),
    )


def _parse_nodes_and_children(list_nodes: list[dict[str, Any]]) -> list[ParsedListNode]:
    parsed_nodes = []
    for node in list_nodes:
        node_info = _parse_node_info(node)
        children = _parse_nodes_and_children(node["nodes"]) if "nodes" in node else []
        parsed_nodes.append(ParsedListNode(node_info=node_info, children=children))
    return parsed_nodes
