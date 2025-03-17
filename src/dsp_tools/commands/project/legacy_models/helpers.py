from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from enum import unique
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


ContextType = dict[str, OntoIri]


@unique
class Cardinality(Enum):
    C_1 = "1"
    C_0_1 = "0-1"
    C_1_n = "1-n"
    C_0_n = "0-n"


class WithId:
    """
    Class helper to get json-ld "@id" thingies
    """

    _tmp: str = None

    def __init__(self, obj: Optional[dict[str, str]]):
        if obj is None:
            return
        self._tmp = obj.get("@id")

    def to_string(self) -> Optional[str]:
        return self._tmp
