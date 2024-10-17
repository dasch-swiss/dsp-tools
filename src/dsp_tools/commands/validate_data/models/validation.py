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
class QueryInfo:
    validation_bn: Node
    focus_iri: Node
    focus_rdf_type: Node


@dataclass
class UnexpectedComponent:
    component_type: str


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
class ValidationResult:
    res_iri: Node
    res_class: Node
    property: Node


@dataclass
class ResultValueTypeViolation(ValidationResult):
    results_message: str
    actual_value_type: Node


@dataclass
class ResultPatternViolation(ValidationResult):
    results_message: str
    actual_value: str


@dataclass
class ResultLinkTargetViolation(ValidationResult):
    results_message: str
    target_iri: Node
    target_resource_type: Node | None


@dataclass
class ResultMaxCardinalityViolation(ValidationResult):
    results_message: str


@dataclass
class ResultMinCardinalityViolation(ValidationResult):
    results_message: str


@dataclass
class ResultNonExistentCardinalityViolation(ValidationResult): ...


@dataclass
class ReformattedIRI:
    res_id: str
    res_type: str
    prop_name: str
