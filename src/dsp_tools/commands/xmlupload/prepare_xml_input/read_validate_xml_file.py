from __future__ import annotations

import warnings
from pathlib import Path

from loguru import logger
from lxml import etree

from dsp_tools.commands.xmlupload.prepare_xml_input.iiif_uri_validator import IIIFUriValidator
from dsp_tools.error.custom_warnings import DspToolsUserWarning
from dsp_tools.error.exceptions import InputError


def validate_iiif_uris(root: etree._Element) -> None:
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
