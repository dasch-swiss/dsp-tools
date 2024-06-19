from dataclasses import dataclass
from dataclasses import field
from datetime import datetime
from pathlib import Path

from loguru import logger
from requests import RequestException
from requests import Session
from requests.adapters import HTTPAdapter
from requests.adapters import Retry

from dsp_tools.models.exceptions import BadCredentialsError
from dsp_tools.models.exceptions import PermanentConnectionError
from dsp_tools.models.exceptions import UserError
from dsp_tools.utils.logger_config import logger_savepath

STATUS_OK = 200
STATUS_UNAUTHORIZED = 401
STATUS_INTERNAL_SERVER_ERROR = 500
STATUS_CONFLICT = 409


@dataclass
class MassIngestClient:
    """Client to upload multiple files to the ingest server and monitoring the ingest process."""

    dsp_ingest_url: str
    token: str
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
            status_forcelist=[STATUS_INTERNAL_SERVER_ERROR],
        )
        adapter = HTTPAdapter(max_retries=retry)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        self.session.headers["Authorization"] = f"Bearer {self.token}"

    def _upload(self, filepath: Path) -> None:
        url = f"{self.dsp_ingest_url}/projects/{self.shortcode}/bulk-ingest/upload/{filepath.name}"
        err = f"Failed to ingest {filepath} to '{url}'."
        with open(filepath, "rb") as binary_io:
            try:
                res = self.session.post(
                    url=url,
                    headers={"Content-Type": "application/octet-stream"},
                    data=binary_io,
                    timeout=60,
                )
                if res.status_code == STATUS_OK:
                    return
                elif res.status_code == STATUS_UNAUTHORIZED:
                    raise BadCredentialsError("Bad credentials")
                else:
                    user_msg = f"{err} See logs for more details: {logger_savepath}"
                    print(user_msg)
                    log_msg = f"{err}. Response status code {res.status_code} '{res.json()}'"
                    logger.error(log_msg)
                    raise PermanentConnectionError(log_msg)
            except RequestException as e:
                raise PermanentConnectionError(f"{err}. {e}")

    def upload_file(
        self,
        filepath: Path,
    ) -> bool:
        """Uploads a file to the ingest server."""
        try:
            self._upload(filepath)
            msg = f"Uploaded file '{filepath}'"
            print(f"{datetime.now()}: {msg}")
            logger.info(msg)
            return True
        except PermanentConnectionError as err:
            msg = f"Unable to upload file '{filepath}'"
            print(f"{datetime.now()}: WARNING: {msg}: {err.message}")
            logger.opt(exception=True).warning(msg)
            return False

    def kick_off_ingest(self) -> None:
        """Start the ingest process on the server."""
        url = f"{self.dsp_ingest_url}/projects/{self.shortcode}/bulk-ingest"
        res = self.session.post(url, timeout=5)
        if res.status_code == STATUS_CONFLICT:
            msg = f"Ingest process on the server {self.dsp_ingest_url} is already running. Wait until it completes..."
            print(msg)
            logger.info(msg)
        if res.json().get("id") != self.shortcode:
            raise UserError("Failed to kick off the ingest process.")
        print(f"Kicked off the ingest process on the server {self.dsp_ingest_url}. Wait until it completes...")
        logger.info(f"Kicked off the ingest process on the server {self.dsp_ingest_url}. Wait until it completes...")

    def retrieve_mapping(self) -> str | None:
        """Try to retrieve the mapping CSV from the server."""
        url = f"{self.dsp_ingest_url}/projects/{self.shortcode}/bulk-ingest/mapping.csv"
        res = self.session.get(url, timeout=5)
        if res.status_code == STATUS_CONFLICT:
            print("Ingest process is still running. Wait until it completes...")
            logger.info("Ingest process is still running. Wait until it completes...")
            return None
        elif not res.ok or not res.text.startswith("original,derivative"):
            print("Dubious error")
            logger.error("Dubious error")
            return None
        print("Ingest process completed.")
        logger.info("Ingest process completed.")
        return res.text

    def finalize(self) -> bool:
        """Delete the mapping file and the temporary directory where the unprocessed files were stored."""
        route = f"/projects/{self.shortcode}/bulk-ingest/finalize"
        res = self.session.post(route, timeout=5)
        if res.status_code != STATUS_OK or res.json().get("id") != self.shortcode:
            print("Failed to finalize the ingest process. Please clean up the server manually.")
            logger.error("Failed to finalize the ingest process. Please clean up the server manually.")
            return False
        logger.info("Finalized the ingest process.")
        return True
