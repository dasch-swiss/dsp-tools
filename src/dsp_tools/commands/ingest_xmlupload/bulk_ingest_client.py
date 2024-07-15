import urllib
from dataclasses import dataclass
from dataclasses import field
from pathlib import Path

from loguru import logger
from requests import RequestException
from requests import Session
from requests.adapters import HTTPAdapter
from requests.adapters import Retry

from dsp_tools.commands.ingest_xmlupload.upload_files.upload_failures import UploadFailure

STATUS_OK = 200
STATUS_INTERNAL_SERVER_ERROR = 500


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
        filename = urllib.parse.quote(filepath.name)
        url = f"{self.dsp_ingest_url}/projects/{self.shortcode}/bulk-ingest/ingest/{filename}"
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
