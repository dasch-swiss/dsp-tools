import json
import os
import time
from dataclasses import dataclass
from dataclasses import field
from datetime import datetime
from typing import Any
from typing import Literal
from typing import Never

from loguru import logger
from requests import JSONDecodeError
from requests import ReadTimeout
from requests import Response

from dsp_tools.models.exceptions import PermanentTimeOutError
from dsp_tools.utils.set_encoder import SetEncoder


@dataclass
class RequestParameters:
    method: Literal["POST", "GET", "PUT", "DELETE"]
    url: str
    timeout: int
    data: dict[str, Any] | None = None
    data_serialized: bytes | None = field(init=False, default=None)
    headers: dict[str, str] | None = None
    files: dict[str, tuple[str, Any]] | None = None

    def __post_init__(self) -> None:
        self.data_serialized = self._serialize_payload(self.data)

    def _serialize_payload(self, payload: dict[str, Any] | None) -> bytes | None:
        # If data is not encoded as bytes, issues can occur with non-ASCII characters,
        # where the content-length of the request will turn out to be different from the actual length.
        return json.dumps(payload, cls=SetEncoder, ensure_ascii=False).encode("utf-8") if payload else None

    def as_kwargs(self) -> dict[str, Any]:
        return {
            "method": self.method,
            "url": self.url,
            "timeout": self.timeout,
            "data": self.data_serialized,
            "headers": self.headers,
            "files": self.files,
        }


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
        dumpobj["files"] = params.files["file"][0]
    logger.debug(f"REQUEST: {json.dumps(dumpobj, cls=SetEncoder)}")


def log_response(response: Response) -> None:
    """Log the response of a request."""
    dumpobj: dict[str, Any] = {
        "status_code": response.status_code,
        "headers": sanitize_headers(dict(response.headers)) if response.headers else "",
    }
    try:
        dumpobj["content"] = response.json()
    except JSONDecodeError:
        dumpobj["content"] = response.text
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
    """Log the reason for a request failure and sleep."""
    msg = f"{reason}: Try reconnecting to DSP server, next attempt in {2**retry_counter} seconds..."
    print(f"{datetime.now()}: {msg}")
    if exc_info:
        logger.exception(f"{msg} ({retry_counter=:})")
    else:
        logger.error(f"{msg} ({retry_counter=:})")
    time.sleep(2**retry_counter)


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
