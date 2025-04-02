from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from enum import auto

from rdflib import Graph

from dsp_tools.utils.rdflib_constants import SubjectObjectTypeAlias


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
    focus_node_iri: SubjectObjectTypeAlias
    focus_node_type: SubjectObjectTypeAlias
    result_path: SubjectObjectTypeAlias
    detail: DetailBaseInfo | None = None


@dataclass
class DetailBaseInfo:
    detail_bn: SubjectObjectTypeAlias
    source_constraint_component: SubjectObjectTypeAlias


@dataclass
class ValidationResult:
    violation_type: ViolationType
    res_iri: SubjectObjectTypeAlias
    res_class: SubjectObjectTypeAlias
    property: SubjectObjectTypeAlias | None = None
    message: SubjectObjectTypeAlias | None = None
    input_value: SubjectObjectTypeAlias | None = None
    input_type: SubjectObjectTypeAlias | None = None
    expected: SubjectObjectTypeAlias | None = None


class ViolationType(Enum):
    SEQNUM_IS_PART_OF = auto()
    UNIQUE_VALUE = auto()
    VALUE_TYPE = auto()
    PATTERN = auto()
    GENERIC = auto()
    LINK_TARGET = auto()
    MAX_CARD = auto()
    MIN_CARD = auto()
    NON_EXISTING_CARD = auto()
    FILEVALUE_PROHIBITED = auto()
    FILE_VALUE = auto()


@dataclass
class ReformattedIRI:
    res_id: str
    res_type: str
    prop_name: str
