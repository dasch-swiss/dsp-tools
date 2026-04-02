import json
from dataclasses import dataclass
from http import HTTPStatus
from typing import Any
from typing import cast
from unittest.mock import patch

from dsp_tools.utils.request_utils import ResponseCodeAndText
from dsp_tools.utils.request_utils import is_server_error
from dsp_tools.utils.request_utils import log_response
from dsp_tools.utils.request_utils import parse_api_v3_error
from dsp_tools.utils.request_utils import should_retry_on_status_code


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
        response_mocked = ResponseMock(404, {}, json_str)
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
        response_mocked = ResponseMock(404, {}, json_str)
        result = parse_api_v3_error(response_mocked)
        assert result.status_code == 404
        assert result.text == json_str
        assert result.v3_errors is None

    def test_not_v3_error_style(self):
        response_message = "Invalid value for: path parameter classIri"
        response_mocked = ResponseMock(400, {}, response_message)
        result = parse_api_v3_error(response_mocked)
        assert result.status_code == 400
        assert result.text == response_message
        assert result.v3_errors is None


class TestShouldRetryOnStatusCode:



    def test_500_returns_true(self):
        assert should_retry_on_status_code(500) is True

    def test_503_returns_true(self):
        assert should_retry_on_status_code(503) is True

    def test_429_returns_true(self):
        assert should_retry_on_status_code(429) is True

    def test_400_returns_false(self):
        assert should_retry_on_status_code(400) is False

    def test_404_returns_false(self):
        assert should_retry_on_status_code(404) is False
