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
) -> bool:
    root = _parse_xml_file(input_file)
    root = _transform_into_localnames(root)
    root_new = etree.ElementTree(_convert(root, auth_prop, copy_prop, license_prop))
    output_file = input_file.with_stem(f"{input_file.stem}_converted")
    root_new.write(output_file, pretty_print=True, encoding="utf-8", doctype='<?xml version="1.0" encoding="UTF-8"?>')
    return True


def _convert(
    root: etree._Element,
    auth_prop: str | None = None,
    copy_prop: str | None = None,
    license_prop: str | None = None,
) -> etree._Element:
    if not any([auth_prop, copy_prop, license_prop]):
        raise InputError("At least one of auth_prop, copy_prop, license_prop must be provided")

    auth_text_to_id: dict[str, int] = {}

    for res in root.iterchildren(tag="resource"):
        if not (media_tag_candidates := res.xpath("bitstream|iiif-uri")):
            continue
        media_elem = media_tag_candidates[0]
        if auth_prop:
            _handle_auth(res, auth_text_to_id, media_elem, auth_prop)
        if copy_prop:
            _handle_copy(res, media_elem, copy_prop)
        if license_prop:
            _handle_license(res, media_elem, license_prop)

    if auth_text_to_id:
        _add_auth_defs(root, auth_text_to_id)

    return root


def _handle_auth(
    res: etree._Element,
    auth_text_to_id: dict[str, int],
    media_elem: etree._Element,
    auth_prop: str,
) -> None:
    auth_elems: list[etree._Element] = res.xpath(f"./text-prop[@name='{auth_prop}']/text")
    if not auth_elems:
        return
    if len(auth_elems) > 1:
        raise InputError(f"Resource {res.attrib['id']} has more than one author. This is not implemented yet.")
    auth_elem = auth_elems[0]
    if not auth_elem.text or not (auth_text := auth_elem.text.strip()):
        raise InputError(f"Resource {res.attrib['id']} has an empty authorship")
    if (auth_id := auth_text_to_id.get(auth_text)) is None:
        auth_id = len(auth_text_to_id)
        auth_text_to_id[auth_text] = auth_id
    media_elem.attrib["authorship-id"] = f"authorship_{auth_id}"
    res.remove(auth_elem.getparent())  # type: ignore[arg-type]


def _handle_copy(res: etree._Element, media_elem: etree._Element, copy_prop: str) -> None:
    copy_elems: list[etree._Element] = res.xpath(f"./text-prop[@name='{copy_prop}']/text")
    if not copy_elems:
        return
    if len(copy_elems) > 1:
        raise InputError(f"Resource {res.attrib['id']} has more than one copyright")
    copy_elem = copy_elems[0]
    if not copy_elem.text or not (copy_text := copy_elem.text.strip()):
        raise InputError(f"Resource {res.attrib['id']} has an empty copyright")
    media_elem.attrib["copyright-holder"] = copy_text
    res.remove(copy_elem.getparent())  # type: ignore[arg-type]


def _handle_license(res: etree._Element, media_elem: etree._Element, license_prop: str) -> None:
    license_elems: list[etree._Element] = res.xpath(f"./text-prop[@name='{license_prop}']/text")
    if not license_elems:
        return
    if len(license_elems) > 1:
        raise InputError(f"Resource {res.attrib['id']} has more than one license")
    license_elem = license_elems[0]
    if not (lic := find_license_in_string(str(license_elem.text))):
        raise InputError(f"Resource {res.attrib['id']} has an invalid license: {license_elem.text}")
    media_elem.attrib["license"] = lic.value
    res.remove(license_elem.getparent())  # type: ignore[arg-type]


def _add_auth_defs(root: etree._Element, auth_text_to_id: dict[str, int]) -> None:
    auth_defs = []
    for auth_text, auth_id in auth_text_to_id.items():
        auth_def = etree.Element(
            "authorship",
            attrib={"id": f"authorship_{auth_id}"},
        )
        auth_child = etree.Element("author")
        auth_child.text = auth_text
        auth_def.append(auth_child)
        auth_defs.append(auth_def)
    for auth_def in reversed(auth_defs):
        root.insert(0, auth_def)
