from __future__ import annotations

from dataclasses import dataclass

from rdflib import Literal
from rdflib import URIRef


@dataclass
class Cardinality:
    res_iri: URIRef
    on_property: URIRef
    cardinality: CardinalityRestriction


@dataclass
class CardinalityRestriction:
    owl_property: URIRef
    cardinality_value: Literal
