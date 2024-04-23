from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field
from typing import Any

import pandas as pd

from dsp_tools.commands.excel2json.models.input_error import ListNodeProblem
from dsp_tools.commands.excel2json.models.input_error import ListProblem


@dataclass
class ListNode:
    id_: str
    labels: dict[str, str]
    row_number: int
    sub_nodes: list[ListNode] = field(default_factory=list)

    @classmethod
    def create(
        cls, id_: str, labels: dict[str, str], row_number: int, sub_nodes: list[ListNode] | None = None
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
        if user_problem:
            return ListNodeProblem(id_, user_problem)
        if not sub_nodes:
            sub_nodes = []
        return cls(id_=id_, labels=labels, row_number=row_number, sub_nodes=sub_nodes)

    def to_json(self) -> dict[str, Any]:
        node = self._make_myself()
        if self.sub_nodes:
            node["nodes"] = self._make_subnodes()
        return node

    def _make_subnodes(self) -> list[dict[str, Any]]:
        return [nd.to_json() for nd in self.sub_nodes]

    def _make_myself(self) -> dict[str, Any]:
        return {"name": self.id_, "labels": self.labels}


@dataclass
class ListRoot:
    id_: str
    labels: dict[str, str]
    nodes: list[ListNode] = field(default_factory=list)
    comments: dict[str, str] | None = None

    @classmethod
    def create(
        cls,
        id_: str,
        labels: dict[str, str],
        nodes: list[ListNode],
        comments: dict[str, str] | None = None,
    ) -> ListRoot | ListProblem:
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
        if comments:
            if not set(comments).issubset({"en", "de", "fr", "it", "rm"}):
                user_problem["comments"] = "Only the following languages are supported: 'en', 'de', 'fr', 'it', 'rm'."
        if len(nodes) == 0:
            user_problem["list nodes"] = "At least one node per list is required."
        if user_problem:
            return ListProblem(id_, user_problem)
        return cls(id_=id_, labels=labels, comments=comments, nodes=nodes)

    def to_json(self) -> dict[str, Any]:
        lst_root = self._make_myself()
        lst_root["nodes"] = self._make_nodes()
        return lst_root

    def _make_nodes(self) -> list[dict[str, Any]]:
        return [nd.to_json() for nd in self.nodes]

    def _make_myself(self) -> dict[str, Any]:
        lst = {"name": self.id_, "labels": self.labels}
        if self.comments:
            lst.update({"comments": self.comments})
        return lst
