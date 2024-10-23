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
    list_name: str
    nodes: list[str]
