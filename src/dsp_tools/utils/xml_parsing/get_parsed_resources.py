from lxml import etree
from dsp_tools.utils.xml_parsing.models.parsed_resource import ParsedValue, ParsedResource, ParsedFileValue, ParsedFileValueMetadata, ParsedMigrationMetadata, KnoraValueType

from dsp_tools.utils.rdflib_constants import KNORA_API_STR

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
    pass



def _construct_namespace(api_url: str, shortcode: str, onto_name: str) -> str:
    return f"{api_url}/ontology/{shortcode}/{onto_name}/v2#"
