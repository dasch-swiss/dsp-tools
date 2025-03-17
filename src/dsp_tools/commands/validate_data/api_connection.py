from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import requests
from loguru import logger
from requests import RequestException
from requests import Response
from requests import Timeout

from dsp_tools.models.exceptions import InternalError
from dsp_tools.utils.request_utils import RequestParameters
from dsp_tools.utils.request_utils import log_request
from dsp_tools.utils.request_utils import log_response


@dataclass
class ApiConnection:
    api_url: str

    def get_with_endpoint(self, endpoint: str, headers: dict[str, Any] | None = None, timeout: int = 42) -> Response:
        url = f"{self.api_url}/{endpoint}"
        return self.get_with_url(url, headers, timeout)

    def get_with_url(self, url: str, headers: dict[str, Any] | None = None, timeout: int = 42) -> Response:
        log_request(RequestParameters("GET", url, timeout, headers=headers))
        try:
            response = requests.get(url=url, headers=headers, timeout=timeout)
            log_response(response)
            return response
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
        log_request(RequestParameters("POST", url, timeout, files=file_dict, headers=headers))
        try:
            response = requests.post(url, files=file_dict, timeout=timeout)
            log_response(response)
            return response
        except (TimeoutError, Timeout) as err:
            logger.error(err)
            raise InternalError("TimeoutError occurred. See logs for details.") from None
        except (ConnectionError, RequestException) as err:
            logger.error(err)
            raise InternalError("ConnectionError occurred. See logs for details.") from None


@dataclass
class PostFiles:
    files: list[OneFile]

    def to_dict(self) -> dict[str, tuple[str, str, str]]:
        return {x.file_name: x.to_tuple() for x in self.files}


@dataclass
class OneFile:
    file_name: str
    file_content: str
    file_format: str

    def to_tuple(self) -> tuple[str, str, str]:
        return self.file_name, self.file_content, self.file_format
