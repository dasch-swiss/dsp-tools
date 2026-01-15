from __future__ import annotations

from dataclasses import dataclass

from rdflib import URIRef

from dsp_tools.commands.xmlupload.iri_resolver import IriResolver
from dsp_tools.commands.xmlupload.models.permission import Permissions


@dataclass
class XmlReferenceLookups:
    permissions: dict[str, Permissions]
    listnodes: dict[tuple[str, str], str]
    authorships: dict[str, list[str]]


@dataclass
class IRILookups:
    project_iri: URIRef
    id_to_iri: IriResolver


@dataclass(frozen=True)
class ListNode:
    """Information about a list node."""

    node_iri: str
    node_name: str


@dataclass(frozen=True)
class List:
    """Information about a list."""

    root_iri: str
    list_name: str
    nodes: list[ListNode]


@dataclass(frozen=True)
class ProjectLists:
    """Information about the lists of a project."""

    lists: list[List]
