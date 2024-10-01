from pathlib import Path

from lxml import etree
from rdflib import SH
from rdflib import Graph

from dsp_tools.commands.xml_validate.api_connection import OntologyConnection
from dsp_tools.commands.xml_validate.api_connection import ShaclValidator
from dsp_tools.commands.xml_validate.deserialise_input import deserialise_xml
from dsp_tools.commands.xml_validate.make_data_rdf import make_data_rdf
from dsp_tools.commands.xml_validate.models.data_deserialised import ProjectDeserialised
from dsp_tools.commands.xml_validate.models.data_rdf import DataRDF
from dsp_tools.commands.xml_validate.sparql.construct_shapes import construct_shapes_graph
from dsp_tools.utils.xml_utils import parse_xml_file
from dsp_tools.utils.xml_utils import remove_comments_from_element_tree
from dsp_tools.utils.xml_utils import transform_into_localnames
from dsp_tools.utils.xml_validation import validate_xml


def xml_validate(filepath: Path, api_url: str, shortcode: str) -> None:
    """
    Takes a file and project information and validates it against the ontologies on the server.

    Args:
        filepath: path to the xml data file
        api_url: url of the api host
        shortcode: shortcode of the project
    """
    onto_con = OntologyConnection(api_url, shortcode)
    data_rdf = _get_data_info_from_file(filepath, api_url)
    ontologies = _get_project_ontos(onto_con)
    shapes = construct_shapes_graph(ontologies)
    data_graph = data_rdf.make_graph() + ontologies
    val = ShaclValidator(api_url)
    shape_str = shapes.serialize(format="ttl")
    data_str = data_graph.serialize(format="ttl")
    result = val.validate(data_str, shape_str)
    conforms = next(result.objects(SH.conforms))
    if bool(conforms):
        print("Validation passed!")
    else:
        print("Validation errors found!")


def _get_project_ontos(onto_con: OntologyConnection) -> Graph:
    all_ontos = onto_con.get_ontologies()
    g = Graph()
    for onto in all_ontos:
        og = Graph()
        og.parse(data=onto, format="ttl")
        g += og
    return g


def _get_data_info_from_file(file: Path, api_url: str) -> DataRDF:
    cleaned_root = _parse_and_clean_file(file, api_url)
    deserialised: ProjectDeserialised = deserialise_xml(cleaned_root)
    rdf_data: DataRDF = make_data_rdf(deserialised.data)
    return rdf_data


def _parse_and_clean_file(file: Path, api_url: str) -> etree._Element:
    root = parse_xml_file(file)
    root = remove_comments_from_element_tree(root)
    validate_xml(root)
    root = transform_into_localnames(root)
    return _replace_namespaces(root, api_url)


def _replace_namespaces(root: etree._Element, api_url: str) -> etree._Element:
    with open("src/dsp_tools/resources/xml_validate/replace_namespace.xslt", "rb") as xslt_file:
        xslt_data = xslt_file.read()
    shortcode = root.attrib["shortcode"]
    default_ontology = root.attrib["default-ontology"]
    namespace = f"{api_url}/ontology/{shortcode}/{default_ontology}/v2#"
    xslt_root = etree.XML(xslt_data)
    transform = etree.XSLT(xslt_root)
    replacement_value = etree.XSLT.strparam(namespace)
    return transform(root, replacementValue=replacement_value).getroot()
