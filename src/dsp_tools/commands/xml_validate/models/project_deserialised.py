from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ListDeserialised:
    list_name: str
    iri: str
    nodes: list[str]
