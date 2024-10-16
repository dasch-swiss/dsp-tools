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
    target_id: Node
    target_resource_type: Node | None


@dataclass
class ResultMinCardinalityViolation(ValidationResult):
    results_message: str


@dataclass
class ResultMaxCardinalityViolation(ValidationResult):
    results_message: str


@dataclass
class ResultNonExistentCardinalityViolation(ValidationResult): ...


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
    detail: ResultDetail


@dataclass
class ResultDetail:
    component: Node
    results_message: str
    result_path: Node | None
    value_type: Node
    value: str | None
