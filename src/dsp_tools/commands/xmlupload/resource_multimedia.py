from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from dsp_tools.commands.xmlupload.models.permission import Permissions
from dsp_tools.commands.xmlupload.models.sipi import Sipi
from dsp_tools.commands.xmlupload.models.xmlbitstream import XMLBitstream
from dsp_tools.commands.xmlupload.models.xmlresource import BitstreamInfo, XMLResource
from dsp_tools.models.exceptions import BaseError
from dsp_tools.utils.create_logger import get_logger
from dsp_tools.utils.shared import try_network_action

logger = get_logger(__name__)


def _upload_bitstream(
    resource: XMLResource,
    sipi_server: Sipi,
    imgdir: str,
    permissions_lookup: dict[str, Permissions],
) -> BitstreamInfo | None:
    """
    This function uploads a specified bitstream file to SIPI and then returns the file information from SIPI.

    Args:
        resource: resource with that has a bitstream
        sipi_server: server to upload
        imgdir: directory of the file
        permissions_lookup: dictionary that contains the permission name as string and the corresponding Python object

    Returns:
        The information from sipi which is needed to establish a link from the resource
    """
    pth = resource.bitstream.value  # type: ignore[union-attr]
    img: Optional[dict[Any, Any]] = try_network_action(
        sipi_server.upload_bitstream,
        filepath=str(Path(imgdir) / Path(pth)),
    )
    internal_file_name_bitstream = img["uploadedFiles"][0]["internalFilename"]  # type: ignore[index]
    return resource.get_bitstream_information(
        internal_file_name_bitstream=internal_file_name_bitstream,
        permissions_lookup=permissions_lookup,
    )


def handle_bitstream(
    resource: XMLResource,
    bitstream: XMLBitstream,
    preprocessing_done: bool,
    permissions_lookup: dict[str, Permissions],
    sipi_server: Sipi,
    imgdir: str,
) -> BitstreamInfo | None:
    """
    Upload a bitstream file to SIPI

    Args:
        resource: resource holding the bitstream
        bitstream: the bitstream object
        preprocessing_done: whether the preprocessing is done already
        permissions_lookup: dictionary that contains the permission name as string and the corresponding Python object
        sipi_server: server to upload
        imgdir: directory of the file

    Returns:
        The information from sipi which is needed to establish a link from the resource
    """
    try:
        if preprocessing_done:
            resource_bitstream = resource.get_bitstream_information(bitstream.value, permissions_lookup)
        else:
            resource_bitstream = _upload_bitstream(
                resource=resource,
                sipi_server=sipi_server,
                imgdir=imgdir,
                permissions_lookup=permissions_lookup,
            )
            msg = f"Uploaded file '{bitstream.value}'"
            print(f"{datetime.now()}: {msg}")
            logger.info(msg)
        return resource_bitstream
    except BaseError as err:
        err_msg = err.orig_err_msg_from_api or err.message
        msg = f"Unable to upload file '{bitstream.value}' of resource '{resource.label}' ({resource.id})"
        print(f"{datetime.now()}: WARNING: {msg}: {err_msg}")
        logger.warning(msg, exc_info=True)
        return None
