from dataclasses import dataclass
from dataclasses import field
from typing import Any
from typing import Literal

import regex


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
    This function formats ontologies returned by the dsp-api into a look-up model.

    Args:
        default_onto_prefix: prefix for the default ontology
        ontologies: ontologies returned from the dsp-api

    Returns:
        A look-up that contains the property and class names from each ontology
    """
    onto_dict = {
        onto_name: _extract_classes_and_properties_from_onto(onto_json) for onto_name, onto_json in ontologies.items()
    }
    return ProjectOntosInformation(default_onto_prefix, onto_dict)


def _extract_classes_and_properties_from_onto(onto_json: list[dict[str, Any]]) -> OntoInfo:
    """
    This function takes an ontology response from the DSP-API.
    It extracts the classes and properties.
    And saves them in an instance of the class Ontology.

    Args:
        onto_json: response from DSP-API

    Returns:
        Ontology instance with the classes and properties
    """
    classes = _get_all_cleaned_classes_from_onto(onto_json)
    properties = _get_all_cleaned_properties_from_onto(onto_json)
    return OntoInfo(classes, properties)


def _get_all_cleaned_classes_from_onto(onto_json: list[dict[str, Any]]) -> list[str]:
    classes = _get_all_classes_from_onto(onto_json)
    return _remove_prefixes(classes)


def _get_all_classes_from_onto(onto_json: list[dict[str, Any]]) -> list[str]:
    return [elem["@id"] for elem in onto_json if elem.get("knora-api:isResourceClass")]


def _get_all_cleaned_properties_from_onto(onto_json: list[dict[str, Any]]) -> list[str]:
    props = _get_all_properties_from_onto(onto_json)
    return _remove_prefixes(props)


def _get_all_properties_from_onto(onto_json: list[dict[str, Any]]) -> list[str]:
    return [elem["@id"] for elem in onto_json if not elem.get("knora-api:isResourceClass")]


def _remove_prefixes(ontology_elements: list[str]) -> list[str]:
    return [x.split(":")[1] for x in ontology_elements]


AllowedEncodings = Literal["utf8", "xml"]


@dataclass
class TextValueData:
    resource_id: str
    property_name: str
    encoding: AllowedEncodings


@dataclass
class PropertyTextValueTypes:
    """
    This class contains the information
    which properties have which type of encoding for a TextValue property in the ontology.
    """

    formatted_text_props: set[str] = field(default_factory=set)
    unformatted_text_props: set[str] = field(default_factory=set)


def get_text_value_types_of_properties_from_onto(
    onto_json_dict: dict[str, list[dict[str, Any]]], default_onto: str
) -> PropertyTextValueTypes:
    """
    This function takes a dict with the project ontologies in the format:
        { ontology_name: ontology_json_from_api }
    It retrieves the properties that are used with `knora-api:TextValue`.
    They are separated into two categories: xml encoded ones, and utf8 encoded ones.

    Args:
        onto_json_dict: dict with the project ontologies
        default_onto: name of the default ontology

    Returns:
        Look-up containing the properties separated according to the formatting
    """
    all_props = []
    for onto_json in onto_json_dict.values():
        all_props.extend(_get_all_text_value_types_properties_and_from_onto(onto_json))
    return _make_text_value_property_type_lookup(all_props, default_onto)


def _make_text_value_property_type_lookup(
    prop_list: list[tuple[str, str]], default_onto: str
) -> PropertyTextValueTypes:
    formatted_text = {
        _remove_default_prefix(p, default_onto) for p, _type in prop_list if _type == "salsah-gui:Richtext"
    }
    formatted_text.add("hasComment")  # this is a knora-api property that can be used directly
    unformatted_text = {
        _remove_default_prefix(p, default_onto) for p, _type in prop_list if _type != "salsah-gui:Richtext"
    }
    return PropertyTextValueTypes(formatted_text, unformatted_text)


def _remove_default_prefix(prop_str: str, default_onto: str) -> str:
    return regex.sub(rf"^{default_onto}:", ":", prop_str)


def _get_all_text_value_types_properties_and_from_onto(onto_json: list[dict[str, Any]]) -> list[tuple[str, str]]:
    prop_id_list = [elem["@id"] for elem in onto_json if _check_if_text_value_property(elem)]
    type_list = [elem["salsah-gui:guiElement"]["@id"] for elem in onto_json if _check_if_text_value_property(elem)]
    return list(zip(prop_id_list, type_list))


def _check_if_text_value_property(onto_ele: dict[str, Any]) -> bool:
    if not onto_ele.get("knora-api:isResourceProperty"):
        return False
    if not (object_type := onto_ele.get("knora-api:objectType")):
        return False
    match object_type["@id"]:
        case "knora-api:TextValue":
            return True
        case _:
            return False
