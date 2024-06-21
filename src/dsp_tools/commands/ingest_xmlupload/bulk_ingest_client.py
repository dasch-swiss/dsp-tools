from dataclasses import dataclass
from dataclasses import field
from datetime import datetime
from pathlib import Path

from loguru import logger
from requests import RequestException
from requests import Session
from requests.adapters import HTTPAdapter
from requests.adapters import Retry

from dsp_tools.commands.ingest_xmlupload.upload_files.upload_failures import UploadFailureDetail
from dsp_tools.models.exceptions import UserError
from dsp_tools.utils.logger_config import logger_savepath

STATUS_OK = 200
STATUS_INTERNAL_SERVER_ERROR = 500
STATUS_CONFLICT = 409


@dataclass
class BulkIngestClient:
    """Client to upload multiple files to the ingest server and monitoring the ingest process."""

    dsp_ingest_url: str
    token: str
    shortcode: str
    imgdir: Path = field(default=Path.cwd())
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

    def _upload(self, filepath: Path) -> UploadFailureDetail | None:
        url = f"{self.dsp_ingest_url}/projects/{self.shortcode}/bulk-ingest/ingest/{filepath}"
        err_msg = f"Failed to ingest '{filepath}' to '{url}'."
        try:
            with open(self.imgdir / filepath, "rb") as binary_io:
                content = binary_io.read()
        except OSError as e:
            logger.error(err_msg)
            return UploadFailureDetail(filepath, f"File could not be opened/read: {e.strerror}")
        try:
            res = self.session.post(
                url=url,
                headers={"Content-Type": "application/octet-stream"},
                data=content,
                timeout=60,
            )
        except RequestException as e:
            logger.error(err_msg)
            return UploadFailureDetail(filepath, f"Exception of requests library: {e}")
        if res.status_code != STATUS_OK:
            logger.error(err_msg)
            reason = f"Response {res.status_code}: {res.text}" if res.text else f"Response {res.status_code}"
            return UploadFailureDetail(filepath, reason)
        return None

    def upload_file(
        self,
        filepath: Path,
    ) -> UploadFailureDetail | None:
        """Uploads a file to the ingest server."""
        if failure_details := self._upload(filepath):
            err_msg = f"Failed to ingest '{filepath}'.\n"
            err_msg += f"Reason: {failure_details.reason}\n"
            err_msg += f"See logs for more details: {logger_savepath}"
            print(err_msg)
            return failure_details
        msg = f"Uploaded file '{filepath}'"
        print(f"{datetime.now()}: {msg}")
        logger.info(msg)
        return None

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
        route = f"{self.dsp_ingest_url}/projects/{self.shortcode}/bulk-ingest/finalize"
        res = self.session.post(route, timeout=5)
        if res.status_code != STATUS_OK or res.json().get("id") != self.shortcode:
            print("Failed to finalize the ingest process. Please clean up the server manually.")
            logger.error("Failed to finalize the ingest process. Please clean up the server manually.")
            return False
        logger.info("Finalized the ingest process.")
        return True
