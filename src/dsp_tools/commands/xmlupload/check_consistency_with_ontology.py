# sourcery skip: use-fstring-for-concatenation

from lxml import etree

from dsp_tools.commands.xmlupload.models.ontology_diagnose_models import (
    InvalidOntologyElements,
    OntoCheckInformation,
    Ontology,
)
from dsp_tools.commands.xmlupload.ontology_client import OntologyClient, deserialize_ontology
from dsp_tools.models.exceptions import BaseError


def do_xml_consistency_check(onto_client: OntologyClient, root: etree._Element) -> None:
    """
    This function takes an OntologyClient and the root of an XML.
    It retrieves the ontologies from the server.
    It iterates over the root.
    If it finds any unknown properties or classes, they are printed out and a UserError is raised.

     Args:
         onto_client: client for the ontology retrieval
         root: root of the XML

     Raises:
         UserError: if there are any unknown properties or classes
    """
    onto_tool = OntoCheckInformation(
        default_ontology_prefix=onto_client.default_ontology,
        onto_lookup=_get_project_and_knora_ontology_from_server(onto_client),
        save_location=onto_client.save_location,
    )
    _find_problems_in_xml(root, onto_tool)


def _get_project_and_knora_ontology_from_server(onto_client: OntologyClient) -> dict[str, Ontology]:
    ontologies = onto_client.get_all_ontologies_from_server()
    return {onto_name: deserialize_ontology(onto_graph) for onto_name, onto_graph in ontologies.items()}


def _find_problems_in_xml(root: etree._Element, onto_tool: OntoCheckInformation) -> None:
    unknown_elems = InvalidOntologyElements(save_path=onto_tool.save_location)
    for resource in root.iterchildren():
        if not _diagnose_class(resource.tag, onto_tool):
            unknown_elems.classes.append((resource.attrib["id"], resource.attrib["restype"]))
        if problems := _diagnose_all_properties(resource, onto_tool):
            unknown_elems.properties.extend(problems)
    if unknown_elems.not_empty():
        unknown_elems.execute_problem_protocol()


def _diagnose_class(class_str: str, onto_tool: OntoCheckInformation) -> bool:
    prefix, cls_ = _get_prefix_and_prop_cls_identifier(class_str, onto_tool)
    return cls_ in onto_tool.onto_lookup[prefix].classes


def _diagnose_all_properties(resource: etree._Element, onto_tool: OntoCheckInformation) -> list[tuple[str, str]]:
    return [
        (resource.attrib["id"], prop.attrib["name"])
        for prop in resource.iterchildren()
        if not _diagnose_properties(prop.attrib["name"], onto_tool)
    ]


def _diagnose_properties(prop_str: str, onto_tool: OntoCheckInformation) -> bool:
    prefix, prop = _get_prefix_and_prop_cls_identifier(prop_str, onto_tool)
    return prop in onto_tool.onto_lookup[prefix].properties


def _get_prefix_and_prop_cls_identifier(prop_cls: str, onto_tool: OntoCheckInformation) -> tuple[str, ...]:
    if onto_tool.default_ontology_colon.match(prop_cls):
        return onto_tool.default_ontology_prefix, prop_cls.lstrip(":")
    elif onto_tool.knora_undeclared.match(prop_cls):
        return "knora-api", prop_cls
    elif onto_tool.generic_prefixed_ontology.match(prop_cls):
        return tuple(prop_cls.split(":"))
    else:
        raise BaseError(f"The input property or class: '{prop_cls}' does not follow a known ontology pattern.")
