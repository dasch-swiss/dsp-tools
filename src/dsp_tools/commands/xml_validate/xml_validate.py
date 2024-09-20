from pathlib import Path

from lxml import etree

from dsp_tools.commands.xml_validate.models.data_rdf import DataRDF
from dsp_tools.commands.xml_validate.reformat_input import to_data_rdf
from dsp_tools.utils.xml_utils import parse_xml_file
from dsp_tools.utils.xml_utils import remove_comments_from_element_tree
from dsp_tools.utils.xml_utils import remove_qnames_and_transform_special_tags
from dsp_tools.utils.xml_validation import validate_xml


def _deserialise_file(file: Path, ontology_name: str) -> DataRDF:
    """Returns an object which follows the structure of the XML closely"""
    root = _parse_and_clean_file(file, ontology_name)
    return to_data_rdf(root)


def _parse_and_clean_file(file: Path, ontology_name: str) -> etree._Element:
    root = parse_xml_file(file)
    root = remove_comments_from_element_tree(root)
    validate_xml(root)
    root = remove_qnames_and_transform_special_tags(root)
    return _replace_namespaces(root, ontology_name)


def _replace_namespaces(root: etree._Element, ontology_namespace: str) -> etree._Element:
    with open("src/dsp_tools/resources/xml_validate/replace_namespace.xslt", "rb") as xslt_file:
        xslt_data = xslt_file.read()
    xslt_root = etree.XML(xslt_data)
    transform = etree.XSLT(xslt_root)
    replacement_value = etree.XSLT.strparam(ontology_namespace)
    return transform(root, replacementValue=replacement_value).getroot()
