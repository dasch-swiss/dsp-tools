from __future__ import annotations

from datetime import datetime
from pathlib import Path

from loguru import logger

from dsp_tools.commands.xmlupload.models.deserialise.deserialise_value import XMLBitstream
from dsp_tools.commands.xmlupload.models.deserialise.xmlresource import BitstreamInfo
from dsp_tools.commands.xmlupload.models.deserialise.xmlresource import XMLResource
from dsp_tools.commands.xmlupload.models.permission import Permissions
from dsp_tools.commands.xmlupload.models.sipi import IngestClient
from dsp_tools.models.exceptions import PermanentConnectionError


def handle_media_info(
    resource: XMLResource,
    media_previously_uploaded: bool,
    ingest_client: IngestClient,
    imgdir: str,
    permissions_lookup: dict[str, Permissions],
) -> tuple[bool, None | BitstreamInfo]:
    """
    This function checks if a resource has a bitstream.
    If not, it reports success and returns None.
    If the file has been uploaded it returns the internal ID.
    Else it uploads it and returns the internal ID.


    Args:
        resource: resource holding the bitstream
        media_previously_uploaded: True if the image is already in SIPI
        ingest_client: server to upload
        imgdir: directory of the file
        permissions_lookup: dictionary that contains the permission name as string and the corresponding Python object

    Returns:
        If the bitstream could be processed successfully, then the function returns True and the new internal ID.
        If there was no bitstream, it returns True and None.
        If the upload was not successful, it returns False and None.
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
            ingest_client=ingest_client,
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
    ingest_client: IngestClient,
    imgdir: str,
) -> BitstreamInfo | None:
    """
    Upload a bitstream file to SIPI

    Args:
        resource: resource holding the bitstream
        bitstream: the bitstream object
        permissions_lookup: dictionary that contains the permission name as string and the corresponding Python object
        ingest_client: server to upload
        imgdir: directory of the file

    Returns:
        The information from sipi which is needed to establish a link from the resource
    """
    try:
        resource_bitstream = _upload_bitstream(
            resource=resource,
            ingest_client=ingest_client,
            imgdir=imgdir,
            permissions_lookup=permissions_lookup,
        )
        msg = f"Uploaded file '{bitstream.value}'"
        print(f"{datetime.now()}: {msg}")
        logger.info(msg)
        return resource_bitstream
    except PermanentConnectionError as err:
        msg = f"Unable to upload file '{bitstream.value}' of resource '{resource.label}' ({resource.res_id})"
        print(f"{datetime.now()}: WARNING: {msg}: {err.message}")
        logger.opt(exception=True).warning(msg)
        return None


def _upload_bitstream(
    resource: XMLResource,
    ingest_client: IngestClient,
    imgdir: str,
    permissions_lookup: dict[str, Permissions],
) -> BitstreamInfo | None:
    """
    This function uploads a specified bitstream file to SIPI and then returns the file information from SIPI.

    Args:
        resource: resource that has a bitstream
        ingest_client: server to upload
        imgdir: directory of the file
        permissions_lookup: dictionary that contains the permission name as string and the corresponding Python object

    Returns:
        The information from sipi which is needed to establish a link from the resource
    """
    if not resource.bitstream:
        return None
    res = ingest_client.ingest("", Path(imgdir) / Path(resource.bitstream.value))
    return resource.get_bitstream_information(
        internal_file_name_bitstream=res.internal_filename,
        permissions_lookup=permissions_lookup,
    )
