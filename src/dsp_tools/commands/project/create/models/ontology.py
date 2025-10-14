from dataclasses import dataclass

from rdflib import Literal
from rdflib import URIRef


@dataclass
class Cardinality:
    on_property: URIRef
    cardinality: Literal
