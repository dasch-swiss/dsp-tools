# sourcery skip: use-fstring-for-concatenation
from pathlib import Path

import regex
from lxml import etree
from regex import Pattern

from dsp_tools.commands.xmlupload.models.ontology_diagnose_models import InvalidOntologyElements, OntoCheckInformation
from dsp_tools.commands.xmlupload.ontology_client import OntologyClient
from dsp_tools.models.exceptions import UserError

defaultOntologyColon: Pattern[str] = regex.compile(r"^:\w+$")
knoraUndeclared: Pattern[str] = regex.compile(r"^\w+$")
genericPrefixedOntology: Pattern[str] = regex.compile(r"^[\w\-]+:\w+$")


def do_xml_consistency_check(onto_client: OntologyClient, root: etree._Element) -> None:
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


def _find_problems_in_classes_and_properties(
    classes: dict[str, list[str]], properties: dict[str, list[str]], onto_check_info: OntoCheckInformation
) -> None:
    class_problems = _diagnose_all_classes(classes, onto_check_info)
    property_problems = _diagnose_all_properties(properties, onto_check_info)
    if not class_problems and not property_problems:
        return None
    problems = InvalidOntologyElements(classes=class_problems, properties=property_problems)
    msg, df = problems.execute_problem_protocol()
    if df:
        ex_name = "XML_syntax_errors.xlsx"
        df.to_excel(excel_writer=Path(onto_check_info.save_location, ex_name), sheet_name=" ", index=False)
        msg += (
            "\n\n---------------------------------------\n\n"
            f"\nAn excel: '{ex_name}' was saved at '{onto_check_info.save_location}' listing the problems."
        )
    raise UserError(msg)


def _get_all_classes_and_properties(root: etree._Element) -> tuple[dict[str, list[str]], dict[str, list[str]]]:
    cls_dict = _get_all_class_types_and_ids(root)
    prop_dict: dict[str, list[str]] = {}
    for resource in root.iterchildren(tag="resource"):
        prop_dict = _get_all_property_names_and_resource_ids_one_resource(resource, prop_dict)
    return cls_dict, prop_dict


def _get_all_class_types_and_ids(root: etree._Element) -> dict[str, list[str]]:
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


def _diagnose_all_classes(
    classes: dict[str, list[str]], onto_check_info: OntoCheckInformation
) -> list[tuple[str, list[str], str]]:
    problem_list = []
    for cls_type, ids in classes.items():
        if problem := _diagnose_class(cls_type, onto_check_info):
            problem_list.append((cls_type, ids, problem))
    return problem_list


def _diagnose_class(cls_type: str, onto_check_info: OntoCheckInformation) -> str | None:
    prefix, cls_ = _get_prefix_and_prop_or_cls_identifier(cls_type, onto_check_info.default_ontology_prefix)
    if not prefix:
        return "Property name does not follow a known ontology pattern"
    if onto := onto_check_info.onto_lookup.get(prefix):
        return "Invalid Class Type" if cls_ not in onto.classes else None
    else:
        return "Unknown ontology prefix"


def _diagnose_all_properties(
    properties: dict[str, list[str]], onto_check_info: OntoCheckInformation
) -> list[tuple[str, list[str], str]]:
    problem_list = []
    for prop_name, ids in properties.items():
        if problem := _diagnose_property(prop_name, onto_check_info):
            problem_list.append((prop_name, ids, problem))
    return problem_list


def _diagnose_property(prop_name: str, onto_check_info: OntoCheckInformation) -> str | None:
    prefix, prop = _get_prefix_and_prop_or_cls_identifier(prop_name, onto_check_info.default_ontology_prefix)
    if not prefix:
        return "Property name does not follow a known ontology pattern"
    if onto := onto_check_info.onto_lookup.get(prefix):
        return "Invalid Property" if prop not in onto.properties else None
    else:
        return "Unknown ontology prefix"


def _get_prefix_and_prop_or_cls_identifier(
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
