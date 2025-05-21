from __future__ import annotations

from dataclasses import dataclass

from rdflib import Graph


@dataclass
class SHACLValidationReport:
    conforms: bool
    validation_graph: Graph


@dataclass
class ProjectDataFromApi:
    all_lists: list[OneList]
    enabled_licenses: EnabledLicenseIris


@dataclass
class ListLookup:
    lists: dict[tuple[str, str], str]


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
class EnabledLicenseIris:
    enabled_licenses: list[str]
