from __future__ import annotations

import json
import os
import time
import warnings
from dataclasses import dataclass
from dataclasses import field
from datetime import datetime
from typing import Any
from typing import Literal
from typing import Never
from typing import Union

from loguru import logger
from requests import JSONDecodeError
from requests import ReadTimeout
from requests import RequestException
from requests import Response

from dsp_tools.commands.project.legacy_models.context import Context
from dsp_tools.commands.project.legacy_models.helpers import OntoIri
from dsp_tools.config.logger_config import LOGGER_SAVEPATH
from dsp_tools.error.custom_warnings import DspToolsUnexpectedStatusCodeWarning
from dsp_tools.error.exceptions import DspToolsRequestException
from dsp_tools.error.exceptions import PermanentTimeOutError


@dataclass
class PostFiles:
    """One or more files to be uploaded in a POST request."""

    files: list[PostFile]

    def to_dict(self) -> dict[str, tuple[str, Any, str] | tuple[str, Any]]:
        return {x.file_name: x.to_tuple() for x in self.files}


@dataclass
class PostFile:
    file_name: str
    fileobj: Any
    content_type: str | None = None

    def to_tuple(self) -> tuple[str, Any, str] | tuple[str, Any]:
        if self.content_type:
            return self.file_name, self.fileobj, self.content_type
        return self.file_name, self.fileobj


class SetEncoder(json.JSONEncoder):
    """Encoder used to serialize objects to JSON that would by default not be serializable"""

    def default(self, o: Union[set[Any], Context, OntoIri]) -> Any:
        """Return a serializable object for o"""
        if isinstance(o, set):
            return list(o)
        elif isinstance(o, Context):
            return o.toJsonObj()
        elif isinstance(o, OntoIri):
            return {"iri": o.iri, "hashtag": o.hashtag}
        return json.JSONEncoder.default(self, o)


@dataclass
class RequestParameters:
    method: Literal["POST", "GET", "PUT", "DELETE"]
    url: str
    timeout: int
    data: dict[str, Any] | None = None
    data_serialized: bytes | None = field(init=False, default=None)
    headers: dict[str, str] | None = None
    files: PostFiles | None = None

    def __post_init__(self) -> None:
        self.data_serialized = self._serialize_payload(self.data)

    def _serialize_payload(self, payload: dict[str, Any] | None) -> bytes | None:
        # If data is not encoded as bytes, issues can occur with non-ASCII characters,
        # where the content-length of the request will turn out to be different from the actual length.
        return json.dumps(payload, cls=SetEncoder, ensure_ascii=False).encode("utf-8") if payload else None

    def as_kwargs(self) -> dict[str, Any]:
        kwargs = {
            "method": self.method,
            "url": self.url,
            "timeout": self.timeout,
            "data": self.data_serialized,
            "headers": self.headers,
        }
        if self.files:
            kwargs["files"] = self.files.to_dict()
        return kwargs


def log_request(params: RequestParameters, extra_headers: dict[str, Any] | None = None) -> None:
    """Logs the request."""
    dumpobj = {
        "method": params.method,
        "url": params.url,
        "timeout": params.timeout,
    }
    headers_to_log = {}
    if extra_headers:
        headers_to_log = extra_headers
    if params.headers:
        headers_to_log = headers_to_log | params.headers
    dumpobj["headers"] = sanitize_headers(headers_to_log)
    if params.data:
        data = params.data.copy()
        if "password" in data:
            data["password"] = "***"
        dumpobj["data"] = data
    if params.files:
        dumpobj["files"] = [x.file_name for x in params.files.files]
    logger.debug(f"REQUEST: {json.dumps(dumpobj, cls=SetEncoder)}")


def log_response(response: Response, include_response_content: bool = True) -> None:
    """Log the response of a request."""
    dumpobj: dict[str, Any] = {
        "status_code": response.status_code,
        "headers": sanitize_headers(dict(response.headers)) if response.headers else "",
    }
    if include_response_content:
        try:
            dumpobj["content"] = response.json()
        except JSONDecodeError:
            dumpobj["content"] = response.text
    else:
        dumpobj["content"] = "too big to be logged"
    logger.debug(f"RESPONSE: {json.dumps(dumpobj)}")


def sanitize_headers(headers: dict[str, str | bytes]) -> dict[str, str]:
    """Remove sensitive information from request headers."""

    def _mask(key: str, value: str | bytes) -> str:
        if isinstance(value, bytes):
            value = value.decode("utf-8")
        if key == "Authorization" and value.startswith("Bearer "):
            return "Bearer ***"
        if key == "Set-Cookie":
            return "***"
        return value

    return {k: _mask(k, v) for k, v in headers.items()}


def log_request_failure_and_sleep(reason: str, retry_counter: int, exc_info: bool) -> None:
    """
    Log the reason for a request failure and sleep.

    =============  ================  =============================
    retry_counter  seconds to sleep  cumulative waiting time (min)
    =============  ================  =============================
    0              1                 0
    1              2                 0
    2              4                 0
    3              8                 0
    4              16                0
    5              32                1
    6              64                2
    7              128               4
    8              256               9
    9              300               14
    10             300               19
    11             300               24
    12             300               29
    15             300               44
    18             300               59
    24             300               89
    30             300               119
    =============  ================  =============================
    """
    sleep_time = min(2**retry_counter, 300)
    msg = f"{reason}: Try reconnecting to DSP server, next attempt in {sleep_time} seconds..."
    print(f"{datetime.now()}: {msg}")
    if exc_info:
        logger.exception(f"{msg} ({retry_counter=:})")
    else:
        logger.error(f"{msg} ({retry_counter=:})")
    time.sleep(sleep_time)


def log_and_raise_timeouts(error: TimeoutError | ReadTimeout) -> Never:
    """Log a timeout error raised by a request and raise our own PermanentTimeOutError"""
    msg = f"A '{error.__class__.__name__}' occurred during the connection to the DSP server."
    print(f"{datetime.now()}: {msg}")
    logger.error(msg)
    raise PermanentTimeOutError(msg) from None


def should_retry(response: Response) -> bool:
    """Returns the decision if a retry of a request is sensible."""
    in_500_range = 500 <= response.status_code < 600
    try_again_later = "try again later" in response.text.lower()
    in_testing_env = os.getenv("DSP_TOOLS_TESTING") == "true"  # set in .github/workflows/tests-on-push.yml
    return (try_again_later or in_500_range) and not in_testing_env


def log_and_raise_request_exception(error: RequestException) -> Never:
    msg = (
        f"During an API call the following exception occurred. "
        f"Please contact info@dasch.swiss with the log file at {LOGGER_SAVEPATH} "
        f"if you required help resolving the issue.\n"
        f"Original exception name: {error.__class__.__name__}\n"
    )
    if error.request:
        msg += f"Original request: {error.request.method} {error.request.url}"
    logger.exception(msg)
    raise DspToolsRequestException(msg) from None


def log_and_warn_unexpected_non_ok_response(status_code: int, response_text: str) -> None:
    resp_txt = response_text[:200] if len(response_text) > 200 else response_text
    msg = (
        "We got an unexpected API response during the following request. "
        "Please contact the dsp-tools development team (at info@dasch.swiss) with your log file "
        "so that we can handle this more gracefully in the future.\n"
        f"Response status code: {status_code}\n"
        f"Original Message: {resp_txt}"
    )
    logger.warning(msg)
    warnings.warn(DspToolsUnexpectedStatusCodeWarning(msg))
