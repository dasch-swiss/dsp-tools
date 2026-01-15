

import json
from dataclasses import dataclass
from http import HTTPStatus
from typing import Any
from typing import cast
from unittest.mock import patch

from dsp_tools.utils.request_utils import ResponseCodeAndText
from dsp_tools.utils.request_utils import is_server_error
from dsp_tools.utils.request_utils import log_response


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


@dataclass
class ResponseMock:
    status_code: int
    headers: dict[str, Any]
    text: str

    def json(self) -> dict[str, Any]:
        return cast(dict[str, Any], json.loads(self.text))


class TestIsServerError:
    def test_bad_request_without_matching_pattern_returns_false(self):
        response = ResponseCodeAndText(status_code=HTTPStatus.BAD_REQUEST, text="Invalid ontology definition")
        assert is_server_error(response) is False

    def test_internal_server_error_returns_true(self):
        response = ResponseCodeAndText(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, text="Server error")
        assert is_server_error(response) is True
