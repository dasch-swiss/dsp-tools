from dataclasses import dataclass
from dataclasses import field

from dsp_tools.commands.create.constants import KNORA_API_STR


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

    def __post_init__(self) -> None:
        self.properties.update({f"{KNORA_API_STR}seqnum", f"{KNORA_API_STR}isPartOf"})
