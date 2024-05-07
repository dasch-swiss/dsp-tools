from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field
from typing import Any

import pandas as pd

from dsp_tools.commands.excel2json.models.input_error import ListNodeProblem
from dsp_tools.commands.excel2json.models.input_error import ListSheetProblem


@dataclass
class ListNode:
    id_: str
    labels: dict[str, str]
    parent_id: str
    sub_nodes: list[ListNode] = field(default_factory=list)

    @classmethod
    def create(
        cls,
        id_: str | int | float,
        labels: dict[str, str],
        parent_id: str,
        sub_nodes: list[ListNode],
    ) -> ListNode | ListNodeProblem:
        user_problem = {}
        if pd.isna(id_):
            user_problem["name"] = "The name of the node may not be empty."
        elif isinstance(id_, int | float):
            id_ = str(id_)
        elif len(id_) == 0:
            user_problem["name"] = "The name of the node does not contain any characters."
        if not labels:
            user_problem["labels"] = "At least one label per list is required."
        elif not set(labels).issubset({"en", "de", "fr", "it", "rm"}):
            user_problem["labels"] = "Only the following languages are supported: 'en', 'de', 'fr', 'it', 'rm'."
        if not parent_id:
            user_problem["parent_id"] = "The node does not have a parent node specified."
        if user_problem:
            return ListNodeProblem(id_, user_problem)
        return cls(id_=id_, labels=labels, parent_id=parent_id, sub_nodes=sub_nodes)

    def to_dict(self) -> dict[str, Any]:
        node = self._make_own_node()
        if self.sub_nodes:
            node["nodes"] = self._make_subnodes()
        return node

    def _make_subnodes(self) -> list[dict[str, Any]]:
        return [nd.to_dict() for nd in self.sub_nodes]

    def _make_own_node(self) -> dict[str, Any]:
        return {"name": self.id_, "labels": self.labels}


@dataclass
class ListRoot:
    id_: str
    labels: dict[str, str]
    nodes: list[ListNode]
    comments: dict[str, str] = field(default_factory=dict)

    @classmethod
    def create(
        cls,
        id_: str | int | float,
        labels: dict[str, str],
        sheet_name: str,
        nodes: list[ListNode],
        comments: dict[str, str],
    ) -> ListRoot | ListSheetProblem:
        user_problem = {}
        if pd.isna(id_):
            user_problem["name"] = "The name of the list may not be empty."
        elif isinstance(id_, int | float):
            id_ = str(id_)
        elif not isinstance(id_, str):
            user_problem["name"] = "The name of the list is not a string."
        elif len(id_) == 0:
            user_problem["name"] = "The name of the list does not contain any characters."
        if not labels:
            user_problem["labels"] = "At least one label per list is required."
        elif not set(labels).issubset({"en", "de", "fr", "it", "rm"}):
            user_problem["labels"] = "Only the following languages are supported: 'en', 'de', 'fr', 'it', 'rm'."
        if not set(comments).issubset({"en", "de", "fr", "it", "rm"}):
            user_problem["comments"] = "Only the following languages are supported: 'en', 'de', 'fr', 'it', 'rm'."
        if not nodes:
            user_problem["list nodes"] = "At least one node per list is required."
        if user_problem:
            return ListSheetProblem(sheet_name, user_problem)
        return cls(id_=id_, labels=labels, comments=comments, nodes=nodes)

    def to_dict(self) -> dict[str, Any]:
        lst_root = self._make_list_root()
        lst_root["nodes"] = self._make_nodes()
        return lst_root

    def _make_nodes(self) -> list[dict[str, Any]]:
        return [nd.to_dict() for nd in self.nodes]

    def _make_list_root(self) -> dict[str, Any]:
        lst = {"name": self.id_, "labels": self.labels}
        if self.comments:
            lst.update({"comments": self.comments})
        else:
            lst.update({"comments": self.labels})
        return lst
