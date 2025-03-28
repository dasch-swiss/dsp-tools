from __future__ import annotations

from pathlib import Path

import regex
from lxml import etree

from dsp_tools.error.exceptions import InputError
from dsp_tools.utils.data_formats.iri_util import is_resource_iri
from dsp_tools.utils.xml_parsing.parse_xml import parse_xml_file
from dsp_tools.utils.xml_parsing.transform import remove_comments_from_element_tree
from dsp_tools.utils.xml_parsing.transform import transform_special_tags_make_localname
from dsp_tools.utils.xml_parsing.xml_schema_validation import validate_xml_with_schema


def prepare_input_xml_file(input_file: Path, imgdir: str) -> tuple[etree._Element, str, str]:
    """
    Parses the file and does some rudimentary checks.

    Args:
        input_file: input XML
        imgdir: directory of the images

    Returns:
        The root element of the parsed XML file, the shortcode, and the default ontology
    """
    root, shortcode, default_ontology = validate_and_parse(input_file)
    check_if_bitstreams_exist(root, imgdir)
    return root, shortcode, default_ontology


def validate_and_parse(input_file: Path) -> tuple[etree._Element, str, str]:
    """Parse and validate an XML file.

    Args:
        input_file: Path to the XML file

    Returns:
        The root element of the parsed XML file, the shortcode, and the default ontology
    """
    root = parse_xml_file(input_file)
    root = remove_comments_from_element_tree(root)

    validate_xml_with_schema(root)
    print("The XML file is syntactically correct.")
    root = transform_special_tags_make_localname(root)
    _check_if_link_targets_exist(root)
    shortcode = root.attrib["shortcode"]
    default_ontology = root.attrib["default-ontology"]
    return root, shortcode, default_ontology


def _check_if_link_targets_exist(root: etree._Element) -> None:
    """
    Make sure that all targets of links (resptr and salsah-links)
    are either IRIs or IDs that exist in the present XML file.

    Args:
        root: parsed XML file

    Raises:
        InputError: if a link target does not exist in the XML file
    """
    resptr_errors = _check_if_resptr_targets_exist(root)
    salsah_errors = _check_if_salsah_targets_exist(root)
    if errors := resptr_errors + salsah_errors:
        sep = "\n - "
        msg = f"It is not possible to upload the XML file, because it contains invalid links:{sep}{sep.join(errors)}"
        raise InputError(msg)


def _check_if_resptr_targets_exist(root: etree._Element) -> list[str]:
    link_values = [x for x in root.iter() if x.tag == "resptr"]
    resource_ids = [x.attrib["id"] for x in root.iter() if x.tag == "resource"]
    invalid_link_values = [x for x in link_values if x.text not in resource_ids]
    invalid_link_values = [x for x in invalid_link_values if not is_resource_iri(str(x.text))]
    errors = []
    for inv in invalid_link_values:
        prop_name = next(inv.iterancestors(tag="resptr-prop")).attrib["name"]
        res_id = next(inv.iterancestors(tag="resource")).attrib["id"]
        errors.append(f"Resource '{res_id}', property '{prop_name}' has an invalid link target '{inv.text}'")
    return errors


def _check_if_salsah_targets_exist(root: etree._Element) -> list[str]:
    link_values = [x for x in root.iter() if x.tag == "a"]
    resource_ids = [x.attrib["id"] for x in root.iter() if x.tag == "resource"]
    invalid_link_values = [x for x in link_values if regex.sub(r"IRI:|:IRI", "", x.attrib["href"]) not in resource_ids]
    invalid_link_values = [x for x in invalid_link_values if x.attrib.get("class") == "salsah-link"]
    invalid_link_values = [x for x in invalid_link_values if not is_resource_iri(x.attrib["href"])]
    errors = []
    for inv in invalid_link_values:
        prop_name = next(inv.iterancestors(tag="text-prop")).attrib["name"]
        res_id = next(inv.iterancestors(tag="resource")).attrib["id"]
        errors.append(f"Resource '{res_id}', property '{prop_name}' has an invalid link target '{inv.attrib['href']}'")
    return errors


def check_if_bitstreams_exist(root: etree._Element, imgdir: str) -> None:
    """
    Make sure that all bitstreams referenced in the XML file exist in the imgdir.

    Args:
        root: parsed XML file
        imgdir: folder where the bitstreams are stored

    Raises:
        InputError: if a bitstream does not exist in the imgdir
    """
    multimedia_resources = [x for x in root if any((y.tag == "bitstream" for y in x.iter()))]
    for res in multimedia_resources:
        pth = next(Path(x.text.strip()) for x in res.iter() if x.tag == "bitstream" and x.text)
        if not Path(imgdir / pth).is_file():
            raise InputError(
                f"Bitstream '{pth!s}' of resource '{res.attrib['label']}' does not exist in the imgdir '{imgdir}'."
            )
