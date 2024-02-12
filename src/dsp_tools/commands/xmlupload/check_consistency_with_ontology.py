from datetime import datetime
from pathlib import Path

import regex
from lxml import etree
from regex import Pattern

from dsp_tools.commands.xmlupload.models.ontology_lookup_models import ProjectOntosInformation
from dsp_tools.commands.xmlupload.models.ontology_problem_models import (
    InvalidOntologyElementsInData,
)
from dsp_tools.commands.xmlupload.ontology_client import OntologyClient
from dsp_tools.models.exceptions import UserError

defaultOntologyColon: Pattern[str] = regex.compile(r"^:\w+$")
knoraUndeclared: Pattern[str] = regex.compile(r"^\w+$")
genericPrefixedOntology: Pattern[str] = regex.compile(r"^[\w\-]+:\w+$")


def do_xml_consistency_check_with_ontology(onto_client: OntologyClient, root: etree._Element) -> None:
    """
    This function takes an OntologyClient and the root of an XML.
    It retrieves the ontologies from the server.
    It iterates over the root.
    If it finds any invalid properties or classes, they are printed out and a UserError is raised.

     Args:
         onto_client: client for the ontology retrieval
         root: root of the XML

     Raises:
         UserError: if there are any invalid properties or classes
    """
    onto_check_info = ProjectOntosInformation(
        default_ontology_prefix=onto_client.default_ontology,
        onto_lookup=onto_client.get_all_ontologies_from_server(),
    )
    classes_in_data, properties_in_data = _get_all_classes_and_properties_from_data(root)
    _find_if_all_classes_and_properties_exist_in_onto(classes_in_data, properties_in_data, onto_check_info)


def _find_if_all_classes_and_properties_exist_in_onto(
    classes_in_data: dict[str, list[str]],
    properties_in_data: dict[str, list[str]],
    onto_check_info: ProjectOntosInformation,
) -> None:
    class_problems = _check_if_all_class_types_exist(classes_in_data, onto_check_info)
    property_problems = _check_if_all_properties_exist(properties_in_data, onto_check_info)
    if not class_problems and not property_problems:
        return None
    problems = InvalidOntologyElementsInData(
        classes=class_problems, properties=property_problems, ontos_on_server=list(onto_check_info.onto_lookup.keys())
    )
    msg, df = problems.execute_problem_protocol()
    if df is not None:
        csv_file = f"XML_syntax_errors_{datetime.now().strftime('%Y-%m-%d_%H%M%S')}.csv"
        df.to_csv(path_or_buf=Path(Path.cwd(), csv_file), index=False)
        msg += (
            "\n\n---------------------------------------\n\n"
            f"\nAll the problems are listed in the file: '{Path.cwd()}/{csv_file}'"
        )
    raise UserError(msg)


def _get_all_classes_and_properties_from_data(
    root: etree._Element,
) -> tuple[dict[str, list[str]], dict[str, list[str]]]:
    cls_dict = _get_all_class_types_and_ids_from_data(root)
    prop_dict: dict[str, list[str]] = {}
    for resource in root.iterchildren(tag="resource"):
        prop_dict = _get_all_property_names_and_resource_ids_one_resource(resource, prop_dict)
    return cls_dict, prop_dict


def _get_all_class_types_and_ids_from_data(root: etree._Element) -> dict[str, list[str]]:
    cls_dict: dict[str, list[str]] = {}
    for resource in root.iterchildren(tag="resource"):
        restype = resource.attrib["restype"]
        if restype in cls_dict:
            cls_dict[restype].append(resource.attrib["id"])
        else:
            cls_dict[restype] = [resource.attrib["id"]]
    return cls_dict


def _get_all_property_names_and_resource_ids_one_resource(
    resource: etree._Element, prop_dict: dict[str, list[str]]
) -> dict[str, list[str]]:
    for prop in resource.iterchildren():
        if prop.tag != "bitstream":
            prop_name = prop.attrib["name"]
            if prop_name in prop_dict:
                prop_dict[prop_name].append(resource.attrib["id"])
            else:
                prop_dict[prop_name] = [resource.attrib["id"]]
    return prop_dict


def _check_if_all_class_types_exist(
    classes: dict[str, list[str]], onto_check_info: ProjectOntosInformation
) -> list[tuple[str, list[str], str]]:
    problem_list = []
    for cls_type, ids in classes.items():
        if problem := _check_if_one_class_type_exists(cls_type, onto_check_info):
            problem_list.append((cls_type, ids, problem))
    return problem_list


def _check_if_one_class_type_exists(cls_type: str, onto_check_info: ProjectOntosInformation) -> str | None:
    prefix, cls_ = _get_separate_prefix_and_iri_from_onto_prop_or_cls(cls_type, onto_check_info.default_ontology_prefix)
    if not prefix:
        return "Property name does not follow a known ontology pattern"
    if onto := onto_check_info.onto_lookup.get(prefix):
        return "Invalid Class Type" if cls_ not in onto.classes else None
    else:
        return "Unknown ontology prefix"


def _check_if_all_properties_exist(
    properties: dict[str, list[str]], onto_check_info: ProjectOntosInformation
) -> list[tuple[str, list[str], str]]:
    problem_list = []
    for prop_name, ids in properties.items():
        if problem := _check_if_one_property_exists(prop_name, onto_check_info):
            problem_list.append((prop_name, ids, problem))
    return problem_list


def _check_if_one_property_exists(prop_name: str, onto_check_info: ProjectOntosInformation) -> str | None:
    prefix, prop = _get_separate_prefix_and_iri_from_onto_prop_or_cls(
        prop_name, onto_check_info.default_ontology_prefix
    )
    if not prefix:
        return "Property name does not follow a known ontology pattern"
    if onto := onto_check_info.onto_lookup.get(prefix):
        return "Invalid Property" if prop not in onto.properties else None
    else:
        return "Unknown ontology prefix"


def _get_separate_prefix_and_iri_from_onto_prop_or_cls(
    prop_or_cls: str, default_ontology_prefix: str
) -> tuple[str, ...] | tuple[None, None]:
    if defaultOntologyColon.match(prop_or_cls):
        return default_ontology_prefix, prop_or_cls.lstrip(":")
    elif knoraUndeclared.match(prop_or_cls):
        return "knora-api", prop_or_cls
    elif genericPrefixedOntology.match(prop_or_cls):
        return tuple(prop_or_cls.split(":"))
    else:
        return None, None
