from pathlib import Path

from lxml import etree

from dsp_tools.commands.xml_validate.deserialise_input import deserialise_xml
from dsp_tools.commands.xml_validate.make_data_rdf import make_data_rdf
from dsp_tools.commands.xml_validate.models.data_deserialised import ProjectDeserialised
from dsp_tools.commands.xml_validate.models.data_deserialised import ProjectInformation
from dsp_tools.commands.xml_validate.models.data_rdf import DataRDF
from dsp_tools.utils.xml_utils import parse_xml_file
from dsp_tools.utils.xml_utils import remove_comments_from_element_tree
from dsp_tools.utils.xml_utils import transform_into_localnames
from dsp_tools.utils.xml_validation import validate_xml


def _get_data_info_from_file(file: Path, namespace: str) -> tuple[ProjectInformation, DataRDF]:
    cleaned_root = _parse_and_clean_file(file, namespace)
    deserialised: ProjectDeserialised = deserialise_xml(cleaned_root)
    rdf_data: DataRDF = make_data_rdf(deserialised.data)
    return deserialised.info, rdf_data


def _parse_and_clean_file(file: Path, namespace: str) -> etree._Element:
    root = parse_xml_file(file)
    root = remove_comments_from_element_tree(root)
    validate_xml(root)
    root = transform_into_localnames(root)
    return _replace_namespaces(root, namespace)


def _replace_namespaces(root: etree._Element, ontology_namespace: str) -> etree._Element:
    with open("src/dsp_tools/resources/xml_validate/replace_namespace.xslt", "rb") as xslt_file:
        xslt_data = xslt_file.read()
    xslt_root = etree.XML(xslt_data)
    transform = etree.XSLT(xslt_root)
    replacement_value = etree.XSLT.strparam(ontology_namespace)
    return transform(root, replacementValue=replacement_value).getroot()
