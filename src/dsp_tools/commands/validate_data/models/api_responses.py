from __future__ import annotations

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
        escaped_nodes = [self._escape(x) for x in sorted(self.nodes)]
        node_str = " ".join(escaped_nodes)
        return f"( {node_str} )"

    def shacl_list(self) -> str:
        return f"( {self._escape(self.list_name)} )"

    def escaped_list_name(self) -> str:
        return self.list_name.replace("\\", "\\\\").replace("'", "\\'").replace('"', '\\"')

    def _escape(self, in_str: str) -> str:
        replace_problems = in_str.replace("\\", "\\\\").replace("'", "\\'").replace('"', '\\"')
        return '"' + replace_problems + '"'
