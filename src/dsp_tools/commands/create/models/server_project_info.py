from dataclasses import dataclass

from dsp_tools.error.exceptions import InternalError


@dataclass
class ProjectIriLookup:
    project_iri: str
    onto_iris: dict[str, str]

    def get_onto_iri(self, onto_name: str) -> str:
        if found := self.onto_iris.get(onto_name):
            return found
        raise InternalError(f"Ontology with name '{onto_name}' does not have an IRI.")
