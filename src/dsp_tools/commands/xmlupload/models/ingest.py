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

from dsp_tools.commands.xmlupload.models.deserialise.deserialise_value import XMLBitstream
from dsp_tools.commands.xmlupload.models.deserialise.xmlresource import BitstreamInfo
from dsp_tools.commands.xmlupload.models.permission import Permissions
from dsp_tools.models.exceptions import BadCredentialsError
from dsp_tools.models.exceptions import PermanentConnectionError
from dsp_tools.utils.authentication_client import AuthenticationClient
from dsp_tools.utils.logger_config import WARNINGS_SAVEPATH

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
        err = f"Failed to ingest {filepath} to '{url}'."
        with open(filepath, "rb") as binary_io:
            try:
                logger.debug(f"REQUEST: POST to {url}, timeout: {timeout}, headers: {headers | {"Authorization": "*"}}")
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
                else:
                    user_msg = f"{err} See {WARNINGS_SAVEPATH} for more information."
                    print(user_msg)
                    log_msg = f"{err}. Response status code {res.status_code} '{res.text}'"
                    logger.error(log_msg)
                    raise PermanentConnectionError(log_msg)
            except requests.exceptions.RequestException as e:
                raise PermanentConnectionError(f"{err}. {e}") from e

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
            logger.info(msg)
            permissions = permissions_lookup.get(bitstream.permissions) if bitstream.permissions else None
            return True, BitstreamInfo(bitstream.value, res.internal_filename, permissions)
        except PermanentConnectionError:
            msg = f"Unable to upload file '{bitstream.value}' of resource '{res_label}' ({res_id})"
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
