from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from loguru import logger

from dsp_tools.commands.xmlupload.models.bitstream_info import BitstreamInfo
from dsp_tools.commands.xmlupload.models.permission import Permissions
from dsp_tools.commands.xmlupload.models.processed.file_values import ProcessedFileBitstream
from dsp_vre.clients.exceptions import InvalidIngestFileNameError
from dsp_vre.clients.exceptions import PermanentConnectionError
from dsp_vre.clients.ingest import DspIngestClientLive
from dsp_vre.clients.legal_info_client import LegalInfoClient
from dsp_vre.clients.list_client import ListGetClient


class AssetClient(Protocol):
    """Protocol for asset handling clients."""

    def get_bitstream_info(
        self, file_info: ProcessedFileBitstream, permissions: Permissions | None
    ) -> BitstreamInfo | None:
        """Uploads the file to the ingest service if applicable, and returns the upload results.

        Args:
            file_info: Information required for ingesting an asset
            permissions: Permission information of the File
        """


@dataclass
class DspIngestAssetClient(AssetClient):
    """Uploads the assets of an XML file to the ingest service."""

    ingest_client: DspIngestClientLive
    imgdir: str

    def get_bitstream_info(
        self, file_info: ProcessedFileBitstream, permissions: Permissions | None
    ) -> BitstreamInfo | None:
        """Uploads a file to the ingest service and returns the upload results."""
        try:
            res = self.ingest_client.ingest(Path(self.imgdir) / Path(file_info.value))
            logger.info(f"Uploaded file '{file_info.value}'")
            return BitstreamInfo(res.internal_filename, permissions)
        except InvalidIngestFileNameError:
            msg = f"Invalid filename: Unable to upload file '{file_info.value}' of resource '{file_info.res_id}'"
        except PermanentConnectionError:
            msg = f"Unable to upload file '{file_info.value}' of resource '{file_info.res_id}'"
        logger.error(msg)
        return None


@dataclass(frozen=True)
class BulkIngestedAssetClient(AssetClient):
    """Client for handling media info, if the assets were bulk ingested previously."""

    def get_bitstream_info(self, file_info: ProcessedFileBitstream, permissions: Permissions | None) -> BitstreamInfo:
        """Returns the BitstreamInfo of the already ingested file based on the `ProcessedFileValue.value`."""
        return BitstreamInfo(file_info.value, permissions)


@dataclass(frozen=True)
class UploadClients:
    """Holds all the clients needed for the upload process."""

    asset_client: AssetClient
    list_client: ListGetClient
    legal_info_client: LegalInfoClient
