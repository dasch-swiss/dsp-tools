from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Optional

from loguru import logger

from dsp_tools.commands.xmlupload.models.deserialise.deserialise_value import XMLBitstream
from dsp_tools.commands.xmlupload.models.deserialise.xmlresource import BitstreamInfo
from dsp_tools.commands.xmlupload.models.deserialise.xmlresource import XMLResource
from dsp_tools.commands.xmlupload.models.ingest import IngestClient
from dsp_tools.commands.xmlupload.models.permission import Permissions
from dsp_tools.models.exceptions import PermanentConnectionError


def handle_media_info(
    resource: XMLResource,
    media_previously_uploaded: bool,
    ingest_client: IngestClient,
    imgdir: str,
    permissions_lookup: dict[str, Permissions],
    shortcode: str,
) -> tuple[bool, None | BitstreamInfo]:
    """
    This function checks if a resource has a bitstream.
    If not, it reports success and returns None.
    If the file has been uploaded it returns the internal ID.
    Else it uploads it and returns the internal ID.


    Args:
        resource: resource holding the bitstream
        media_previously_uploaded: True if the image was already ingested
        ingest_client: server to upload
        imgdir: directory of the file
        permissions_lookup: dictionary that contains the permission name as string and the corresponding Python object
        shortcode: shortcode of the project

    Returns:
        If the bitstream could be processed successfully, then the function returns True and the new internal ID.
        If there was no bitstream, it returns True and None.
        If the upload was not successful, it returns False and None.
    """
    bitstream = resource.bitstream
    if bitstream is None:
        return True, None
    elif not media_previously_uploaded:
        try:
            res = ingest_client.ingest(shortcode, Path(imgdir) / Path(bitstream.value))
            msg = f"Uploaded file '{bitstream.value}'"
            print(f"{datetime.now()}: {msg}")
            logger.info(msg)
            return True, BitstreamInfo(
                bitstream.value, res.internal_filename, _permissions(bitstream, permissions_lookup)
            )
        except PermanentConnectionError as err:
            msg = f"Unable to upload file '{bitstream.value}' " f"of resource '{resource.label}' ({resource.res_id})"
            print(f"{datetime.now()}: WARNING: {msg}: {err.message}")
            logger.opt(exception=True).warning(msg)
            return False, None
    else:
        return True, BitstreamInfo(bitstream.value, bitstream.value, _permissions(bitstream, permissions_lookup))


def _permissions(
    bitstream: Optional[XMLBitstream], permissions_lookup: dict[str, Permissions]
) -> Optional[Permissions]:
    if bitstream is None:
        return None
    if bitstream.permissions is None:
        return None
    else:
        return permissions_lookup.get(bitstream.permissions)
