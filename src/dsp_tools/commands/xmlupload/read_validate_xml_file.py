from __future__ import annotations

from pathlib import Path
from typing import Any, Union

from lxml import etree

from dsp_tools.models.exceptions import UserError
from dsp_tools.utils.create_logger import get_logger
from dsp_tools.utils.shared import validate_xml_against_schema
from dsp_tools.utils.xml_utils import parse_and_clean_xml_file

logger = get_logger(__name__)


def validate_and_parse_xml_file(
    imgdir: str,
    input_file: Union[str, Path, etree._ElementTree[Any]],
    preprocessing_done: bool,
) -> tuple[str, etree._Element, str]:
    """
    This function takes an element tree or a path to an XML file.
    It validates the file against the XML schema.
    It checks if all the mentioned bitstream files are in the specified location.
    It retrieves the shortcode and default ontology from the XML file.

    Args:
        imgdir: directory to the bitstream files
        input_file: file or etree that will be processed
        preprocessing_done: True if the bitstream files have already been processed

    Returns:
        The ontology name, the parsed XML file and the shortcode of the project
    """
    validate_xml_against_schema(input_file=input_file)
    root = parse_and_clean_xml_file(input_file=input_file)
    if not preprocessing_done:
        check_if_bitstreams_exist(root=root, imgdir=imgdir)
    shortcode = root.attrib["shortcode"]
    default_ontology = root.attrib["default-ontology"]
    logger.info(f"Validated and parsed the XML file. {shortcode=:} and {default_ontology=:}")
    return default_ontology, root, shortcode


def check_if_bitstreams_exist(
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
        pth = [Path(x.text) for x in res.iter() if x.tag == "bitstream" and x.text][0]
        if not Path(imgdir / pth).is_file():
            raise UserError(
                f"Bitstream '{pth!s}' of resource '{res.attrib['label']}' does not exist in the imgdir '{imgdir}'."
            )
