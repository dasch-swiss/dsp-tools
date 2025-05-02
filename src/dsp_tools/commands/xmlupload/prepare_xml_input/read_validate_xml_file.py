from __future__ import annotations

import warnings
from pathlib import Path

from loguru import logger
from lxml import etree

from dsp_tools.clients.connection import Connection
from dsp_tools.commands.xmlupload.prepare_xml_input.check_consistency_with_ontology import (
    do_xml_consistency_check_with_ontology,
)
from dsp_tools.commands.xmlupload.prepare_xml_input.iiif_uri_validator import IIIFUriValidator
from dsp_tools.commands.xmlupload.prepare_xml_input.ontology_client import OntologyClientLive
from dsp_tools.commands.xmlupload.upload_config import UploadConfig
from dsp_tools.error.custom_warnings import DspToolsUserWarning
from dsp_tools.error.exceptions import InputError


def preliminary_validation_of_root(root: etree._Element, con: Connection, config: UploadConfig) -> None:
    if not config.skip_iiif_validation:
        _validate_iiif_uris(root)
    default_ontology = root.attrib["default-ontology"]
    ontology_client = OntologyClientLive(con=con, shortcode=config.shortcode, default_ontology=default_ontology)
    do_xml_consistency_check_with_ontology(ontology_client, root)


def _validate_iiif_uris(root: etree._Element) -> None:
    uris = [uri.strip() for node in root.iter(tag="iiif-uri") if (uri := node.text)]
    if problems := IIIFUriValidator(uris).validate():
        msg = problems.get_msg()
        warnings.warn(DspToolsUserWarning(msg))
        logger.warning(msg)


def check_if_bitstreams_exist(root: etree._Element, imgdir: str) -> None:
    """
    Make sure that all bitstreams referenced in the XML file exist in the imgdir.

    Args:
        root: parsed XML file
        imgdir: folder where the bitstreams are stored

    Raises:
        InputError: if a bitstream does not exist in the imgdir
    """
    multimedia_resources = [x for x in root if any(y.tag == "bitstream" for y in x.iter())]
    for res in multimedia_resources:
        pth = next(Path(x.text.strip()) for x in res.iter() if x.tag == "bitstream" and x.text)
        if not Path(imgdir / pth).is_file():
            raise InputError(
                f"Bitstream '{pth!s}' of resource '{res.attrib['label']}' does not exist in the imgdir '{imgdir}'."
            )
