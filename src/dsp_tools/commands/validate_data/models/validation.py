from __future__ import annotations

from dataclasses import dataclass

from rdflib import Graph
from rdflib.term import Node


@dataclass
class RDFGraphs:
    data: Graph
    ontos: Graph
    cardinality_shapes: Graph
    content_shapes: Graph

    def get_cardinality_data_str(self) -> str:
        return self.data.serialize(format="ttl")

    def get_cardinality_shacl_str(self) -> str:
        return self.cardinality_shapes.serialize(format="ttl")

    def get_content_data_str(self) -> str:
        g = self.data + self.ontos
        return g.serialize(format="ttl")

    def get_content_shacl_str(self) -> str:
        return self.content_shapes.serialize(format="ttl")


@dataclass
class ValidationReports:
    conforms: bool
    content_validation: Graph | None
    cardinality_validation: Graph | None
    shacl_graphs: Graph
    data_graph: Graph


@dataclass
class UnexpectedComponent:
    component_type: str


@dataclass
class CardinalityValidationResult:
    source_constraint_component: Node
    res_iri: Node
    res_class: Node
    property: Node
    results_message: str


@dataclass
class ContentValidationResult:
    source_constraint_component: Node
    res_iri: Node
    res_class: Node
    property: Node
    results_message: str
    value: str | None = None
    value_type: Node | None = None
