from lxml import etree

from dsp_tools.commands.xmlupload.ontology_client import Ontology, OntologyClient, format_ontology


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
    out_ontologies = {}
    for onto_name, onto_graph in ontologies.items():
        out_ontologies[onto_name] = format_ontology(onto_graph)
    return out_ontologies


def _get_resource_class_from_root(root: etree._Element) -> set[str]:
    return {res.attrib["restype"] for res in list(root.getiterator(tag="resource"))}


def _get_all_properties_from_root(root: etree._Element) -> set[str]:
    resources = list(root.getiterator(tag="resource"))
    all_props = set()
    for resource in resources:
        all_props.update(_get_all_properties_from_one_resource(resource))
    return all_props


def _get_all_properties_from_one_resource(resource_ele: etree._Element) -> set[str]:
    props: set[etree._Element] = {prop for prop in list(resource_ele.iterchildren()) if prop.attrib.get("name")}
    return {prop.attrib["name"] for prop in props}
