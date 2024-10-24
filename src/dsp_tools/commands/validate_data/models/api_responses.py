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
        sorted_nodes = sorted(self.nodes)
        output = [f'"{x}"' for x in sorted_nodes]
        node_str = " ".join(output)
        return f"( {node_str} )"

    def shacl_list(self) -> str:
        return f'( "{self.list_name}" )'
