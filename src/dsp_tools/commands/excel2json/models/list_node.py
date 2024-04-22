from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field
from typing import Any
from typing import Literal

LanguageTag = Literal["en", "de", "fr", "it", "rm"]


@dataclass
class ListRoot:
    _id: str
    labels: dict[LanguageTag, str]
    nodes: list[ListNode]
    comments: dict[LanguageTag, str] | None = None

    def to_json(self) -> dict[str, Any]:
        lst_root = self._make_myself()
        lst_root["nodes"] = self._make_nodes()
        return lst_root

    def _make_nodes(self) -> list[dict[str, Any]]:
        return [nd.to_json() for nd in self.nodes]

    def _make_myself(self) -> dict[str, Any]:
        lst = {"name": self._id, "labels": self.labels}
        if self.comments:
            lst.update({"comments": self.comments})
        return lst


@dataclass
class ListNode:
    _id: str
    labels: dict[LanguageTag, str]
    sub_nodes: list[ListNode] = field(default_factory=list)

    def to_json(self) -> dict[str, Any]:
        node = self._make_myself()
        if self.sub_nodes:
            node["nodes"] = self._make_subnodes()
        return node

    def _make_subnodes(self) -> list[dict[str, Any]]:
        return [nd.to_json() for nd in self.sub_nodes]

    def _make_myself(self) -> dict[str, Any]:
        return {"name": self._id, "labels": self.labels}
