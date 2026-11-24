from __future__ import annotations

import logging
import urllib
from dataclasses import dataclass
from dataclasses import field
from http import HTTPStatus
from pathlib import Path

import requests
from requests import Session
from requests.adapters import HTTPAdapter
from requests.adapters import Retry

from dsp_vre_lib.clients.authentication_client import AuthenticationClient
from dsp_vre_lib.clients.exceptions import BadCredentialsError
from dsp_vre_lib.clients.exceptions import InvalidIngestFileNameError
from dsp_vre_lib.clients.exceptions import PermanentConnectionError
from dsp_vre_lib.clients.request_utils import RequestParameters
from dsp_vre_lib.clients.request_utils import log_request
from dsp_vre_lib.clients.request_utils import log_response

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class IngestResponse:
    """Wrapper around `internal_filename`"""

    internal_filename: str


@dataclass
class DspIngestClientLive:
    """Client for uploading assets to the DSP-Ingest."""

    dsp_ingest_url: str
    auth: AuthenticationClient
    shortcode: str
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
            status_forcelist=[HTTPStatus.INTERNAL_SERVER_ERROR.value],
        )
        adapter = HTTPAdapter(max_retries=retry)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

    def ingest(self, filepath: Path) -> IngestResponse:
        """Uploads a file to the ingest server and returns the IngestResponse.

        This function sends a POST request to the ingest server with the file to upload.
        It will retry the request 6 times in case of a connection, timeout or internal server error.

        After all retry attempts are exhausted it will raise exceptions if the upload failed.
        The http status code is also checked and if it is not 200, a PermanentConnectionError is raised.

        The load balancer on DSP servers currently has a timeout of 10m,
        so we need to use a slightly shorter timeout of 9m.
        See https://linear.app/dasch/issue/INFRA-847/increase-traefik-readtimeout

        Args:
            filepath: Path to the file to ingest, could be either absolute or relative.

        Raises:
            BadCredentialsError: If the server refuses the upload because the user has no write access
                to the project, or because the token is invalid.
            PermanentConnectionError: If the connection fails.
            InvalidIngestFileNameError: If the ingest server rejects the name of the file.

        Returns:
            IngestResponse: The internal filename of the uploaded file.
        """
        filename = urllib.parse.quote(filepath.name)
        url = f"{self.dsp_ingest_url}/projects/{self.shortcode}/assets/ingest/{filename}"
        headers = {
            "Authorization": f"Bearer {self.auth.get_token()}",
            "Content-Type": "application/octet-stream",
        }
        timeout = 9 * 60
        params = RequestParameters(method="POST", url=url, timeout=timeout, headers=headers)
        with open(filepath, "rb") as binary_io:
            try:
                log_request(params)
                res = self.session.post(
                    url=params.url,
                    headers=params.headers,
                    data=binary_io,
                    timeout=params.timeout,
                )
                log_response(res, status_code=res.status_code)
            except requests.exceptions.RequestException as e:
                logger.exception(f"Ingest request failed: {url}")
                raise PermanentConnectionError() from e

            if res.ok:
                return IngestResponse(internal_filename=res.json()["internalFilename"])
            # As of 2026-10, DSP-INGEST answers 401, not 403, if the user lacks write access (see clients/CLAUDE.md).
            elif res.status_code in (HTTPStatus.UNAUTHORIZED, HTTPStatus.FORBIDDEN):
                raise BadCredentialsError(
                    f"The ingest server refused the upload to project {self.shortcode}. "
                    "Either you have no write access to the project, or your login token is invalid or expired. "
                    "SystemAdmins always have write access. "
                    "By default, ProjectAdmins and all project members have it, too."
                )
            elif res.status_code == HTTPStatus.BAD_REQUEST and res.text == "Invalid value for: path parameter filename":
                raise InvalidIngestFileNameError()
            else:
                raise PermanentConnectionError()
