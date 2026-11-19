from __future__ import annotations

import warnings
from pathlib import Path
from urllib.parse import urlparse

from loguru import logger
from lxml import etree
from tqdm import tqdm

from dsp_tools.commands.xmlupload.exceptions import MultimediaFileNotFoundError
from dsp_tools.commands.xmlupload.models.input_problems import AllIIIFUriProblems
from dsp_tools.commands.xmlupload.models.input_problems import IIIFHostRefused
from dsp_tools.commands.xmlupload.models.input_problems import IIIFProblemCategory
from dsp_tools.commands.xmlupload.models.input_problems import IIIFUriProblem
from dsp_tools.commands.xmlupload.models.input_problems import MultimediaFileNotFoundProblem
from dsp_tools.commands.xmlupload.prepare_xml_input.iiif_uri_validator import IIIFUriValidator
from dsp_tools.error.custom_warnings import DspToolsUserWarning
from dsp_tools.setup.ansi_colors import BOLD_CYAN
from dsp_tools.setup.ansi_colors import RESET_TO_DEFAULT


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
    all_problems = _check_iiif_uris(uris)
    if warning_msg := all_problems.get_warning_msg():
        warnings.warn(DspToolsUserWarning(warning_msg))
        logger.warning(warning_msg)
    if info_msg := all_problems.get_info_msg():
        print(BOLD_CYAN + info_msg + RESET_TO_DEFAULT)
        logger.info(info_msg)


def _check_iiif_uris(uris: list[str]) -> AllIIIFUriProblems:
    """Check each URI. After a server refused access, do not call it again, to prevent a block of the IP address."""
    validator = IIIFUriValidator()
    problems: list[IIIFUriProblem] = []
    refused_hosts: dict[str, IIIFHostRefused] = {}
    for uri in tqdm(uris, desc="Checking IIIF-URIs", dynamic_ncols=True):
        host = urlparse(uri).netloc
        if refused := refused_hosts.get(host):
            refused.unverified_uris.append(uri)
            continue
        result = validator.validate_one_uri(uri)
        if not result:
            continue
        if result.category == IIIFProblemCategory.ACCESS_REFUSED:
            refused_hosts[host] = IIIFHostRefused(host=host, status_code=result.status_code, unverified_uris=[uri])
        else:
            problems.append(result)
    return AllIIIFUriProblems(problems=problems, refused_hosts=list(refused_hosts.values()))


def check_if_bitstreams_exist(root: etree._Element, imgdir: Path) -> None:
    """
    Make sure that all bitstreams referenced in the XML file exist in the imgdir.

    Args:
        root: parsed XML file
        imgdir: path to the folder where the bitstreams are stored

    Raises:
        InputError: if a bitstream does not exist in the imgdir
    """
    logger.debug("Checking if filepaths exist.")
    multimedia_resources = [x for x in root if any(y.tag == "bitstream" and not len(y) for y in x.iter())]
    progress_bar = tqdm(multimedia_resources, desc="Checking multimedia filepaths", dynamic_ncols=True)
    all_problems = []
    for res in progress_bar:
        pth = next(Path(x.text.strip()) for x in res.iter() if x.tag == "bitstream" and x.text and x.text.strip())
        if not Path(imgdir / pth).is_file():
            all_problems.append(MultimediaFileNotFoundProblem(res.attrib["id"], str(pth)))
    if all_problems:
        raise MultimediaFileNotFoundError(str(imgdir), all_problems)
