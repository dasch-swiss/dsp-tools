from dataclasses import dataclass
from dataclasses import field

from dsp_tools.error.exceptions import InternalError


@dataclass
class ProjectIriLookup:
    project_iri: str
    onto_iris: dict[str, str] = field(default_factory=dict)

    def get_onto_iri(self, onto_name: str) -> str:
        if found := self.onto_iris.get(onto_name):
            return found
        raise InternalError(f"Ontology with name '{onto_name}' does not have an IRI.")


@dataclass
class CreatedIriCollection:
    classes: set[str] = field(default_factory=set)
    properties: set[str] = field(default_factory=set)
