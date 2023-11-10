from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class ProjectOntology:
    ontology_name: str
    classes: list[str] = field(default_factory=lambda: list())
    properties: list[str] = field(default_factory=lambda: list())
    is_default_onto: bool = False

    @staticmethod
    def make(ontology_info: list[dict[str, Any]], ontology_name: str) -> ProjectOntology:
        onto = ProjectOntology(ontology_name=ontology_name)
        for ele in ontology_info:
            if ele.get("knora-api:isResourceClass"):
                onto.classes.append(ele["@id"])
            else:
                onto.properties.append(ele["id"])
        return onto
