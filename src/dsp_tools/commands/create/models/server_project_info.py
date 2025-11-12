from dataclasses import dataclass
from dataclasses import field

from dsp_tools.commands.create.constants import KNORA_API_STR
from dsp_tools.error.exceptions import InternalError


@dataclass
class ProjectIriLookup:
    project_iri: str
    onto_iris: dict[str, str] = field(default_factory=dict)

    def add_onto(self, name: str, iri: str) -> None:
        self.onto_iris[name] = iri


@dataclass
class GroupNameToIriLookup:
    name2iri: dict[str, str]

    def check_exists(self, name: str) -> bool:
        return name in self.name2iri.keys()

    def add_iri(self, name: str, iri: str) -> None:
        if self.check_exists(name):
            raise InternalError(f"Group with the name '{name}' already exists in the lookup.")
        self.name2iri[name] = iri

    def get_iri(self, name: str) -> str | None:
        return self.name2iri.get(name)


@dataclass
class CreatedIriCollection:
    classes: set[str] = field(default_factory=set)
    properties: set[str] = field(default_factory=set)

    def __post_init__(self) -> None:
        self.properties.update({f"{KNORA_API_STR}seqnum", f"{KNORA_API_STR}isPartOf"})


@dataclass
class ListNameToIriLookup:
    name2iri: dict[str, str]

    def check_list_exists(self, name: str) -> bool:
        return name in self.name2iri.keys()

    def add_iri(self, name: str, iri: str) -> None:
        if self.check_list_exists(name):
            raise InternalError(f"List with the name '{name}' already exists in the lookup.")
        self.name2iri[name] = iri

    def get_iri(self, name: str) -> str | None:
        return self.name2iri.get(name)
