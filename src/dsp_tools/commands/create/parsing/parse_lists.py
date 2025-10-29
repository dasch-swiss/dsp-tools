from typing import Any

from dsp_tools.commands.create.models.parsed_project import ParsedList
from dsp_tools.commands.create.models.parsed_project import ParsedListNode
from dsp_tools.commands.create.models.parsed_project import ParsedNodeInfo


def parse_list_section(lists: list[dict[str, Any]]) -> list[ParsedList]:
    pass


def _parse_one_list(one_list: dict[str, Any]) -> ParsedList:
    pass


def _parse_node_info(one_node: dict[str, Any]) -> ParsedNodeInfo:
    pass


def _parse_nodes_and_children(list_nodes: list[dict[str, Any]]) -> list[ParsedListNode]:
    pass
