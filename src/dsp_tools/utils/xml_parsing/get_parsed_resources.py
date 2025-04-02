from lxml import etree

from dsp_tools.error.exceptions import InputError
from dsp_tools.utils.rdflib_constants import KNORA_API_STR
from dsp_tools.utils.xml_parsing.models.parsed_resource import ParsedFileValue
from dsp_tools.utils.xml_parsing.models.parsed_resource import ParsedResource
from dsp_tools.utils.xml_parsing.models.parsed_resource import ParsedValue


def get_parsed_resources(root: etree._Element, api_url: str) -> list[ParsedResource]:
    pass


def _parse_one_resource(resource: etree._Element) -> ParsedResource:
    pass


def _parse_segment(segment: etree._Element, segment_type: str) -> ParsedResource:
    pass


def _parse_values(values: etree._Element) -> list[ParsedValue]:
    pass


def _parse_file_values(file_value: etree._Element) -> ParsedFileValue:
    pass


def _create_namespace_lookup(root: etree._Element, api_url: str) -> dict[str, str]:
    shortcode = root.attrib["shortcode"]
    default_ontology = root.attrib["default-ontology"]
    local_names = [ele.attrib["restype"] for ele in root.iterdescendants(tag="resource")]
    props = [ele.attrib["name"] for ele in root.iter() if "name" in ele.attrib]
    local_names.extend(props)
    local_names = set(local_names)
    lookup = {local: _get_one_absolute_iri(local, shortcode, default_ontology, api_url) for local in local_names}
    return lookup


def _get_one_absolute_iri(local_name: str, shortcode: str, default_ontology: str, api_url: str) -> str:
    split_name = local_name.split(":")
    if len(split_name) == 1:
        return f"{KNORA_API_STR}{local_name}"
    if len(split_name) == 2:
        if len(split_name[0]) == 0:
            return f"{_construct_namespace(api_url, shortcode, default_ontology)}{split_name[1]}"
        if split_name[0] == "knora-api":
            return f"{KNORA_API_STR}{split_name[1]}"
        return f"{_construct_namespace(api_url, shortcode, split_name[0])}{split_name[1]}"
    raise InputError(
        f"It is not permissible to have a colon in a property or resource class name. "
        f"Please correct the following: {local_name}"
    )


def _construct_namespace(api_url: str, shortcode: str, onto_name: str) -> str:
    return f"{api_url}/ontology/{shortcode}/{onto_name}/v2#"
