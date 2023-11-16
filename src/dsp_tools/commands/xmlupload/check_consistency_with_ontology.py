# sourcery skip: use-fstring-for-concatenation

from lxml import etree

from dsp_tools.commands.xmlupload.ontology_client import OntologyClient, format_ontology
from dsp_tools.commands.xmlupload.ontology_diagnose_models import OntoDiagnoseTool, Ontology, UnknownOntologyElements
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
    onto_tool = OntoDiagnoseTool(
        default_ontology_prefix=onto_client.default_ontology,
        onto_lookup=_get_project_and_knora_ontology_from_server(onto_client),
        save_location=onto_client.save_location,
    )
    _iterate_over_xml_find_problems(root, onto_tool)


def _get_project_and_knora_ontology_from_server(onto_client: OntologyClient) -> dict[str, Ontology]:
    ontologies = onto_client.get_all_ontologies_from_server()
    return {onto_name: format_ontology(onto_graph) for onto_name, onto_graph in ontologies.items()}


def _iterate_over_xml_find_problems(root: etree._Element, onto_tool: OntoDiagnoseTool) -> None:
    unknown_eles = UnknownOntologyElements(save_path=onto_tool.save_location)
    for resource in root.iterchildren():
        if not _diagnose_classes(resource.tag, onto_tool):
            unknown_eles.classes.append((resource.attrib["id"], resource.attrib["restype"]))
        if problems := _diagnose_all_properties(resource, onto_tool):
            unknown_eles.properties.extend(problems)
    if unknown_eles.not_empty():
        unknown_eles.execute_problem_protocol()


def _diagnose_classes(class_str: str, onto_tool: OntoDiagnoseTool) -> bool:
    prefix, cls = _identify_ontology(class_str, onto_tool)
    return cls in onto_tool.onto_lookup[prefix].classes


def _diagnose_all_properties(resource: etree._Element, onto_tool: OntoDiagnoseTool) -> list[tuple[str, str]]:
    return [
        (resource.attrib["id"], prop.attrib["name"])
        for prop in resource.iterchildren()
        if not _diagnose_properties(prop.attrib["name"], onto_tool)
    ]


def _diagnose_properties(prop_str: str, onto_tool: OntoDiagnoseTool) -> bool:
    prefix, prop = _identify_ontology(prop_str, onto_tool)
    return prop in onto_tool.onto_lookup[prefix].properties


def _identify_ontology(prop_cls: str, onto_tool: OntoDiagnoseTool) -> tuple[str, ...]:
    if onto_tool.default_ontology_colon.match(prop_cls):
        return onto_tool.default_ontology_prefix, prop_cls.lstrip(":")
    elif onto_tool.knora_undeclared.match(prop_cls):
        return "knora-api", prop_cls
    elif onto_tool.generic_prefixed_ontology.match(prop_cls):
        return tuple(prop_cls.split(":"))
    else:
        raise BaseError(f"The input property or class: '{prop_cls}' does not follow a known ontology pattern.")
