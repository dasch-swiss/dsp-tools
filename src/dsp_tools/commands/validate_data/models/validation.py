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
class ResourceValidationReportIdentifiers:
    validation_bn: Node
    focus_node_iri: Node
    res_class_type: Node
    detail_node: Node | None = None


@dataclass
class UnexpectedComponent:
    component_type: str


@dataclass
class ResultWithoutDetail:
    source_constraint_component: Node
    res_iri: Node
    res_class: Node
    property: Node
    results_message: str
    value: str | None = None


@dataclass
class ResultWithDetail:
    source_constraint_component: Node
    res_iri: Node
    res_class: Node
    property: Node
    results_message: str
    detail_bn_component: Node
    value: str | None
    value_type: Node | None = None
