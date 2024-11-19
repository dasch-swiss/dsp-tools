from __future__ import annotations

from dataclasses import dataclass

from rdflib import BNode
from rdflib import Graph
from rdflib import Literal
from rdflib import URIRef


@dataclass
class ValueTypeTripleInfo:
    rdf_type: URIRef
    d_type: URIRef
    prop_name: URIRef


@dataclass
class RDFResource:
    res_id: str  # This is for the mapping at the moment and communication with the user
    res_bn: BNode  # This is for the mapping
    triples: list[RDFTriple]

    def to_graph(self) -> Graph:
        g = Graph()
        for val in self.triples:
            g.add(val.to_triple())
        return g


@dataclass
class RDFTriple:
    rdf_subject: URIRef | BNode
    rdf_property: URIRef
    rdf_object: URIRef | Literal | BNode

    def to_triple(self) -> tuple[BNode, URIRef, URIRef | Literal | BNode]:
        return self.rdf_subject, self.rdf_property, self.rdf_object
