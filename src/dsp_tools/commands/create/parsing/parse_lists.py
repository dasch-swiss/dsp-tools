from collections import Counter
from typing import Any

from dsp_tools.commands.create.models.input_problems import CollectedProblems
from dsp_tools.commands.create.models.input_problems import CreateProblem
from dsp_tools.commands.create.models.input_problems import InputProblem
from dsp_tools.commands.create.models.input_problems import ProblemType
from dsp_tools.commands.create.models.parsed_project import ParsedList
from dsp_tools.commands.create.models.parsed_project import ParsedListNode
from dsp_tools.commands.create.models.parsed_project import ParsedNodeInfo


def parse_list_section(lists: list[dict[str, Any]]) -> list[ParsedList] | CollectedProblems:
    list_section = [_parse_one_list(one_list) for one_list in lists]
    list_names = [parsed_list.list_info.name for parsed_list in list_section]
    duplicates = {name for name, count in Counter(list_names).items() if count > 1}
    if duplicates:
        problems: list[CreateProblem] = [
            InputProblem(problematic_object=name, problem=ProblemType.DUPLICATE_LIST_NAME) for name in duplicates
        ]
        return CollectedProblems(header="The following problems were found in the list section:", problems=problems)
    return list_section


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
