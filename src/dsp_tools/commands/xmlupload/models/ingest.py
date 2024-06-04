from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Protocol

from loguru import logger

from dsp_tools.commands.xmlupload.models.deserialise.deserialise_value import XMLBitstream
from dsp_tools.commands.xmlupload.models.deserialise.xmlresource import BitstreamInfo
from dsp_tools.commands.xmlupload.models.permission import Permissions
from dsp_tools.models.exceptions import PermanentConnectionError
from dsp_tools.utils.connection import Connection

STATUS_OK = 200
STATUS_UNAUTHORIZED = 401
STATUS_INTERNAL_SERVER_ERROR = 500


@dataclass(frozen=True)
class IngestResponse:
    """Wrapper around `internal_filename`"""

    internal_filename: str


class AssetClient(Protocol):
    """Protocol for asset handling clients."""

    def get_bitstream_info(
        self,
        bitstream: XMLBitstream,
        permissions_lookup: dict[str, Permissions],
        res_label: str,
        res_id: str,
    ) -> tuple[bool, None | BitstreamInfo]:
        """Uploads the file to the ingest server if applicable, and returns the BitstreamInfo.

        Args:
            bitstream: The bitstream to upload.
            permissions_lookup: The permissions lookup.
            res_label: The resource label (for error message in failure case).
            res_id: The resource ID (for error message in failure case).
        """


@dataclass
class DspIngestClientLive(AssetClient):
    """Client for uploading assets to the DSP-Ingest."""

    con: Connection
    shortcode: str
    imgdir: str

    def _ingest(self, filepath: Path) -> IngestResponse:
        """
        Uploads a file to the ingest server and returns the IngestResponse.

        Args:
            filepath: Path to the file to ingest, could be either absolute or relative.

        Raises:
            BadCredentialsError: If the credentials are invalid.
            PermanentConnectionError: If the connection fails.

        Returns:
            IngestResponse: The internal filename of the uploaded file.
        """
        route = f"/projects/{self.shortcode}/assets/ingest/{filepath.name}"
        with open(filepath, "rb") as binary_io:
            res = self.con.post(
                route=route,
                files={"file": ("filename", binary_io, "application/octet-stream")},
                timeout=60,
            )
            return IngestResponse(internal_filename=res["internalFilename"])

    def get_bitstream_info(
        self,
        bitstream: XMLBitstream,
        permissions_lookup: dict[str, Permissions],
        res_label: str,
        res_id: str,
    ) -> tuple[bool, None | BitstreamInfo]:
        """Uploads a file to the ingest server and returns the BitstreamInfo."""
        try:
            res = self._ingest(Path(self.imgdir) / Path(bitstream.value))
            msg = f"Uploaded file '{bitstream.value}'"
            print(f"{datetime.now()}: {msg}")
            logger.info(msg)
            permissions = permissions_lookup.get(bitstream.permissions) if bitstream.permissions else None
            return True, BitstreamInfo(bitstream.value, res.internal_filename, permissions)
        except PermanentConnectionError as err:
            msg = f"Unable to upload file '{bitstream.value}' " f"of resource '{res_label}' ({res_id})"
            print(f"{datetime.now()}: WARNING: {msg}: {err.message}")
            logger.opt(exception=True).warning(msg)
            return False, None


@dataclass(frozen=True)
class BulkIngestedAssetClient(AssetClient):
    """Client for handling media info, if the assets were bulk ingested previously."""

    def get_bitstream_info(
        self,
        bitstream: XMLBitstream,
        permissions_lookup: dict[str, Permissions],
        res_label: str,  # noqa: ARG002
        res_id: str,  # noqa: ARG002
    ) -> tuple[bool, BitstreamInfo | None]:
        """Returns the BitstreamInfo of the already ingested file based on the `XMLBitstream.value`."""
        permissions = permissions_lookup.get(bitstream.permissions) if bitstream.permissions else None
        return True, BitstreamInfo(bitstream.value, bitstream.value, permissions)
