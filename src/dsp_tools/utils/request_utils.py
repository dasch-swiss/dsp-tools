import json
from dataclasses import dataclass
from json import JSONDecodeError
from typing import Any
from typing import Literal

from loguru import logger
from requests import Response

from dsp_tools.utils.set_encoder import SetEncoder


@dataclass
class GenericRequestParameters:
    method: Literal["POST", "GET", "PUT", "DELETE"]
    url: str
    timeout: int
    data: Any | None = None
    headers: dict[str, str] | None = None


def log_request(params: GenericRequestParameters) -> None:
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
    dumpobj: dict[str, Any] = {
        "status_code": response.status_code,
        "headers": sanitize_headers(dict(response.headers)),
    }
    try:
        dumpobj["content"] = response.json()
    except JSONDecodeError:
        dumpobj["content"] = response.text
    logger.debug(f"RESPONSE: {json.dumps(dumpobj)}")
