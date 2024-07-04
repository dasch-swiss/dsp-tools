from dataclasses import dataclass
from dataclasses import field
from pathlib import Path

from loguru import logger
from requests import RequestException
from requests import Session
from requests.adapters import HTTPAdapter
from requests.adapters import Retry

from dsp_tools.commands.ingest_xmlupload.upload_files.upload_failures import UploadFailure
from dsp_tools.models.exceptions import UserError
from dsp_tools.utils.logger_config import LOGGER_SAVEPATH

STATUS_OK = 200
STATUS_UNAUTHORIZED = 401
STATUS_FORBIDDEN = 403
STATUS_NOT_FOUND = 404
STATUS_CONFLICT = 409
STATUS_INTERNAL_SERVER_ERROR = 500
STATUS_SERVER_UNAVAILABLE = 503


@dataclass
class BulkIngestClient:
    """Client to upload multiple files to the ingest server and monitor the ingest process."""

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

    def upload_file(
        self,
        filepath: Path,
    ) -> UploadFailure | None:
        """Uploads a file to the ingest server."""
        url = f"{self.dsp_ingest_url}/projects/{self.shortcode}/bulk-ingest/ingest/{filepath}"
        err_msg = f"Failed to upload '{filepath}' to '{url}'."
        try:
            with open(self.imgdir / filepath, "rb") as binary_io:
                content = binary_io.read()
        except OSError as e:
            logger.error(err_msg)
            return UploadFailure(filepath, f"File could not be opened/read: {e.strerror}")
        try:
            res = self.session.post(
                url=url,
                headers={"Content-Type": "application/octet-stream"},
                data=content,
                timeout=60,
            )
        except RequestException as e:
            logger.error(err_msg)
            return UploadFailure(filepath, f"Exception of requests library: {e}")
        if res.status_code != STATUS_OK:
            logger.error(err_msg)
            reason = f"Response {res.status_code}: {res.text}" if res.text else f"Response {res.status_code}"
            return UploadFailure(filepath, reason)

        logger.info(f"Uploaded file '{filepath}' to '{url}'")
        return None

    def trigger_ingest_process(self) -> None:
        """Start the ingest process on the server."""
        url = f"{self.dsp_ingest_url}/projects/{self.shortcode}/bulk-ingest"
        res = self.session.post(url, timeout=5)
        if res.status_code in [STATUS_UNAUTHORIZED, STATUS_FORBIDDEN]:
            raise UserError("Unauthorized to start the ingest process. Please check your credentials.")
        if res.status_code == STATUS_NOT_FOUND:
            raise UserError(
                f"No assets have been uploaded for project {self.shortcode}. "
                "Before using the 'ingest-files' command, you must upload some files with the 'upload-files' command."
            )
        if res.status_code == STATUS_CONFLICT:
            msg = f"Ingest process on the server {self.dsp_ingest_url} is already running. Wait until it completes..."
            print(msg)
            logger.info(msg)
        if res.status_code in [STATUS_INTERNAL_SERVER_ERROR, STATUS_SERVER_UNAVAILABLE]:
            raise UserError("Server is unavailable. Please try again later.")
        if res.json().get("id") != self.shortcode:
            raise UserError("Failed to trigger the ingest process. Please check the server logs, or try again later.")
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
            msg = (
                "Dubious error while retrieving the mapping CSV. "
                f"If this happens again at the next attempt, please check the logs at {LOGGER_SAVEPATH}."
            )
            print(msg)
            logger.error(msg)
            return None
        print("Ingest process completed.")
        logger.info("Ingest process completed.")
        return res.text
