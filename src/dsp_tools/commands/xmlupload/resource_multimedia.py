from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Tuple

from loguru import logger

from dsp_tools.commands.xmlupload.models.deserialise.deserialise_value import XMLBitstream
from dsp_tools.commands.xmlupload.models.deserialise.xmlresource import BitstreamInfo
from dsp_tools.commands.xmlupload.models.deserialise.xmlresource import XMLResource
from dsp_tools.commands.xmlupload.models.permission import Permissions
from dsp_tools.commands.xmlupload.models.sipi import IngestClient
from dsp_tools.models.exceptions import PermanentConnectionError


@dataclass
class IngestContext:
    ingest_client: IngestClient
    resource: XMLResource
    imgdir: str
    shortcode: str
    permissions_lookup: dict[str, Permissions]

    def stream_permissions(self) -> Permissions | None:
        if self.resource.bitstream is None:
            return None
        if self.resource.bitstream.permissions is None:
            return None
        else:
            return self.permissions_lookup.get(self.resource.bitstream.permissions)

    def bitstream_and_path(self) -> Tuple[XMLBitstream, Path] | None:
        if self.resource.bitstream is None:
            return None
        else:
            bitstream = self.resource.bitstream
            path = Path(self.imgdir) / Path(bitstream.value)
            return bitstream, path


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
    ctx = IngestContext(ingest_client, resource, imgdir, shortcode, permissions_lookup)
    bitstream = ctx.resource.bitstream
    if bitstream is None:
        return True, None
    if not media_previously_uploaded:
        info = _do_ingest(ctx)
        return info is not None, info
    else:
        return True, BitstreamInfo(bitstream.value, bitstream.value, ctx.stream_permissions())


def _do_ingest(ctx: IngestContext) -> BitstreamInfo | None:
    """
    This function ingests the specified bitstream file and then returns the BitstreamInfo.

    Args:
        ctx: The context object which contains all necessary information for the upload

    Returns:
        The BitstreamInfo which is needed to establish a link from the resource
    """
    stream_and_path = ctx.bitstream_and_path()
    if stream_and_path is None:
        return None
    else:
        try:
            stream, path = stream_and_path
            res = ctx.ingest_client.ingest(ctx.shortcode, path)
            msg = f"Uploaded file '{ctx.bitstream_and_path()}'"
            print(f"{datetime.now()}: {msg}")
            logger.info(msg)
            return BitstreamInfo(stream.value, res.internal_filename, ctx.stream_permissions())
        except PermanentConnectionError as err:
            msg = (
                f"Unable to upload file '{ctx.bitstream_and_path()}' "
                f"of resource '{ctx.resource.label}' ({ctx.resource.res_id})"
            )
            print(f"{datetime.now()}: WARNING: {msg}: {err.message}")
            logger.opt(exception=True).warning(msg)
            return None
