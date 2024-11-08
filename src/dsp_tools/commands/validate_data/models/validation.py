from __future__ import annotations

from dataclasses import dataclass

from rdflib import Graph
from rdflib.term import Node


@dataclass
class SHACLGraphs:
    cardinality: Graph
    content: Graph


@dataclass
class RDFGraphs:
    data: Graph
    ontos: Graph
    cardinality_shapes: Graph
    content_shapes: Graph
    knora_api: Graph

    def get_data_and_onto_str(self) -> str:
        g = self.data + self.ontos + self.knora_api
        return g.serialize(format="ttl")

    def get_data_str(self) -> str:
        return self.data.serialize(format="ttl")

    def get_cardinality_shacl_and_onto_str(self) -> str:
        g = self.cardinality_shapes + self.ontos + self.knora_api
        return g.serialize(format="ttl")

    def get_content_shacl_and_onto_str(self) -> str:
        g = self.content_shapes + self.ontos + self.knora_api
        return g.serialize(format="ttl")


@dataclass
class ValidationReportGraphs:
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
class ResultUniqueValueViolation(ValidationResult):
    actual_value: Node


@dataclass
class ResultValueTypeViolation(ValidationResult):
    results_message: str
    actual_value_type: Node


@dataclass
class ResultPatternViolation(ValidationResult):
    results_message: str
    actual_value: str


@dataclass
class ResultGenericViolation(ValidationResult):
    results_message: str
    actual_value: str


@dataclass
class ResultLinkTargetViolation(ValidationResult):
    expected_type: Node
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
