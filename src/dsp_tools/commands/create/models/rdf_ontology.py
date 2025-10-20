from __future__ import annotations

from dataclasses import dataclass

from rdflib import Literal
from rdflib import URIRef


@dataclass
class RdfResourceCardinality:
    resource_iri: URIRef
    on_property: URIRef
    cardinality: RdfCardinalityRestriction


@dataclass
class RdfCardinalityRestriction:
    owl_property: URIRef
    cardinality_value: Literal
