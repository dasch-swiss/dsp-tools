import urllib.parse
from dataclasses import dataclass
from dataclasses import field
from pathlib import Path
from typing import Iterator

import regex
from loguru import logger
from requests import JSONDecodeError
from requests import RequestException
from requests import Session
from requests.adapters import HTTPAdapter
from requests.adapters import Retry

from dsp_tools.commands.ingest_xmlupload.upload_files.upload_failures import UploadFailure
from dsp_tools.models.exceptions import BadCredentialsError
from dsp_tools.models.exceptions import UserError
from dsp_tools.utils.authentication_client import AuthenticationClient
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
    authentication_client: AuthenticationClient
    shortcode: str
    imgdir: Path = field(default=Path.cwd())
    session: Session = field(init=False)
    retrieval_failures = 0

    def __post_init__(self) -> None:
        retries = 6
        self.session = Session()
        retry = Retry(
            total=retries,
            read=retries,
            connect=retries,
            backoff_factor=0.3,
            allowed_methods=None,  # means all methods
            status_forcelist=[STATUS_INTERNAL_SERVER_ERROR, STATUS_SERVER_UNAVAILABLE],
        )
        adapter = HTTPAdapter(max_retries=retry)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        self.session.headers["Authorization"] = f"Bearer {self.authentication_client.get_token()}"

    def upload_file(
        self,
        filepath: Path,
    ) -> UploadFailure | None:
        """Uploads a file to the ingest server."""
        try:
            with open(self.imgdir / filepath, "rb") as binary_io:
                content = binary_io.read()
        except OSError as e:
            err_msg = f"Cannot bulk-ingest {filepath}, because the file could not be opened/read: {e.strerror}"
            logger.error(err_msg)
            return UploadFailure(filepath, err_msg)
        url = self._build_url_for_bulk_ingest_ingest_route(filepath)
        headers = {"Content-Type": "application/octet-stream"}
        timeout = 600
        err_msg = f"Failed to upload '{filepath}' to '{url}'."
        try:
            logger.debug(f"REQUEST: POST to {url}, timeout: {timeout}, headers: {headers}")
            res = self.session.post(
                url=url,
                headers=headers,
                data=content,
                timeout=timeout,
            )
            logger.debug(f"RESPONSE: {res.status_code}")
        except RequestException as e:
            logger.error(err_msg)
            return UploadFailure(filepath, f"Exception of requests library: {e}")
        if res.status_code != STATUS_OK:
            logger.error(err_msg)
            reason = f"Response {res.status_code}: {res.text}" if res.text else f"Response {res.status_code}"
            return UploadFailure(filepath, reason)
        return None

    def _build_url_for_bulk_ingest_ingest_route(self, filepath: Path) -> str:
        """
        Remove the leading slash of absolute filepaths,
        because the /project/<shortcode>/bulk-ingest/ingest route only accepts relative paths.
        The leading slash has to be added again in the "ingest-xmlupload" step, when applying the ingest ID.

        Args:
            filepath: filepath

        Returns:
            url
        """
        quoted = regex.sub(r"^\/", "", urllib.parse.quote(str(filepath)))
        return f"{self.dsp_ingest_url}/projects/{self.shortcode}/bulk-ingest/ingest/{quoted}"

    def trigger_ingest_process(self) -> None:
        """Start the ingest process on the server."""
        url = f"{self.dsp_ingest_url}/projects/{self.shortcode}/bulk-ingest"
        timeout = 5
        logger.debug(f"REQUEST: POST to {url}, timeout: {timeout}")
        res = self.session.post(url, timeout=timeout)
        logger.debug(f"RESPONSE: {res.status_code}: {res.text}")
        if res.status_code in [STATUS_UNAUTHORIZED, STATUS_FORBIDDEN]:
            raise BadCredentialsError("Unauthorized to start the ingest process. Please check your credentials.")
        if res.status_code == STATUS_NOT_FOUND:
            raise UserError(
                f"No assets have been uploaded for project {self.shortcode}. "
                "Before using the 'ingest-files' command, you must upload some files with the 'upload-files' command."
            )
        if res.status_code == STATUS_CONFLICT:
            msg = f"Ingest process on the server {self.dsp_ingest_url} is already running. Wait until it completes..."
            print(msg)
            logger.info(msg)
            return
        if res.status_code in [STATUS_INTERNAL_SERVER_ERROR, STATUS_SERVER_UNAVAILABLE]:
            raise UserError("Server is unavailable. Please try again later.")

        try:
            returned_shortcode = res.json().get("id")
            failed: bool = returned_shortcode != self.shortcode
        except JSONDecodeError:
            failed = True
        if failed:
            raise UserError("Failed to trigger the ingest process. Please check the server logs, or try again later.")
        print(f"Kicked off the ingest process on the server {self.dsp_ingest_url}. Wait until it completes...")
        logger.info(f"Kicked off the ingest process on the server {self.dsp_ingest_url}. Wait until it completes...")

    def retrieve_mapping_generator(self) -> Iterator[str | bool]:
        """
        Try to retrieve the mapping CSV from the server.

        Yields:
            True if the ingest process is still running.
            False if there is a server error.
            The mapping CSV if the ingest process has completed.

        Raises:
            UserError: if there are too many server errors in a row.
        """
        url = f"{self.dsp_ingest_url}/projects/{self.shortcode}/bulk-ingest/mapping.csv"
        timeout = 5
        while True:
            logger.debug(f"REQUEST: GET to {url}, timeout: {timeout}")
            res = self.session.get(url, timeout=timeout)
            logger.debug(f"RESPONSE: {res.status_code}")
            if res.status_code == STATUS_CONFLICT:
                self.retrieval_failures = 0
                logger.info("Ingest process is still running. Wait until it completes...")
                yield True
            elif res.status_code != STATUS_OK or not res.text.startswith("original,derivative"):
                self.retrieval_failures += 1
                if self.retrieval_failures > 15:
                    raise UserError(f"There were too many server errors. Please check the logs at {LOGGER_SAVEPATH}.")
                msg = "While retrieving the mapping CSV, the server responded with an unexpected status code/content."
                logger.error(msg)
                yield False
            else:
                logger.info("Ingest process completed.")
                break
        yield res.content.decode("utf-8")
