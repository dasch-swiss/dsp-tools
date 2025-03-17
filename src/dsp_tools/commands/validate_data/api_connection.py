from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import requests
from loguru import logger
from requests import RequestException
from requests import Response
from requests import Timeout

from dsp_tools.models.exceptions import InternalError
from dsp_tools.utils.request_utils import PostFiles


@dataclass
class ApiConnection:
    api_url: str

    def get_with_endpoint(self, endpoint: str, headers: dict[str, Any] | None = None, timeout: int = 42) -> Response:
        url = f"{self.api_url}/{endpoint}"
        return self.get_with_url(url, headers, timeout)

    def get_with_url(self, url: str, headers: dict[str, Any] | None = None, timeout: int = 42) -> Response:
        logger.debug(f"REQUEST: GET to {url} | Timeout: {timeout} | Headers: {headers}")
        try:
            return requests.get(url=url, headers=headers, timeout=timeout)
        except (TimeoutError, Timeout) as err:
            logger.error(err)
            raise InternalError("TimeoutError occurred. See logs for details.") from None
        except (ConnectionError, RequestException) as err:
            logger.error(err)
            raise InternalError("ConnectionError occurred. See logs for details.") from None

    def post_files(
        self, endpoint: str, files: PostFiles, headers: dict[str, Any] | None = None, timeout: int = 42
    ) -> Response:
        file_dict = files.to_dict()
        url = f"{self.api_url}/{endpoint}"
        logger.debug(f"REQUEST: POST FILES to {url} | Timeout: {timeout} | Headers: {headers}")
        try:
            return requests.post(url, files=file_dict, timeout=timeout)
        except (TimeoutError, Timeout) as err:
            logger.error(err)
            raise InternalError("TimeoutError occurred. See logs for details.") from None
        except (ConnectionError, RequestException) as err:
            logger.error(err)
            raise InternalError("ConnectionError occurred. See logs for details.") from None
