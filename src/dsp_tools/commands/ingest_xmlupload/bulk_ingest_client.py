import urllib.parse
from collections.abc import Iterator
from dataclasses import dataclass
from dataclasses import field
from pathlib import Path

import regex
from loguru import logger
from requests import JSONDecodeError

from dsp_tools.clients.openapi_ingest import openapi_client
from dsp_tools.commands.ingest_xmlupload.upload_files.upload_failures import UploadFailure
from dsp_tools.config.logger_config import LOGGER_SAVEPATH
from dsp_tools.error.exceptions import BadCredentialsError
from dsp_tools.error.exceptions import InputError

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

    bulk_ingest_api: openapi_client.BulkIngestApi
    shortcode: str
    imgdir: Path = field(default=Path.cwd())
    retrieval_failures = 0

    def upload_file(
        self,
        filepath: Path,
    ) -> UploadFailure | None:
        """
        Uploads a file to the ingest server.
        The load balancer on DSP servers currently has a timeout of 60s, so we need to use a timeout of 58s.
        See https://github.com/dasch-swiss/dsp-tools/pull/1335/files#r1882508057
        # noqa: DAR101
        # noqa: DAR201
        """
        timeout = 58
        quoted_file_name = regex.sub(r"^%2F", "", urllib.parse.quote(str(filepath), safe=""))
        url_for_logging = f"{self.dsp_ingest_url}/projects/{self.shortcode}/bulk-ingest/ingest/{quoted_file_name}"
        headers = {"Content-Type": "application/octet-stream"}
        err_msg = f"Failed to upload '{filepath}' to '{url_for_logging}'."
        try:
            logger.debug(f"REQUEST: POST to {url_for_logging}, timeout: {timeout}, headers: {headers}")
            with open(self.imgdir / filepath, "rb") as binary_io:
                api_response = self.bulk_ingest_api.post_projects_shortcode_bulk_ingest_ingest_file(
                    self.shortcode, quoted_file_name, binary_io, _request_timeout=timeout
                )
            logger.debug(f"RESPONSE: {api_response.status_code}")
        except OSError as e:
            err_msg = f"Cannot bulk-ingest {filepath}, because the file could not be opened/read: {e.strerror}"
            logger.error(err_msg)
            return UploadFailure(filepath, err_msg)
        except Exception as e:  # noqa: BLE001
            logger.error(err_msg)
            return UploadFailure(filepath, f"Exception of requests library: {e}")
        if api_response.status_code != STATUS_OK:
            logger.error(err_msg)
            return UploadFailure(filepath, api_response.reason, api_response.status_code, api_response.text)
        return None

    def trigger_ingest_process(self) -> None:
        """Start the ingest process on the server."""
        url_for_logging = f"{self.dsp_ingest_url}/projects/{self.shortcode}/bulk-ingest"
        timeout = 5
        logger.debug(f"REQUEST: POST to {url_for_logging}, timeout: {timeout}")
        res = self.bulk_ingest_api.post_projects_shortcode_bulk_ingest(self.shortcode, _request_timeout=timeout)
        logger.debug(f"RESPONSE: {res.status_code}: {res.text}")
        if res.status_code in [STATUS_UNAUTHORIZED, STATUS_FORBIDDEN]:
            raise BadCredentialsError("Unauthorized to start the ingest process. Please check your credentials.")
        if res.status_code == STATUS_NOT_FOUND:
            raise InputError(
                f"No assets have been uploaded for project {self.shortcode}. "
                "Before using the 'ingest-files' command, you must upload some files with the 'upload-files' command."
            )
        if res.status_code == STATUS_CONFLICT:
            msg = f"Ingest process on the server {self.dsp_ingest_url} is already running. Wait until it completes..."
            print(msg)
            logger.info(msg)
            return
        if res.status_code in [STATUS_INTERNAL_SERVER_ERROR, STATUS_SERVER_UNAVAILABLE]:
            raise InputError("Server is unavailable. Please try again later.")

        try:
            returned_shortcode = res.json().get("id")
            failed: bool = returned_shortcode != self.shortcode
        except JSONDecodeError:
            failed = True
        if failed:
            raise InputError("Failed to trigger the ingest process. Please check the server logs, or try again later.")
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
            InputError: if there are too many server errors in a row.
        """
        url_for_logging = f"{self.dsp_ingest_url}/projects/{self.shortcode}/bulk-ingest/mapping.csv"
        timeout = 5
        while True:
            logger.debug(f"REQUEST: GET to {url_for_logging}, timeout: {timeout}")
            res = self.bulk_ingest_api.get_projects_shortcode_bulk_ingest_mapping_csv(self.shortcode)
            logger.debug(f"RESPONSE: {res.status_code}")
            if res.status_code == STATUS_CONFLICT:
                self.retrieval_failures = 0
                logger.info("Ingest process is still running. Wait until it completes...")
                yield True
            elif res.status_code != STATUS_OK or not res.text.startswith("original,derivative"):
                self.retrieval_failures += 1
                if self.retrieval_failures > 15:
                    raise InputError(f"There were too many server errors. Please check the logs at {LOGGER_SAVEPATH}.")
                msg = "While retrieving the mapping CSV, the server responded with an unexpected status code/content."
                logger.error(msg)
                yield False
            else:
                logger.info("Ingest process completed.")
                break
        yield res.content.decode("utf-8")
