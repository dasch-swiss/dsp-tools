from __future__ import annotations

from dataclasses import dataclass

from rdflib import Graph
from rdflib.term import Node


@dataclass
class RDFGraphs:
    data: Graph
    ontos: Graph
    shapes: Graph

    def get_data_and_onto_str(self) -> str:
        g = self.data + self.ontos
        return g.serialize(format="ttl")

    def get_shacl_and_onto_str(self) -> str:
        g = self.shapes + self.ontos
        return g.serialize(format="ttl")


@dataclass
class ValidationReport:
    conforms: bool
    validation_graph: Graph
    shacl_graph: Graph
    onto_graph: Graph
    data_graph: Graph


@dataclass
class UnexpectedComponent:
    component_type: str


@dataclass
class QueryInfo:
    validation_bn: Node
    focus_iri: Node
    focus_rdf_type: Node


@dataclass
class ValidationResultBaseInfo:
    result_bn: Node
    source_constraint_component: Node
    resource_iri: Node
    res_class_type: Node
    result_path: Node
    detail: DetailBaseInfo | None = None


@dataclass
class DetailBaseInfo:
    detail_bn: Node
    source_constraint_component: Node


@dataclass
class ExtractedResultWithoutDetail:
    source_constraint_component: Node
    res_iri: Node
    res_class: Node
    property: Node
    results_message: str
    value: str | None = None


@dataclass
class ExtractedResultWithDetail:
    source_constraint_component: Node
    res_iri: Node
    res_class: Node
    property: Node
    detail: ExtractedResultDetail


@dataclass
class ExtractedResultDetail:
    component: Node
    results_message: str
    result_path: Node | None
    value_type: Node
    value: str | None
