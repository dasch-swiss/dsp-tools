from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field
from typing import Any


@dataclass
class ListNode:
    id_: str
    labels: dict[str, str]
    comments: dict[str, str]
    parent_id: str
    sub_nodes: list[ListNode] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        node = self._make_own_node()
        if self.sub_nodes:
            node["nodes"] = self._make_subnodes()
        return node

    def _make_subnodes(self) -> list[dict[str, Any]]:
        return [nd.to_dict() for nd in self.sub_nodes]

    def _make_own_node(self) -> dict[str, Any]:
        sorted_labels = {k: self.labels[k] for k in sorted(self.labels.keys())}
        d = {"name": self.id_, "labels": sorted_labels}
        if self.comments:
            sorted_comments = {k: self.comments[k] for k in sorted(self.comments.keys())}
            d["comments"] = sorted_comments
        return d


@dataclass
class ListRoot:
    id_: str
    labels: dict[str, str]
    nodes: list[ListNode]
    comments: dict[str, str]

    def to_dict(self) -> dict[str, Any]:
        lst_root = self._make_list_root()
        lst_root["nodes"] = self._make_nodes()
        return lst_root

    def _make_nodes(self) -> list[dict[str, Any]]:
        return [nd.to_dict() for nd in self.nodes]

    def _make_list_root(self) -> dict[str, Any]:
        sorted_labels = {k: self.labels[k] for k in sorted(self.labels.keys())}
        lst = {"name": self.id_, "labels": sorted_labels}
        if self.comments:
            sorted_comments = {k: self.comments[k] for k in sorted(self.comments.keys())}
            lst["comments"] = sorted_comments
        else:
            lst["comments"] = sorted_labels
        return lst
