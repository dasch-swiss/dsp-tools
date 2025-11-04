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
    @patch("dsp_tools.clients.authentication_client_live.log_response")
    @patch("dsp_tools.clients.authentication_client_live.log_request")
    def test_get_token_success(self, log_request: Mock, log_response: Mock, auth_client: AuthenticationClientLive):
        expected_token = "test-token-abc123"
        mock_response = Mock(status_code=200, ok=True)
        mock_response.json.return_value = {"token": expected_token}

        with patch("dsp_tools.clients.authentication_client_live.requests.post") as post_mock:
            post_mock.return_value = mock_response
            token = auth_client.get_token()

        assert token == expected_token
        log_request.assert_called_once()
        log_response.assert_called_once()

    def test_get_token_uses_cached_token(self, auth_client: AuthenticationClientLive):
        # Pre-set the token to simulate it being cached
        cached_token = "cached-token-xyz"
        auth_client._token = cached_token

        with patch("dsp_tools.clients.authentication_client_live.requests.post") as post_mock:
            token = auth_client.get_token()

        # Should return cached token without making API call
        assert token == cached_token
        post_mock.assert_not_called()

    @patch("dsp_tools.clients.authentication_client_live.log_response")
    @patch("dsp_tools.clients.authentication_client_live.log_request")
    def test_get_token_unauthorized(self, log_request: Mock, log_response: Mock, auth_client: AuthenticationClientLive):
        mock_response = Mock(status_code=HTTPStatus.UNAUTHORIZED.value, ok=False, text="Unauthorized")

        with patch("dsp_tools.clients.authentication_client_live.requests.post") as post_mock:
            post_mock.return_value = mock_response
            with pytest.raises(BadCredentialsError) as exc_info:
                auth_client.get_token()

        assert "test@example.com" in str(exc_info.value)
        assert "not successful" in str(exc_info.value)
        log_request.assert_called_once()
        log_response.assert_called_once()

    @patch("dsp_tools.clients.authentication_client_live.log_response")
    @patch("dsp_tools.clients.authentication_client_live.log_request")
    def test_get_token_server_error(self, log_request: Mock, log_response: Mock, auth_client: AuthenticationClientLive):
        mock_response = Mock(status_code=500, ok=False, text="Internal Server Error")

        with patch("dsp_tools.clients.authentication_client_live.requests.post") as post_mock:
            post_mock.return_value = mock_response
            with pytest.raises(FatalNonOkApiResponseCode) as exc_info:
                auth_client.get_token()

        assert "500" in str(exc_info.value)
        log_request.assert_called_once()
        log_response.assert_called_once()

    @patch("dsp_tools.clients.authentication_client_live.log_request")
    @patch("dsp_tools.clients.authentication_client_live.log_and_raise_request_exception")
    def test_get_token_request_exception(
        self, log_and_raise_mock: Mock, log_request: Mock, auth_client: AuthenticationClientLive
    ):
        request_error = RequestException("Connection timeout")
        log_and_raise_mock.side_effect = request_error

        with patch("dsp_tools.clients.authentication_client_live.requests.post") as post_mock:
            post_mock.side_effect = request_error
            with pytest.raises(RequestException):
                auth_client.get_token()

        log_request.assert_called_once()
        log_and_raise_mock.assert_called_once()

    @patch("dsp_tools.clients.authentication_client_live.log_response")
    @patch("dsp_tools.clients.authentication_client_live.log_request")
    def test_get_token_logs_request_parameters(
        self, log_request: Mock, log_response: Mock, auth_client: AuthenticationClientLive
    ):
        mock_response = Mock(status_code=200, ok=True)
        mock_response.json.return_value = {"token": "test-token"}

        with patch("dsp_tools.clients.authentication_client_live.requests.post") as post_mock:
            post_mock.return_value = mock_response
            auth_client.get_token()

        log_request_call = log_request.call_args_list[0].args[0]
        assert log_request_call.method == "POST"
        assert log_request_call.url == "http://api.com/v2/authentication"
        assert log_request_call.timeout == 10
        assert "User-Agent" in log_request_call.headers

    @patch("dsp_tools.clients.authentication_client_live.log_response")
    @patch("dsp_tools.clients.authentication_client_live.log_request")
    def test_get_token_makes_post_request_with_correct_parameters(
        self, log_request: Mock, log_response: Mock, auth_client: AuthenticationClientLive
    ):
        mock_response = Mock(status_code=200, ok=True)
        mock_response.json.return_value = {"token": "test-token"}

        with patch("dsp_tools.clients.authentication_client_live.requests.post") as post_mock:
            post_mock.return_value = mock_response
            auth_client.get_token()

        # Check the call was made with correct arguments (url is positional, rest are kwargs)
        post_call_args = post_mock.call_args_list[0][0]
        post_call_kwargs = post_mock.call_args_list[0][1]
        assert post_call_args[0] == "http://api.com/v2/authentication"
        assert post_call_kwargs["json"] == {"email": "test@example.com", "password": "password123"}
        assert post_call_kwargs["timeout"] == 10
        assert "User-Agent" in post_call_kwargs["headers"]
