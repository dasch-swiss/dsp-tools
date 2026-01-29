from dataclasses import dataclass
from dataclasses import field

from rdflib import Literal
from rdflib import URIRef

from dsp_tools.error.exceptions import InternalError
from dsp_tools.utils.rdf_constants import KNORA_API_PREFIX


@dataclass
class ProjectIriLookup:
    project_iri: str
    onto_iris: dict[str, str] = field(default_factory=dict)

    def add_onto(self, name: str, iri: str) -> None:
        self.onto_iris[name] = iri

    def does_onto_exist(self, name: str) -> bool:
        return bool(self.onto_iris.get(name))


@dataclass
class OntoLastModDateLookup:
    project_iri: str
    onto_iris: dict[str, URIRef]
    iri_to_last_modification_date: dict[str, Literal] = field(default_factory=dict)

    def get_last_mod_date(self, iri: str) -> Literal:
        return self.iri_to_last_modification_date[iri]

    def update_last_mod_date(self, iri: str, last_modification_date: Literal) -> None:
        self.iri_to_last_modification_date[iri] = last_modification_date


@dataclass
class GroupNameToIriLookup:
    name2iri: dict[str, str]
    shortname: str

    def check_exists(self, name: str) -> bool:
        return name in self.name2iri.keys()

    def add_iri(self, name: str, iri: str) -> None:
        if self.check_exists(name):
            raise InternalError(f"Group with the name '{name}' already exists in the lookup.")
        self.name2iri[name] = iri
        self.name2iri[f"{self.shortname}:{name}"] = iri

    def get_iri(self, name: str) -> str | None:
        return self.name2iri.get(name)


@dataclass
class UserNameToIriLookup:
    name2iri: dict[str, str] = field(default_factory=dict)

    def check_exists(self, name: str) -> bool:
        return name in self.name2iri.keys()

    def add_iri(self, name: str, iri: str) -> None:
        if self.check_exists(name):
            raise InternalError(f"User with the name '{name}' already exists in the lookup.")
        self.name2iri[name] = iri

    def get_iri(self, name: str) -> str | None:
        return self.name2iri.get(name)


@dataclass
class CreatedIriCollection:
    created_classes: set[str] = field(default_factory=set)
    created_properties: set[str] = field(default_factory=set)
    failed_classes: set[str] = field(default_factory=set)
    failed_properties: set[str] = field(default_factory=set)

    def __post_init__(self) -> None:
        self.created_properties.update({f"{KNORA_API_PREFIX}seqnum", f"{KNORA_API_PREFIX}isPartOf"})

    def any_properties_failed(self, props: set[str]) -> bool:
        return bool(props.intersection(self.failed_properties))

    def any_classes_failed(self, classes: set[str]) -> bool:
        return bool(classes.intersection(self.failed_classes))


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
