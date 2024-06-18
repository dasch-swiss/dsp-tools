from dataclasses import dataclass
from dataclasses import field
from typing import Any

from loguru import logger
from requests import Session
from requests.adapters import HTTPAdapter
from requests.adapters import Retry

from dsp_tools.models.exceptions import UserError

STATUS_OK = 200
STATUS_UNAUTHORIZED = 401
STATUS_CONFLICT = 409
STATUS_INTERNAL_SERVER_ERROR = 500


@dataclass
class IngestKickoffClient:
    """Client to kick off the ingest process on the server, and to retrieve the mapping file once it has finished."""

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

    def kick_off_ingest(self) -> None:
        url = f"{self.dsp_ingest_url}/projects/{self.shortcode}/bulk-ingest"
        headers = {"Authorization": f"Bearer {self.token}"}
        res: dict[str, Any] = self.session.post(url, headers=headers, timeout=5).json()
        if res.get("id") != self.shortcode:
            raise UserError("Failed to kick off the ingest process.")
        print(f"Kicked off the ingest process on the server {self.dsp_ingest_url}. Wait until it completes...")
        logger.info(f"Kicked off the ingest process on the server {self.dsp_ingest_url}. Wait until it completes...")

    def try_download(self) -> str | None:
        url = f"{self.dsp_ingest_url}/projects/{self.shortcode}/bulk-ingest/mapping.csv"
        res = self.session.get(url, headers={"Authorization": f"Bearer {self.token}"}, timeout=5)
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
