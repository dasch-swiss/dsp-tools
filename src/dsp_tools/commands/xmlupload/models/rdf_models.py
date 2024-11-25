from __future__ import annotations

from dataclasses import dataclass

from rdflib import Literal
from rdflib import URIRef


@dataclass
class TransformedValue:
    value: Literal | URIRef
    prop_name: URIRef
    permissions: str | None
    comment: str | None


@dataclass
class RDFPropTypeInfo:
    knora_type: URIRef
    knora_prop: URIRef


@dataclass
class Interval:
    start: Literal
    end: Literal
