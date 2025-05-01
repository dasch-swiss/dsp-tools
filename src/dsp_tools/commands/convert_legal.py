from pathlib import Path

from lxml import etree

from dsp_tools.utils.xml_parsing.parse_clean_validate_xml import _parse_xml_file
from dsp_tools.utils.xml_parsing.parse_clean_validate_xml import _transform_into_localnames


def convert_legal_metadata(
    input_file: Path,
    auth_prop: str,
    copy_prop: str,
    license_prop: str,
) -> None:
    root = _parse_xml_file(input_file)
    root = _transform_into_localnames(root)


def _convert(root: etree._Element) -> etree._Element:
    auth_id_to_text: dict[str, str] = {}

    for elem in root.iterchildren(tag="resource"):
        if media_tag := elem.find(path=".bitstream|.iiif-uri"):
            print(media_tag)
    
    return root
