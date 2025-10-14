from __future__ import annotations

from dataclasses import dataclass

from rdflib import Literal
from rdflib import URIRef


@dataclass
class ResourceCardinalities:
    res_iri: URIRef
    cards: list[Cardinality]


@dataclass
class Cardinality:
    on_property: URIRef
    cardinality: CardinalityRestriction


@dataclass
class CardinalityRestriction:
    owl_property: URIRef
    cardinality_value: Literal
