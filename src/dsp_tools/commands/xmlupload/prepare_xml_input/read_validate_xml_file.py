from __future__ import annotations

import warnings
from pathlib import Path

from loguru import logger
from lxml import etree
from tqdm import tqdm

from dsp_tools.commands.xmlupload.errors import MultimediaFileNotFound
from dsp_tools.commands.xmlupload.models.input_problems import AllIIIFUriProblems
from dsp_tools.commands.xmlupload.models.input_problems import MultimediaFileNotFoundProblem
from dsp_tools.commands.xmlupload.prepare_xml_input.iiif_uri_validator import IIIFUriValidator
from dsp_tools.error.custom_warnings import DspToolsUserWarning


def validate_iiif_uris(root: etree._Element) -> None:
    uris = [uri.strip() for node in root.iter(tag="iiif-uri") if (uri := node.text)]
    if (num := len(uris)) > 1001:
        warnings.warn(
            DspToolsUserWarning(
                f"Your data contains {num} IIIF-URIs. "
                f"Each validation makes a server call. "
                f"Due to the large number, the validation of the IIIF-URIs has to be skipped."
            )
        )
        return
    progress_bar = tqdm(uris, desc="Checking IIIF-URIs", dynamic_ncols=True)
    validator = IIIFUriValidator()
    problems = []
    for uri in progress_bar:
        if result := validator.validate_one_uri(uri):
            problems.append(result)
    if problems:
        msg = AllIIIFUriProblems(problems).get_msg()
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
    logger.debug("Checking if filepaths exist.")
    multimedia_resources = [x for x in root if any(y.tag == "bitstream" for y in x.iter())]
    progress_bar = tqdm(multimedia_resources, desc="Checking multimedia filepaths", dynamic_ncols=True)
    all_problems = []
    for res in progress_bar:
        pth = next(Path(x.text.strip()) for x in res.iter() if x.tag == "bitstream" and x.text)
        if not Path(imgdir / pth).is_file():
            all_problems.append(MultimediaFileNotFoundProblem(res.attrib["id"], str(pth)))
    if all_problems:
        raise MultimediaFileNotFound(imgdir, all_problems)
