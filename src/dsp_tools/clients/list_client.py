from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from typing import Protocol

from dsp_tools.clients.authentication_client import AuthenticationClient


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
        """Get all lists and its nodes from a project."""

    def get_all_list_iris_and_names(self) -> dict[str, str]:
        """Get all list names and IRIs"""


@dataclass
class ListCreateClient(Protocol):
    api_url: str
    auth: AuthenticationClient

    def create_new_list(self, list_info: dict[str, Any]) -> str | None:
        """Create a new list."""

    def add_list_node(self, node_info: dict[str, Any], parent_iri: str) -> str | None:
        """Add a list node to an existing list."""
