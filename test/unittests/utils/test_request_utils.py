import json
from typing import Any
from unittest.mock import create_autospec
from unittest.mock import patch

import pytest
from requests import Response

from dsp_tools.utils.request_utils import ResponseCodeAndText
from dsp_tools.utils.request_utils import _is_retriable_status_code
from dsp_tools.utils.request_utils import log_response
from dsp_tools.utils.request_utils import parse_api_v3_error
from dsp_tools.utils.request_utils import should_retry_request


def _make_response(status_code: int, headers: dict[str, Any], text: str):
    mock = create_autospec(Response, instance=True)
    mock.status_code = status_code
    mock.headers = headers
    mock.text = text
    try:
        mock.json.return_value = json.loads(text)
    except json.JSONDecodeError as e:
        mock.json.side_effect = e
    return mock


def test_log_response() -> None:
    response_mock = _make_response(
        200,
        {"Set-Cookie": "KnoraAuthenticationMFYGSLT", "Content-Type": "application/json"},
        json.dumps({"foo": "bar"}),
    )
    expected_output = {
        "status_code": 200,
        "headers": {"Set-Cookie": "***", "Content-Type": "application/json"},
        "content": {"foo": "bar"},
    }
    with patch("dsp_tools.utils.request_utils.logger.debug") as debug_mock:
        log_response(response_mock)
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


class TestParseApiV3Errors:
    def test_several_errors(self):
        response_json = {
            "message": "complete message",
            "errors": [
                {
                    "code": "code_1",
                    "message": "msg_1",
                    "details": {"iri": "detail_iri_1"},
                },
                {
                    "code": "code_2",
                    "message": "msg_2",
                    "details": {"iri": "detail_iri_2"},
                },
            ],
        }
        json_str = json.dumps(response_json)
        response_mocked = _make_response(404, {}, json_str)
        result = parse_api_v3_error(response_mocked)
        assert result.status_code == 404
        assert result.text == json_str
        assert result.v3_errors is not None
        assert len(result.v3_errors) == 2
        first = next(x for x in result.v3_errors if x.error_code == "code_1")
        assert first.message == "msg_1"
        assert first.details == {"iri": "detail_iri_1"}

        second = next(x for x in result.v3_errors if x.error_code == "code_2")
        assert second.message == "msg_2"
        assert second.details == {"iri": "detail_iri_2"}

    def test_no_error_code(self):
        response_json = {"message": "complete message", "errors": []}
        json_str = json.dumps(response_json)
        response_mocked = _make_response(404, {}, json_str)
        result = parse_api_v3_error(response_mocked)
        assert result.status_code == 404
        assert result.text == json_str
        assert result.v3_errors is None

    def test_not_v3_error_style(self):
        response_message = "Invalid value for: path parameter classIri"
        response_mocked = _make_response(400, {}, response_message)
        result = parse_api_v3_error(response_mocked)
        assert result.status_code == 400
        assert result.text == response_message
        assert result.v3_errors is None
