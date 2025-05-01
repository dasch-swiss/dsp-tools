from pathlib import Path

from lxml import etree

from dsp_tools.error.exceptions import InputError
from dsp_tools.utils.xml_parsing.parse_clean_validate_xml import _parse_xml_file
from dsp_tools.utils.xml_parsing.parse_clean_validate_xml import _transform_into_localnames
from dsp_tools.xmllib.helpers import find_license_in_string


def convert_legal_metadata(
    input_file: Path,
    auth_prop: str,
    copy_prop: str,
    license_prop: str,
) -> None:
    root = _parse_xml_file(input_file)
    root = _transform_into_localnames(root)
    root_new = etree.ElementTree(_convert(root, auth_prop, copy_prop, license_prop))
    output_file = input_file.with_stem(f"{input_file.stem}_converted")
    root_new.write(output_file, pretty_print=True, xml_declaration=True, encoding="utf-8")


def _convert(
    root: etree._Element,
    auth_prop: str,
    copy_prop: str,
    license_prop: str,
) -> etree._Element:
    auth_text_to_id: dict[str, int] = {}

    for res in root.iterchildren(tag="resource"):
        if not (media_tag_candidates := res.xpath("bitstream|iiif-uri")):
            continue
        media_elem = media_tag_candidates[0]
        copy_text = res.xpath(f"./text-prop[@name='{copy_prop}']/text/text()")[0]
        license_text = res.xpath(f"./text-prop[@name='{license_prop}']/text/text()")[0]
        auth_text = res.xpath(f"./text-prop[@name='{auth_prop}']/text/text()")[0]
        if not (auth_id := auth_text_to_id.get(auth_text)):
            auth_id = len(auth_text_to_id)
            auth_text_to_id[auth_text] = auth_id
        media_elem.attrib["authorship-id"] = f"authorship_{auth_id}"
        media_elem.attrib["copyright-holder"] = copy_text
        if not (lic := find_license_in_string(license_text)):
            raise InputError(f"Resource {res.attrib['id']} has invalid license {license_text}")
        media_elem.attrib["license"] = lic.value


    
    return root
