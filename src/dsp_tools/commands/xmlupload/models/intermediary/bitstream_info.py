from __future__ import annotations

from dataclasses import dataclass

from dsp_tools.commands.xmlupload.models.permission import Permissions


@dataclass(frozen=True)
class BitstreamInfo:
    """
    Represents a bitstream object,
    consisting of its file name on the local file system,
    the internal file name assigned by the ingest service
    and optionally its permissions.
    """

    local_file: str
    internal_file_name: str
    permissions: Permissions | None = None
