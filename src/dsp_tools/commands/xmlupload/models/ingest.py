from __future__ import annotations

import urllib
from dataclasses import dataclass
from dataclasses import field
from pathlib import Path
from typing import Protocol

import requests
from loguru import logger
from requests import Session
from requests.adapters import HTTPAdapter
from requests.adapters import Retry

from dsp_tools.clients.authentication_client import AuthenticationClient
from dsp_tools.commands.xmlupload.models.bitstream_info import BitstreamInfo
from dsp_tools.commands.xmlupload.models.processed.file_values import ProcessedFileValue
from dsp_tools.error.exceptions import BadCredentialsError
from dsp_tools.error.exceptions import InvalidFileNameError
from dsp_tools.error.exceptions import PermanentConnectionError

STATUS_OK = 200
BAD_REQUEST = 400
STATUS_UNAUTHORIZED = 401
STATUS_INTERNAL_SERVER_ERROR = 500


@dataclass(frozen=True)
class IngestResponse:
    """Wrapper around `internal_filename`"""

    internal_filename: str


class AssetClient(Protocol):
    """Protocol for asset handling clients."""

    def get_bitstream_info(self, file_info: ProcessedFileValue) -> BitstreamInfo | None:
        """Uploads the file to the ingest server if applicable, and returns the upload results.

        Args:
            file_info: Information required for ingesting an asset
        """


@dataclass
class DspIngestClientLive(AssetClient):
    """Client for uploading assets to the DSP-Ingest."""

    dsp_ingest_url: str
    authentication_client: AuthenticationClient
    shortcode: str
    imgdir: str
    session: Session = field(init=False)

    def __post_init__(self) -> None:
        retries = 6
        self.session = Session()
        retry = Retry(
            total=retries,
            read=retries,
            connect=retries,
            backoff_factor=0.3,
            allowed_methods=None,  # means all methods
            status_forcelist=[STATUS_INTERNAL_SERVER_ERROR],
        )
        adapter = HTTPAdapter(max_retries=retry)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

    def _ingest(self, filepath: Path) -> IngestResponse:
        """Uploads a file to the ingest server and returns the IngestResponse.

        This function sends a POST request to the ingest server with the file to upload.
        It will retry the request 6 times in case of a connection, timeout or internal server error.

        After all retry attempts are exhausted it will raise exceptions if the upload failed.
        The http status code is also checked and if it is not 200, a PermanentConnectionError is raised.

        Args:
            filepath: Path to the file to ingest, could be either absolute or relative.

        Raises:
            BadCredentialsError: If the credentials are invalid.
            PermanentConnectionError: If the connection fails.

        Returns:
            IngestResponse: The internal filename of the uploaded file.
        """
        filename = urllib.parse.quote(filepath.name)
        url = f"{self.dsp_ingest_url}/projects/{self.shortcode}/assets/ingest/{filename}"
        headers = {
            "Authorization": f"Bearer {self.authentication_client.get_token()}",
            "Content-Type": "application/octet-stream",
        }
        timeout = 600
        with open(filepath, "rb") as binary_io:
            try:
                logger.debug(f"REQUEST: POST to {url}, timeout: {timeout}, headers: {headers | {'Authorization': '*'}}")
                res = self.session.post(
                    url=url,
                    headers=headers,
                    data=binary_io,
                    timeout=timeout,
                )
                logger.debug(f"RESPONSE: {res.status_code}: {res.text}")
                if res.status_code == STATUS_OK:
                    return IngestResponse(internal_filename=res.json()["internalFilename"])
                elif res.status_code == STATUS_UNAUTHORIZED:
                    raise BadCredentialsError("Bad credentials")
                elif res.status_code == BAD_REQUEST and res.text == "Invalid value for: path parameter filename":
                    raise InvalidFileNameError()
                else:
                    raise PermanentConnectionError()
            except requests.exceptions.RequestException as e:
                raise PermanentConnectionError() from e

    def get_bitstream_info(self, file_info: ProcessedFileValue) -> BitstreamInfo | None:
        """Uploads a file to the ingest server and returns the upload results."""
        try:
            res = self._ingest(Path(self.imgdir) / Path(file_info.value))
            logger.info(f"Uploaded file '{file_info.value}'")
            return BitstreamInfo(res.internal_filename, file_info.metadata.permissions)
        except InvalidFileNameError:
            msg = f"Invalid filename: Unable to upload file '{file_info.value}' of resource '{file_info.res_id}'"
        except PermanentConnectionError:
            msg = f"Unable to upload file '{file_info.value}' of resource '{file_info.res_id}'"
        logger.error(msg)
        return None


@dataclass(frozen=True)
class BulkIngestedAssetClient(AssetClient):
    """Client for handling media info, if the assets were bulk ingested previously."""

    def get_bitstream_info(self, file_info: ProcessedFileValue) -> BitstreamInfo:
        """Returns the BitstreamInfo of the already ingested file based on the `ProcessedFileValue.value`."""
        return BitstreamInfo(file_info.value, file_info.metadata.permissions)
