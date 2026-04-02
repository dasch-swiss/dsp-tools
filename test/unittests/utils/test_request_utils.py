import json
from dataclasses import dataclass
from typing import Any
from typing import cast
from unittest.mock import patch

import pytest

from dsp_tools.utils.request_utils import _is_retriable_status_code
from dsp_tools.utils.request_utils import log_response


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
        (),  # TODO: add more
    ],
)
def test_is_retriable_status_code(status_code: int, expected: bool) -> None:
    result = _is_retriable_status_code(status_code)
    assert result == expected
