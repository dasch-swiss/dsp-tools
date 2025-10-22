from dataclasses import dataclass
from dataclasses import field


@dataclass
class ProjectIriLookup:
    project_iri: str
    onto_iris: dict[str, str] = field(default_factory=dict)


@dataclass
class CreatedIriCollection:
    classes: set[str] = field(default_factory=set)
    properties: set[str] = field(default_factory=set)
