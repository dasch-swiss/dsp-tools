from pathlib import Path

from lxml import etree
from rdflib import Graph

from dsp_tools.commands.xml_validate.api_connection import OntologyConnection
from dsp_tools.commands.xml_validate.deserialise_input import deserialise_xml
from dsp_tools.commands.xml_validate.make_data_rdf import make_data_rdf
from dsp_tools.commands.xml_validate.models.data_deserialised import ProjectDeserialised
from dsp_tools.commands.xml_validate.models.data_deserialised import ProjectInformation
from dsp_tools.commands.xml_validate.models.data_rdf import DataRDF
from dsp_tools.utils.xml_utils import parse_xml_file
from dsp_tools.utils.xml_utils import remove_comments_from_element_tree
from dsp_tools.utils.xml_utils import transform_into_localnames
from dsp_tools.utils.xml_validation import validate_xml


def _get_project_ontos(onto_con: OntologyConnection) -> Graph:
    all_ontos = onto_con.get_ontologies()
    g = Graph()
    for onto in all_ontos:
        og = Graph()
        og.parse(data=onto, format="ttl")
        g += og
    return g


def _get_data_info_from_file(file: Path, api_url: str) -> tuple[ProjectInformation, DataRDF]:
    cleaned_root = _parse_and_clean_file(file, api_url)
    deserialised: ProjectDeserialised = deserialise_xml(cleaned_root)
    rdf_data: DataRDF = make_data_rdf(deserialised.data)
    return deserialised.info, rdf_data


def _parse_and_clean_file(file: Path, api_url: str) -> etree._Element:
    root = parse_xml_file(file)
    root = remove_comments_from_element_tree(root)
    validate_xml(root)
    root = transform_into_localnames(root)
    return _replace_namespaces(root, api_url)


def _replace_namespaces(root: etree._Element, api_url: str) -> etree._Element:
    with open("src/dsp_tools/resources/xml_validate/replace_namespace.xslt", "rb") as xslt_file:
        xslt_data = xslt_file.read()
    xslt_root = etree.XML(xslt_data)
    transform = etree.XSLT(xslt_root)
    replacement_value = etree.XSLT.strparam(api_url)
    return transform(root, replacementValue=replacement_value).getroot()
