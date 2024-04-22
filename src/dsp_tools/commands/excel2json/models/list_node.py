from __future__ import annotations

from typing import Any
from typing import Literal

from pydantic import BaseModel
from pydantic import Field

LanguageTag = Literal["en", "de", "fr", "it", "rm"]


class ListNode(BaseModel):
    id_: str
    labels: dict[LanguageTag, str]
    row_number: int
    sub_nodes: list[ListNode] = Field(default_factory=list)

    def to_json(self) -> dict[str, Any]:
        node = self._make_myself()
        if self.sub_nodes:
            node["nodes"] = self._make_subnodes()
        return node

    def _make_subnodes(self) -> list[dict[str, Any]]:
        return [nd.to_json() for nd in self.sub_nodes]

    def _make_myself(self) -> dict[str, Any]:
        return {"name": self.id_, "labels": self.labels}


class ListRoot(BaseModel):
    id_: str
    labels: dict[LanguageTag, str]
    nodes: list[ListNode] = Field(default_factory=list)
    comments: dict[LanguageTag, str] | None = None

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
