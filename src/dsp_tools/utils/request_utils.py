import json
from dataclasses import dataclass
import os
import time
from datetime import datetime
from json import JSONDecodeError
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
class GenericRequestParameters:
    method: Literal["POST", "GET", "PUT", "DELETE"]
    url: str
    timeout: int
    data: Any | None = None
    headers: dict[str, str] | None = None


def log_request(params: GenericRequestParameters) -> None:
    """Log a request"""
    dumpobj = {
        "method": params.method,
        "url": params.url,
        "timeout": params.timeout,
    }
    if params.data:
        data = params.data.copy()
        if "password" in data:
            data["password"] = "***"
        dumpobj["data"] = data
    if params.headers:
        dumpobj["headers"] = sanitize_headers(params.headers)
    logger.debug(f"REQUEST: {json.dumps(dumpobj, cls=SetEncoder)}")


def log_response(response: Response) -> None:
    """Log the response of a request."""
    dumpobj: dict[str, Any] = {
        "status_code": response.status_code,
        "headers": sanitize_headers(dict(response.headers)),
    }
    try:
        dumpobj["content"] = response.json()
    except JSONDecodeError:
        dumpobj["content"] = response.text
    logger.debug(f"RESPONSE: {json.dumps(dumpobj)}")


def sanitize_headers(headers: dict[str, str | bytes]) -> dict[str, str]:
    """Remove any authorisation of cookie information from the header."""

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
        logger.opt(exception=True).error(f"{msg} ({retry_counter=:})")
    else:
        logger.error(f"{msg} ({retry_counter=:})")
    time.sleep(2**retry_counter)


def log_and_raise_timeouts(error: TimeoutError | ReadTimeout) -> Never:
    """Logs the timeout errors that may occur during a request and raises our own."""
    msg = f"A '{error.__class__.__name__}' occurred during the connection to the DSP server."
    print(f"{datetime.now()}: {msg}")
    logger.exception(msg)
    raise PermanentTimeOutError(msg) from None


def should_retry(response: Response) -> bool:
    """Returns the decision if a retry of a request is sensible."""
    in_500_range = 500 <= response.status_code < 600
    try_again_later = "try again later" in response.text.lower()
    in_testing_env = os.getenv("DSP_TOOLS_TESTING") == "true"  # set in .github/workflows/tests-on-push.yml
    return (try_again_later or in_500_range) and not in_testing_env
