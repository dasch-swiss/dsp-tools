from dataclasses import dataclass
from rdflib import URIRef, Literal

@dataclass
class Cardinality:
    on_property: URIRef
    cardinality: Literal


