# ruff: noqa: ARG002
import json
from http import HTTPStatus
from typing import Any
from unittest.mock import Mock
from unittest.mock import patch

import pytest
from requests import ReadTimeout
from requests import RequestException

from dsp_tools.clients.value_client_live import ValueClientLive
from dsp_tools.error.exceptions import BadCredentialsError
from dsp_tools.utils.exceptions import DspToolsRequestException
from dsp_tools.utils.request_utils import ResponseCodeAndText

AUTH = Mock()
AUTH.get_token = Mock(return_value="tkn")

VALUE_JSON: dict[str, Any] = {"@type": "knora-api:TextValue", "@id": "http://rdfh.ch/value/1"}


@pytest.fixture
def client() -> ValueClientLive:
    return ValueClientLive("http://api.com", AUTH)


class TestPostNewValue:
    @patch("dsp_tools.clients.value_client_live.log_response")
    @patch("dsp_tools.clients.value_client_live.log_request")
    def test_ok_returns_none(self, log_req: Mock, log_resp: Mock, client: ValueClientLive) -> None:
        mock_response = Mock(status_code=HTTPStatus.OK)
        with patch("dsp_tools.clients.value_client_live.requests.post", return_value=mock_response) as mock_post:
            result = client.post_new_value(VALUE_JSON)
        assert mock_post.call_args.kwargs["url"] == f"{client.server}/v2/values"
        assert json.loads(mock_post.call_args.kwargs["data"]) == VALUE_JSON
        assert result is None

    @patch("dsp_tools.clients.value_client_live.log_response")
    @patch("dsp_tools.clients.value_client_live.log_request")
    def test_unauthorized_raises_bad_credentials(self, log_req: Mock, log_resp: Mock, client: ValueClientLive) -> None:
        mock_response = Mock(status_code=HTTPStatus.UNAUTHORIZED)
        with patch("dsp_tools.clients.value_client_live.requests.post", return_value=mock_response):
            with pytest.raises(BadCredentialsError):
                client.post_new_value(VALUE_JSON)

    @patch("dsp_tools.clients.value_client_live.log_response")
    @patch("dsp_tools.clients.value_client_live.log_request")
    def test_forbidden_raises_bad_credentials(self, log_req: Mock, log_resp: Mock, client: ValueClientLive) -> None:
        mock_response = Mock(status_code=HTTPStatus.FORBIDDEN)
        with patch("dsp_tools.clients.value_client_live.requests.post", return_value=mock_response):
            with pytest.raises(BadCredentialsError):
                client.post_new_value(VALUE_JSON)

    @patch("dsp_tools.clients.value_client_live.log_response")
    @patch("dsp_tools.clients.value_client_live.log_request")
    def test_non_ok_returns_response_code_and_text(
        self, log_req: Mock, log_resp: Mock, client: ValueClientLive
    ) -> None:
        mock_response = Mock(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, text="Internal Server Error")
        with patch("dsp_tools.clients.value_client_live.requests.post", return_value=mock_response):
            result = client.post_new_value(VALUE_JSON)
        assert isinstance(result, ResponseCodeAndText)
        assert result.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
        assert result.text == "Internal Server Error"

    @patch("dsp_tools.clients.value_client_live.log_request")
    def test_read_timeout_is_reraised(self, log_req: Mock, client: ValueClientLive) -> None:
        with patch("dsp_tools.clients.value_client_live.requests.post", side_effect=ReadTimeout()):
            with pytest.raises(ReadTimeout):
                client.post_new_value(VALUE_JSON)

    @patch("dsp_tools.clients.value_client_live.log_request")
    def test_request_exception_raises_dsp_tools_exception(self, log_req: Mock, client: ValueClientLive) -> None:
        with patch(
            "dsp_tools.clients.value_client_live.requests.post", side_effect=RequestException("Connection refused")
        ):
            with pytest.raises(DspToolsRequestException):
                client.post_new_value(VALUE_JSON)


class TestReplaceExistingValue:
    @patch("dsp_tools.clients.value_client_live.log_response")
    @patch("dsp_tools.clients.value_client_live.log_request")
    def test_ok_returns_none(self, log_req: Mock, log_resp: Mock, client: ValueClientLive) -> None:
        mock_response = Mock(status_code=HTTPStatus.OK)
        with patch("dsp_tools.clients.value_client_live.requests.put", return_value=mock_response) as mock_put:
            result = client.replace_existing_value(VALUE_JSON)
        assert mock_put.call_args.kwargs["url"] == f"{client.server}/v2/values"
        assert json.loads(mock_put.call_args.kwargs["data"]) == VALUE_JSON
        assert result is None

    @patch("dsp_tools.clients.value_client_live.log_response")
    @patch("dsp_tools.clients.value_client_live.log_request")
    def test_unauthorized_raises_bad_credentials(self, log_req: Mock, log_resp: Mock, client: ValueClientLive) -> None:
        mock_response = Mock(status_code=HTTPStatus.UNAUTHORIZED)
        with patch("dsp_tools.clients.value_client_live.requests.put", return_value=mock_response):
            with pytest.raises(BadCredentialsError):
                client.replace_existing_value(VALUE_JSON)

    @patch("dsp_tools.clients.value_client_live.log_response")
    @patch("dsp_tools.clients.value_client_live.log_request")
    def test_forbidden_raises_bad_credentials(self, log_req: Mock, log_resp: Mock, client: ValueClientLive) -> None:
        mock_response = Mock(status_code=HTTPStatus.FORBIDDEN)
        with patch("dsp_tools.clients.value_client_live.requests.put", return_value=mock_response):
            with pytest.raises(BadCredentialsError):
                client.replace_existing_value(VALUE_JSON)

    @patch("dsp_tools.clients.value_client_live.log_response")
    @patch("dsp_tools.clients.value_client_live.log_request")
    def test_non_ok_returns_response_code_and_text(
        self, log_req: Mock, log_resp: Mock, client: ValueClientLive
    ) -> None:
        mock_response = Mock(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, text="Internal Server Error")
        with patch("dsp_tools.clients.value_client_live.requests.put", return_value=mock_response):
            result = client.replace_existing_value(VALUE_JSON)
        assert isinstance(result, ResponseCodeAndText)
        assert result.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
        assert result.text == "Internal Server Error"

    @patch("dsp_tools.clients.value_client_live.log_request")
    def test_read_timeout_is_reraised(self, log_req: Mock, client: ValueClientLive) -> None:
        with patch("dsp_tools.clients.value_client_live.requests.put", side_effect=ReadTimeout()):
            with pytest.raises(ReadTimeout):
                client.replace_existing_value(VALUE_JSON)

    @patch("dsp_tools.clients.value_client_live.log_request")
    def test_request_exception_raises_dsp_tools_exception(self, log_req: Mock, client: ValueClientLive) -> None:
        with patch(
            "dsp_tools.clients.value_client_live.requests.put", side_effect=RequestException("Connection refused")
        ):
            with pytest.raises(DspToolsRequestException):
                client.replace_existing_value(VALUE_JSON)
