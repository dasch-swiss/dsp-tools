# sourcery skip: use-fstring-for-concatenation

from dataclasses import dataclass, field

import regex
from regex import Pattern

from dsp_tools.commands.xmlupload.ontology_client import Ontology, OntologyClient, format_ontology
from dsp_tools.models.exceptions import BaseError


@dataclass
class OntoRegEx:
    """This class returns the regex for the ontology"""

    default_ontology_prefix: str
    default_ontology_colon: Pattern[str] = field(default=regex.compile(r"^:[A-Za-z]+$"))
    knora_undeclared: Pattern[str] = field(default=regex.compile(r"^[A-Za-z]+$"))
    generic_prefixed_ontology: Pattern[str] = field(default=regex.compile(r"^[A-Za-z]+-?[A-Za-z]+:[A-Za-z]+$"))


def get_project_and_knora_ontology_from_server(onto_client: OntologyClient) -> dict[str, Ontology]:
    """
    This function takes a connection to the server and the shortcode of a project.
    It retrieves the project ontologies and the knora-api ontology.
    Knora-api is saved with an empty string as a key.

    Args:
        onto_client: client for the ontology retrieval

    Returns:
        Dictionary with the ontology names as keys and the ontology in a structured manner as values.
    """

    ontologies = onto_client.get_all_ontologies_from_server()
    return {onto_name: format_ontology(onto_graph) for onto_name, onto_graph in ontologies.items()}


def _identify_ontology(prop_cls: str, onto_regex: OntoRegEx) -> tuple[str, ...]:
    if onto_regex.default_ontology_colon.match(prop_cls):
        return onto_regex.default_ontology_prefix, prop_cls.lstrip(":")
    elif onto_regex.knora_undeclared.match(prop_cls):
        return "knora-api", prop_cls
    elif onto_regex.generic_prefixed_ontology.match(prop_cls):
        return tuple(prop_cls.split(":"))
    else:
        raise BaseError(f"The input property or class: '{prop_cls}' does not follow a known ontology pattern.")


def _check_if_properties_exist(
    property_set: set[tuple[str, str]], onto_lookup: dict[str, Ontology]
) -> set[tuple] | None:
    return {x for x in property_set if x[1] not in onto_lookup[x[0]].properties}


def _check_if_classes_exist(property_set: set[tuple[str, str]], onto_lookup: dict[str, Ontology]) -> set[tuple] | None:
    return {x for x in property_set if x[1] not in onto_lookup[x[0]].classes}
