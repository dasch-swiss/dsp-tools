from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass
class OneList:
    list_iri: str
    list_name: str
    nodes: list[OneNode]

    def hlist(self) -> str:
        return f'"hlist=<{self.list_iri}>"'


@dataclass
class OneNode:
    name: str
    iri: str


@dataclass
class ListGetClient(Protocol):
    """Client to request and reformat the lists of a project."""

    api_url: str
    shortcode: str

    def get_all_lists_and_nodes(self) -> list[OneList]:
        """Get all lists and it's nodes from a project."""
