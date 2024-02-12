from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class OntoInfo:
    """This class saves the properties and the classes from an ontology."""

    classes: list[str] = field(default_factory=list)
    properties: list[str] = field(default_factory=list)


@dataclass
class ProjectOntosInformation:
    """This class saves information needed to check the consistency with the ontology."""

    default_ontology_prefix: str
    onto_lookup: dict[str, OntoInfo]


def extract_classes_properties_from_onto(onto_graph: list[dict[str, Any]]) -> OntoInfo:
    """
    This function takes an ontology graph from the DSP-API.
    It extracts the classes and properties.
    And saves them in an instance of the class Ontology.

    Args:
        onto_graph: graph from DSP-API

    Returns:
        Ontology instance with the classes and properties
    """
    classes = _get_all_cleaned_classes_from_graph(onto_graph)
    properties = _get_all_cleaned_properties_from_graph(onto_graph)
    return OntoInfo(classes, properties)


def _get_all_cleaned_classes_from_graph(onto_graph: list[dict[str, Any]]) -> list[str]:
    classes = _get_all_classes_from_graph(onto_graph)
    return _remove_prefixes(classes)


def _get_all_classes_from_graph(onto_graph: list[dict[str, Any]]) -> list[str]:
    return [elem["@id"] for elem in onto_graph if elem.get("knora-api:isResourceClass")]


def _get_all_cleaned_properties_from_graph(onto_graph: list[dict[str, Any]]) -> list[str]:
    props = _get_all_properties_from_graph(onto_graph)
    return _remove_prefixes(props)


def _get_all_properties_from_graph(onto_graph: list[dict[str, Any]]) -> list[str]:
    return [elem["@id"] for elem in onto_graph if not elem.get("knora-api:isResourceClass")]


def _remove_prefixes(ontology_elements: list[str]) -> list[str]:
    return [x.split(":")[1] for x in ontology_elements]
