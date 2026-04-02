import json
from dataclasses import dataclass
from typing import Any
from typing import cast
from unittest.mock import patch

import pytest

from dsp_tools.utils.request_utils import ResponseCodeAndText
from dsp_tools.utils.request_utils import _is_retriable_status_code
from dsp_tools.utils.request_utils import log_response
from dsp_tools.utils.request_utils import should_retry_request


@dataclass
class ResponseMock:
    status_code: int
    headers: dict[str, Any]
    text: str

    def json(self) -> dict[str, Any]:
        return cast(dict[str, Any], json.loads(self.text))


def test_log_response() -> None:
    response_mock = ResponseMock(
        status_code=200,
        headers={"Set-Cookie": "KnoraAuthenticationMFYGSLT", "Content-Type": "application/json"},
        text=json.dumps({"foo": "bar"}),
    )
    expected_output = {
        "status_code": 200,
        "headers": {"Set-Cookie": "***", "Content-Type": "application/json"},
        "content": {"foo": "bar"},
    }
    with patch("dsp_tools.utils.request_utils.logger.debug") as debug_mock:
        log_response(response_mock)  # type: ignore[arg-type]
        debug_mock.assert_called_once_with(f"RESPONSE: {json.dumps(expected_output)}")


@pytest.mark.parametrize(
    ("status_code", "expected"),
    [
        (500, True),
        (503, True),
        (511, True),
        (429, True),
        (200, False),
        (404, False),
        (400, False),
    ],
)
def test_is_retriable_status_code(status_code: int, expected: bool) -> None:
    result = _is_retriable_status_code(status_code)
    assert result == expected


@pytest.mark.parametrize(
    ("env_value", "response", "expected"),
    [
        (None, ResponseCodeAndText(500, ""), True),
        ("false", ResponseCodeAndText(500, ""), True),
        ("true", ResponseCodeAndText(500, ""), False),
        (None, ResponseCodeAndText(200, "try again later"), True),
        ("true", ResponseCodeAndText(200, "try again later"), False),
        (None, ResponseCodeAndText(200, ""), False),
        ("false", ResponseCodeAndText(429, "try again later"), True),
        ("true", ResponseCodeAndText(429, "try again later"), False),
    ],
)
def test_should_retry_request(
    monkeypatch: pytest.MonkeyPatch,
    env_value: str | None,
    response: ResponseCodeAndText,
    expected: bool,
) -> None:
    if env_value is None:
        monkeypatch.delenv("DSP_TOOLS_TESTING", raising=False)
    else:
        monkeypatch.setenv("DSP_TOOLS_TESTING", env_value)
    assert should_retry_request(response) == expected
