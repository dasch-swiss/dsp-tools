from __future__ import annotations

from dataclasses import dataclass

from rdflib import Literal
from rdflib import URIRef


@dataclass
class RdfCardinalityRestriction:
    owl_property: URIRef
    cardinality_value: Literal
