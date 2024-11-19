from __future__ import annotations

from dataclasses import dataclass

from rdflib import BNode
from rdflib import Graph
from rdflib import Literal
from rdflib import URIRef

from dsp_tools.commands.xmlupload.models.permission import Permissions


@dataclass
class IntermediaryResource:
    res_id: str
    res_type: str
    values: list[GenericValue]
    permissions: Permissions | None
    file_value: AbstractFileValue | None


@dataclass
class GenericValue:
    prop_name: str
    value: bool | str | int | float
    comment: str | None
    permissions: Permissions | None


@dataclass
class AbstractFileValue:
    value: str
    permissions: Permissions | None


@dataclass
class RDFResource:
    res_bn: BNode
    triples: list[RDFTriples]

    def to_graph(self) -> Graph:
        g = Graph()
        for trip in self.triples:
            g.add((self.res_bn, trip.property, trip.object_value))
        return g


@dataclass
class RDFTriples:
    property: URIRef
    object_value: URIRef | Literal | BNode
