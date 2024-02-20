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


def make_project_onto_information(
    default_onto_prefix: str,
    ontologies: dict[str, list[dict[str, Any]]],
) -> ProjectOntosInformation:
    """
    This function formats ontologies, that were returned by the dsp-api into a look-up model.

    Args:
        default_onto_prefix: prefix for the default ontology
        ontologies: ontologies returned from the dsp-api

    Returns:
        A look-up that contains the property and class names from each ontology
    """
    onto_dict = {
        onto_name: _extract_classes_properties_from_onto(onto_json) for onto_name, onto_json in ontologies.items()
    }
    return ProjectOntosInformation(default_onto_prefix, onto_dict)


def _extract_classes_properties_from_onto(onto_json: list[dict[str, Any]]) -> OntoInfo:
    """
    This function takes an ontology response from the DSP-API.
    It extracts the classes and properties.
    And saves them in an instance of the class Ontology.

    Args:
        onto_json: response from DSP-API

    Returns:
        Ontology instance with the classes and properties
    """
    classes = _get_all_cleaned_classes_from_json(onto_json)
    properties = _get_all_cleaned_properties_from_json(onto_json)
    return OntoInfo(classes, properties)


def _get_all_cleaned_classes_from_json(onto_json: list[dict[str, Any]]) -> list[str]:
    classes = _get_all_classes_from_json(onto_json)
    return _remove_prefixes(classes)


def _get_all_classes_from_json(onto_json: list[dict[str, Any]]) -> list[str]:
    return [elem["@id"] for elem in onto_json if elem.get("knora-api:isResourceClass")]


def _get_all_cleaned_properties_from_json(onto_json: list[dict[str, Any]]) -> list[str]:
    props = _get_all_properties_from_json(onto_json)
    return _remove_prefixes(props)


def _get_all_properties_from_json(onto_json: list[dict[str, Any]]) -> list[str]:
    return [elem["@id"] for elem in onto_json if not elem.get("knora-api:isResourceClass")]


def _remove_prefixes(ontology_elements: list[str]) -> list[str]:
    return [x.split(":")[1] for x in ontology_elements]
