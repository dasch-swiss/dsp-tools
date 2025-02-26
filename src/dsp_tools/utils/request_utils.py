import json
from dataclasses import dataclass
from datetime import datetime
from json import JSONDecodeError
from typing import Any
from typing import Literal
from typing import Never

from loguru import logger
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


def log_response(response: Response) -> None:
    """Log the response to a request."""
    dumpobj: dict[str, Any] = {
        "status_code": response.status_code,
        "headers": sanitize_headers(dict(response.headers)),
    }
    try:
        dumpobj["content"] = response.json()
    except JSONDecodeError:
        dumpobj["content"] = response.text
    logger.debug(f"RESPONSE: {json.dumps(dumpobj)}")


def log_and_raise_timeouts(error: TimeoutError | ReadTimeout) -> Never:
    """Logs the timeout errors that may occurr during a request and raises our own."""
    msg = f"A '{error.__class__.__name__}' occurred during the connection to the DSP server."
    print(f"{datetime.now()}: {msg}")
    logger.exception(msg)
    raise PermanentTimeOutError(msg) from None
