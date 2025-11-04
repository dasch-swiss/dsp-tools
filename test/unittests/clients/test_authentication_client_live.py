# mypy: disable-error-code="method-assign,no-untyped-def"
from http import HTTPStatus
from unittest.mock import Mock
from unittest.mock import patch

import pytest
from requests import RequestException

from dsp_tools.clients.authentication_client_live import AuthenticationClientLive
from dsp_tools.error.exceptions import BadCredentialsError
from dsp_tools.error.exceptions import FatalNonOkApiResponseCode


@pytest.fixture
def auth_client() -> AuthenticationClientLive:
    return AuthenticationClientLive(
        server="http://api.com",
        email="test@example.com",
        password="password123",
    )


class TestGetToken:
    def test_get_token_success(self, auth_client: AuthenticationClientLive):
        expected_token = "test-token-abc123"
        mock_response = Mock(status_code=200, ok=True, headers={})
        mock_response.json.return_value = {"token": expected_token}

        with patch("dsp_tools.clients.authentication_client_live.requests.post", return_value=mock_response):
            token = auth_client.get_token()

        assert token == expected_token

    def test_get_token_uses_cached_token(self, auth_client: AuthenticationClientLive):
        cached_token = "cached-token-xyz"
        auth_client._token = cached_token

        with patch("dsp_tools.clients.authentication_client_live.requests.post") as post_mock:
            token = auth_client.get_token()

        assert token == cached_token
        post_mock.assert_not_called()

    @pytest.mark.parametrize(
        ("status_code", "exception_type", "expected_msg"),
        [
            (HTTPStatus.UNAUTHORIZED.value, BadCredentialsError, "test@example.com"),
            (500, FatalNonOkApiResponseCode, "500"),
            (404, FatalNonOkApiResponseCode, "404"),
        ],
    )
    def test_get_token_error_responses(
        self, auth_client: AuthenticationClientLive, status_code: int, exception_type: type, expected_msg: str
    ):
        from requests import JSONDecodeError

        mock_response = Mock(status_code=status_code, ok=False, text="Error", headers={})
        mock_response.json.side_effect = JSONDecodeError("", "", 0)

        with patch("dsp_tools.clients.authentication_client_live.requests.post", return_value=mock_response):
            with pytest.raises(exception_type) as exc_info:
                auth_client.get_token()

        assert expected_msg in str(exc_info.value)

    @patch("dsp_tools.clients.authentication_client_live.log_and_raise_request_exception")
    def test_get_token_request_exception(self, log_and_raise_mock: Mock, auth_client: AuthenticationClientLive):
        request_error = RequestException("Connection timeout")
        log_and_raise_mock.side_effect = request_error

        with patch("dsp_tools.clients.authentication_client_live.requests.post", side_effect=request_error):
            with pytest.raises(RequestException):
                auth_client.get_token()
