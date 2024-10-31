from __future__ import annotations

import json
from dataclasses import dataclass

from rdflib import Graph


@dataclass
class SHACLValidationReport:
    conforms: bool
    validation_graph: Graph


@dataclass
class AllProjectLists:
    all_lists: list[OneList]


@dataclass
class OneList:
    list_iri: str
    list_name: str
    nodes: list[str]

    def hlist(self) -> str:
        return f'"hlist=<{self.list_iri}>"'

    def shacl_nodes(self) -> str:
        escaped_nodes = [str(self._to_json_str(x)) for x in sorted(self.nodes)]
        node_str = " ".join(escaped_nodes)
        return f"( {node_str} )"

    def shacl_list(self) -> str:
        return f"( {self._to_json_str(self.list_name)} )"

    def _to_json_str(self, in_str: str) -> bytes:
        return json.dumps(in_str, ensure_ascii=False).encode("utf-8")
