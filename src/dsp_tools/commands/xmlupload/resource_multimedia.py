from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any, Optional, cast

from dsp_tools.commands.xmlupload.models.permission import Permissions
from dsp_tools.commands.xmlupload.models.sipi import Sipi
from dsp_tools.commands.xmlupload.models.xmlbitstream import XMLBitstream
from dsp_tools.commands.xmlupload.models.xmlresource import BitstreamInfo, XMLResource
from dsp_tools.models.exceptions import BaseError
from dsp_tools.utils.create_logger import get_logger
from dsp_tools.utils.shared import try_network_action

logger = get_logger(__name__)


def handle_media_info(
    resource: XMLResource,
    media_previously_uploaded: bool,
    sipi_server: Sipi,
    imgdir: str,
    permissions_lookup: dict[str, Permissions],
) -> tuple[bool, None | BitstreamInfo]:
    """
    This function checks if a resource has a bitstream

    Args:
        resource: resource holding the bitstream
        media_previously_uploaded: True if the image is already in SIPI
        sipi_server: server to upload
        permissions_lookup: dictionary that contains the permission name as string and the corresponding Python object
        imgdir: directory of the file

    Returns:
        If the handling of the bitstream object was successful,
        in case of a bitstream the object or None in case of unsuccessful try.
    """
    bitstream = resource.bitstream
    success = True
    bitstream_information: None | BitstreamInfo = None

    if not bitstream:
        return success, bitstream_information
    if not media_previously_uploaded:
        bitstream_information = _handle_media_upload(
            resource=resource,
            bitstream=bitstream,
            permissions_lookup=permissions_lookup,
            sipi_server=sipi_server,
            imgdir=imgdir,
        )
        if not bitstream_information:
            success = False
    else:
        bitstream_information = resource.get_bitstream_information(bitstream.value, permissions_lookup)
    return success, bitstream_information


def _handle_media_upload(
    resource: XMLResource,
    bitstream: XMLBitstream,
    permissions_lookup: dict[str, Permissions],
    sipi_server: Sipi,
    imgdir: str,
) -> BitstreamInfo | None:
    """
    Upload a bitstream file to SIPI

    Args:
        resource: resource holding the bitstream
        bitstream: the bitstream object
        permissions_lookup: dictionary that contains the permission name as string and the corresponding Python object
        sipi_server: server to upload
        imgdir: directory of the file

    Returns:
        The information from sipi which is needed to establish a link from the resource
    """
    try:
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
