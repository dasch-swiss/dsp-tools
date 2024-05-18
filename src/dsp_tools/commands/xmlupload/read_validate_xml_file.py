from __future__ import annotations

from pathlib import Path

import regex
from loguru import logger
from lxml import etree

from dsp_tools.models.exceptions import UserError
from dsp_tools.utils.iri_util import is_resource_iri
from dsp_tools.utils.xml_utils import parse_and_clean_xml_file
from dsp_tools.utils.xml_validation import validate_xml


def validate_and_parse_xml_file(imgdir: str, input_file: Path) -> tuple[str, etree._Element, str]:
    """
    This function takes a path to an XML file.
    It validates the file against the XML schema.
    It checks if all the mentioned bitstream files are in the specified location.
    It retrieves the shortcode and default ontology from the XML file.

    Args:
        imgdir: directory to the bitstream files
        input_file: file that will be processed
        preprocessing_done: True if the bitstream files have already been processed

    Returns:
        The ontology name, the parsed XML file and the shortcode of the project
    """
    root, shortcode, default_ontology = _validate_and_parse(input_file)
    _check_if_bitstreams_exist(root=root, imgdir=imgdir)
    logger.info(f"Validated and parsed the XML file. {shortcode=:} and {default_ontology=:}")
    return default_ontology, root, shortcode


def validate_and_parse_xml_file_preprocessing_done(
    xml: etree._ElementTree[etree._Element],
) -> tuple[str, etree._Element, str]:
    """
    This function takes an element tree.
    It validates the file against the XML schema.
    It retrieves the shortcode and default ontology from the XML file.

    Args:
        xml: xml etree that will be processed

    Returns:
        The ontology name, the parsed XML file and the shortcode of the project
    """
    root, shortcode, default_ontology = _validate_and_parse(xml)
    logger.info(f"Validated and parsed the XML. {shortcode=:} and {default_ontology=:}")
    return default_ontology, root, shortcode


def _validate_and_parse(xml: etree._ElementTree[etree._Element] | Path) -> tuple[etree._Element, str, str]:
    validate_xml(input_file=xml)
    root = parse_and_clean_xml_file(xml)
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
        UserError: if a link target does not exist in the XML file
    """
    resptr_errors = _check_if_resptr_targets_exist(root)
    salsah_errors = _check_if_salsah_targets_exist(root)
    if errors := resptr_errors + salsah_errors:
        sep = "\n - "
        msg = f"It is not possible to upload the XML file, because it contains invalid links:{sep}{sep.join(errors)}"
        raise UserError(msg)


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


def _check_if_bitstreams_exist(
    root: etree._Element,
    imgdir: str,
) -> None:
    """
    Make sure that all bitstreams referenced in the XML file exist in the imgdir.

    Args:
        root: parsed XML file
        imgdir: folder where the bitstreams are stored

    Raises:
        UserError: if a bitstream does not exist in the imgdir
    """
    multimedia_resources = [x for x in root if any((y.tag == "bitstream" for y in x.iter()))]
    for res in multimedia_resources:
        pth = next(Path(x.text) for x in res.iter() if x.tag == "bitstream" and x.text)
        if not Path(imgdir / pth).is_file():
            raise UserError(
                f"Bitstream '{pth!s}' of resource '{res.attrib['label']}' does not exist in the imgdir '{imgdir}'."
            )
