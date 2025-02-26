import json
import time
from datetime import datetime
from typing import Any
from typing import Never

from loguru import logger
from requests import JSONDecodeError
from requests import ReadTimeout
from requests import Response

from dsp_tools.models.exceptions import PermanentTimeOutError


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
    """Remove sensistive information from request headers."""

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
    """Log a timeout error raised by a request and raise our own PermanentTimeOutError"""
    msg = f"A '{error.__class__.__name__}' occurred during the connection to the DSP server."
    print(f"{datetime.now()}: {msg}")
    logger.exception(msg)
    raise PermanentTimeOutError(msg) from None
