from __future__ import annotations

from dataclasses import dataclass

from rdflib import Graph
from rdflib import URIRef


@dataclass
class SHACLValidationReport:
    conforms: bool
    validation_graph: Graph


@dataclass
class ProjectDataFromApi:
    all_lists: list[OneList]
    enabled_licenses: EnabledLicenseIris
    resource_iris_in_db: list[InfoForResourceInDB]


@dataclass
class ListLookup:
    lists: dict[tuple[str, str], str]


@dataclass
class SHACLListInfo:
    list_iri: URIRef
    sh_path: URIRef
    sh_message: str
    sh_in: list[str]


@dataclass
class EnabledLicenseIris:
    enabled_licenses: list[str]


@dataclass
class InfoForResourceInDB:
    res_iri: str
    res_type: str


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
