from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

import requests
from loguru import logger
from requests import Session
from requests.adapters import HTTPAdapter
from requests.adapters import Retry

from dsp_tools.models.exceptions import BadCredentialsError
from dsp_tools.models.exceptions import PermanentConnectionError
from dsp_tools.models.exceptions import UserError
from dsp_tools.utils.logger_config import logger_savepath


@dataclass(frozen=True)
class IngestResponse:
    internal_filename: str


class IngestClient(Protocol):
    def ingest(self, shortcode: str, filepath: Path) -> IngestResponse:
        """Uploads a file to the ingest server and returns the IngestResponse.

        This function sends a POST request to the ingest server with the file to upload.
        It will retry the request 6 times in case of a connection, timeout or internal server error.

        After all retry attempts are exhausted it will raise exceptions if the upload failed.
        The http status code is also checked and if it is not 200, a PermanentConnectionError is raised.

        Args:
            shortcode: The shortcode of the project to ingest to.
            filepath: Path to the file to ingest, could be either absolute or relative.

        Raises:
            BadCredentialsError: If the credentials are invalid.
            PermanentConnectionError: If the connection fails.

        """


@dataclass(frozen=True)
class DspIngestClient(IngestClient):
    dsp_ingest_url: str
    token: str

    @staticmethod
    def _retry_session(retries: int, session: Session | None = None, backoff_factor: float = 0.3) -> Session:
        session = session or requests.Session()
        retry = Retry(
            total=retries,
            read=retries,
            connect=retries,
            backoff_factor=backoff_factor,
            allowed_methods=None,  # means all methods
            status_forcelist=[500],
        )
        adapter = HTTPAdapter(max_retries=retry)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        return session

    def ingest(self, shortcode: str, filepath: Path) -> IngestResponse:
        s = DspIngestClient._retry_session(retries=6)
        url = f"{self.dsp_ingest_url}/projects/{shortcode}/assets/ingest/{filepath.name}"
        err = f"Failed to ingest {filepath} to '{url}'."
        try:
            with open(filepath, "rb") as binary_io:
                res = s.post(
                    url=url,
                    headers={"Authorization": f"Bearer {self.token}", "Content-Type": "application/octet-stream"},
                    data=binary_io,
                    timeout=60,
                )
                if res.status_code == 200:
                    return IngestResponse(internal_filename=res.json()["internalFilename"])
                elif res.status_code == 401:
                    raise BadCredentialsError("Bad credentials")
                else:
                    user_msg = f"{err} See logs for more details: {logger_savepath}"
                    print(user_msg)
                    log_msg = f"{err}. Response status code {res.status_code} '{res.json()}'"
                    logger.error(log_msg)
                    raise PermanentConnectionError(log_msg)
        except FileNotFoundError as e:
            logger.error(e)
            raise UserError(f"{err}. File {filepath} not found.")
        except requests.exceptions.RequestException as e:
            raise PermanentConnectionError(f"{err}. {e}")
