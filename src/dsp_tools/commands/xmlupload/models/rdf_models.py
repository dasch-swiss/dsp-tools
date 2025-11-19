from __future__ import annotations

from dataclasses import dataclass

from rdflib import URIRef


@dataclass
class RDFPropTypeInfo:
    knora_type: URIRef
    knora_prop: URIRef
    xsd_type: URIRef | None = None


@dataclass
class AbstractFileValue:
    value: str
    metadata: FileValueMetadata


@dataclass
class FileValueMetadata:
    license_iri: str
    copyright_holder: str
    authorships: list[str]
    permissions: str | None
