from __future__ import annotations

from dataclasses import dataclass

from rdflib import Literal
from rdflib import URIRef

from dsp_tools.utils.xml_parsing.models.parsed_resource import FileValueMetadata


@dataclass
class TransformedValue:
    value: Literal | URIRef
    prop_name: URIRef
    permissions: str | None
    comment: str | None


@dataclass
class Interval:
    start: Literal
    end: Literal


@dataclass
class RDFPropTypeInfo:
    knora_type: URIRef
    knora_prop: URIRef
    xsd_type: URIRef | None = None


@dataclass
class AbstractFileValue:
    value: str
    metadata: FileValueMetadata
