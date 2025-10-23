from dataclasses import dataclass
from dataclasses import field


@dataclass
class ProjectIriLookup:
    project_iri: str
    onto_iris: dict[str, str] = field(default_factory=dict)

    def add_onto(self, name: str, iri: str) -> None:
        self.onto_iris[name] = iri

    def get_onto_iri(self, name: str) -> str | None:
        return self.onto_iris.get(name)


@dataclass
class CreatedIriCollection:
    classes: set[str] = field(default_factory=set)
    properties: set[str] = field(default_factory=set)
