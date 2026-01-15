from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, unique
from typing import Optional


@dataclass(frozen=True)
class OntoIri:
    """
    Holds an ontology IRI

    Attributes:
        iri: the ontology IRI
        hashtag: True if "#" is used to separate elements, False if element name is appended after "/"
    """

    iri: str
    hashtag: bool


@unique
class Cardinality(Enum):
    C_1 = "1"
    C_0_1 = "0-1"
    C_1_n = "1-n"
    C_0_n = "0-n"


def get_json_ld_id(obj: Optional[dict[str, str]]) -> Optional[str]:
    """Extract the @id value from a JSON-LD object."""
    if obj is None:
        return None
    return obj.get("@id")
