# sourcery skip: use-fstring-for-concatenation
import regex
from lxml import etree
from regex import Pattern

from dsp_tools.commands.xmlupload.models.ontology_diagnose_models import InvalidOntologyElements, OntoCheckInformation
from dsp_tools.commands.xmlupload.ontology_client import OntologyClientLive
from dsp_tools.models.exceptions import BaseError

defaultOntologyColon: Pattern[str] = regex.compile(r"^:\w+$")
knoraUndeclared: Pattern[str] = regex.compile(r"^\w+$")
genericPrefixedOntology: Pattern[str] = regex.compile(r"^[A-Za-z]+-?[A-Za-z]+:\w+$")


def do_xml_consistency_check(onto_client: OntologyClientLive, root: etree._Element) -> None:
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
    onto_check_info = OntoCheckInformation(
        default_ontology_prefix=onto_client.default_ontology,
        onto_lookup=onto_client.get_all_ontologies_from_server(),
        save_location=onto_client.save_location,
    )
    classes, properties = _get_all_classes_and_properties(root)
    _find_problems_in_classes_and_properties(classes, properties, onto_check_info)


def _get_all_classes_and_properties(root: etree._Element) -> tuple[list[list[str]], list[list[str]]]:
    classes = _get_all_class_types_and_ids(root)
    properties = []
    for resource in root.iterchildren(tag="resource"):
        properties.extend(_get_all_property_names_and_resource_ids(resource))
    return classes, properties


def _get_all_class_types_and_ids(root: etree._Element) -> list[list[str]]:
    return [[resource.attrib["id"], resource.attrib["restype"]] for resource in root.iterchildren(tag="resource")]


def _get_all_property_names_and_resource_ids(resource: etree._Element) -> list[list[str]]:
    return [[resource.attrib["id"], prop.attrib["name"]] for prop in resource.iterchildren() if prop.tag != "bitstream"]


def _find_problems_in_classes_and_properties(
    classes: list[list[str]], properties: list[list[str]], onto_check_info: OntoCheckInformation
) -> None:
    class_problems = _diagnose_all_classes(classes, onto_check_info)
    property_problems = _diagnose_all_properties(properties, onto_check_info)
    if not class_problems and not property_problems:
        return None
    problems = InvalidOntologyElements(
        save_path=onto_check_info.save_location, classes=class_problems, properties=property_problems
    )
    problems.execute_problem_protocol()


def _diagnose_all_classes(classes: list[list[str]], onto_check_info: OntoCheckInformation) -> list[list[str]]:
    problem_list = []
    for prop_info in classes:
        if problem := _diagnose_class(prop_info, onto_check_info):
            problem_list.append(problem)
    return problem_list


def _diagnose_class(class_info: list[str], onto_check_info: OntoCheckInformation) -> list[str] | None:
    try:
        prefix, cls_ = _get_prefix_and_prop_cls_identifier(class_info[1], onto_check_info.default_ontology_prefix)
    except BaseError:
        class_info.append("Resource type does not follow a known ontology pattern")
        return class_info
    try:
        if cls_ not in onto_check_info.onto_lookup[prefix].classes:
            class_info.append("Invalid Class Type")
            return class_info
        return None
    except KeyError:
        class_info.append("Unknown ontology prefix")
        return class_info


def _diagnose_all_properties(properties: list[list[str]], onto_check_info: OntoCheckInformation) -> list[list[str]]:
    problem_list = []
    for prop_info in properties:
        if problem := _diagnose_properties(prop_info, onto_check_info):
            problem_list.append(problem)
    return problem_list


def _diagnose_properties(prop_info: list[str], onto_check_info: OntoCheckInformation) -> list[str] | None:
    try:
        prefix, prop = _get_prefix_and_prop_cls_identifier(prop_info[1], onto_check_info.default_ontology_prefix)
    except BaseError:
        prop_info.append("Property name does not follow a known ontology pattern")
        return prop_info
    try:
        if prop not in onto_check_info.onto_lookup[prefix].properties:
            prop_info.append("Invalid Property")
            return prop_info
        return None
    except KeyError:
        prop_info.append("Unknown ontology prefix")
        return prop_info


def _get_prefix_and_prop_cls_identifier(prop_cls: str, default_ontology_prefix: str) -> tuple[str, ...]:
    if defaultOntologyColon.match(prop_cls):
        return default_ontology_prefix, prop_cls.lstrip(":")
    elif knoraUndeclared.match(prop_cls):
        return "knora-api", prop_cls
    elif genericPrefixedOntology.match(prop_cls):
        return tuple(prop_cls.split(":"))
    else:
        raise BaseError(f"The input property or class: '{prop_cls}' does not follow a known ontology pattern.")
