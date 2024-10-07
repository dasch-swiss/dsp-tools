from __future__ import annotations

from dataclasses import dataclass

from rdflib import Graph
from rdflib.term import Node


@dataclass
class ValidationResultTypes:
    node_constraint_component: set[Node]
    detail_bns: set[Node]
    cardinality_components: set[Node]


@dataclass
class ValidationReport:
    conforms: bool
    validation_graph: Graph
    shacl_graph: Graph
    data_graph: Graph


@dataclass
class UnexpectedComponent:
    component_type: str


@dataclass
class ValidationResult:
    source_constraint_component: Node
    res_iri: Node
    res_class: Node
    property: Node
    results_message: str
    value: str | None = None
    value_type: Node | None = None
