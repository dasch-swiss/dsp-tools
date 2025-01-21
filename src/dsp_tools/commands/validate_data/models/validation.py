from __future__ import annotations

from dataclasses import dataclass

from rdflib import Graph

from dsp_tools.commands.validate_data.constants import SubjectObjectTypeAlias


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


@dataclass
class ValidationReportGraphs:
    conforms: bool
    validation_graph: Graph
    shacl_graph: Graph
    onto_graph: Graph
    data_graph: Graph


@dataclass
class QueryInfo:
    validation_bn: SubjectObjectTypeAlias
    focus_iri: SubjectObjectTypeAlias
    focus_rdf_type: SubjectObjectTypeAlias


@dataclass
class UnexpectedComponent:
    component_type: str


@dataclass
class ValidationResultBaseInfo:
    result_bn: SubjectObjectTypeAlias
    source_constraint_component: SubjectObjectTypeAlias
    resource_iri: SubjectObjectTypeAlias
    res_class_type: SubjectObjectTypeAlias
    result_path: SubjectObjectTypeAlias
    detail: DetailBaseInfo | None = None


@dataclass
class DetailBaseInfo:
    detail_bn: SubjectObjectTypeAlias
    source_constraint_component: SubjectObjectTypeAlias


@dataclass
class ValidationResult:
    res_iri: SubjectObjectTypeAlias
    res_class: SubjectObjectTypeAlias
    property: SubjectObjectTypeAlias | None


@dataclass
class SeqnumIsPartOfViolation(ValidationResult):
    results_message: str


@dataclass
class ResultUniqueValueViolation(ValidationResult):
    actual_value: SubjectObjectTypeAlias


@dataclass
class ResultValueTypeViolation(ValidationResult):
    results_message: str
    actual_value_type: SubjectObjectTypeAlias


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
    expected_type: SubjectObjectTypeAlias
    target_iri: SubjectObjectTypeAlias
    target_resource_type: SubjectObjectTypeAlias | None


@dataclass
class ResultMaxCardinalityViolation(ValidationResult):
    results_message: str


@dataclass
class ResultMinCardinalityViolation(ValidationResult):
    results_message: str


@dataclass
class ResultNonExistentCardinalityViolation(ValidationResult): ...


@dataclass
class ResultFileValueNotAllowedViolation(ValidationResult): ...


@dataclass
class ResultFileValueViolation(ValidationResult):
    results_message: str


@dataclass
class ReformattedIRI:
    res_id: str
    res_type: str
    prop_name: str
