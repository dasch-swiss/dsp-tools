from __future__ import annotations

from dataclasses import dataclass

from rdflib import Graph
from rdflib.term import Node


@dataclass
class ValidationReport:
    conforms: bool
    validation_graph: Graph | None = None
    shacl_graph: Graph | None = None
    data_graph: Graph | None = None


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
