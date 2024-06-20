from dataclasses import dataclass
from dataclasses import field
from datetime import datetime
from pathlib import Path

from loguru import logger
from requests import RequestException
from requests import Session
from requests.adapters import HTTPAdapter
from requests.adapters import Retry

from dsp_tools.models.exceptions import PermanentConnectionError
from dsp_tools.utils.logger_config import logger_savepath

STATUS_OK = 200
STATUS_INTERNAL_SERVER_ERROR = 500


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

    def _upload(self, filepath: Path) -> None:
        url = f"{self.dsp_ingest_url}/projects/{self.shortcode}/bulk-ingest/ingest/{filepath}"
        err = f"Failed to ingest {filepath} to '{url}'."
        with open(self.imgdir / filepath, "rb") as binary_io:
            content = binary_io.read()
        try:
            res = self.session.post(
                url=url,
                headers={"Content-Type": "application/octet-stream"},
                data=content,
                timeout=60,
            )
        except RequestException as e:
            raise PermanentConnectionError(f"{err}. {e}")
        if res.status_code != STATUS_OK:
            user_msg = f"{err} See logs for more details: {logger_savepath}"
            print(user_msg)
            log_msg = f"{err} Response status code {res.status_code} '{res.json()}'"
            logger.error(log_msg)
            raise PermanentConnectionError(log_msg)

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
