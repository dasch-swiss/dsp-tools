# mypy: disable-error-code="method-assign,no-untyped-def"

from http import HTTPStatus
from unittest.mock import Mock
from unittest.mock import patch

import pytest
from requests import JSONDecodeError
from requests import RequestException

from dsp_tools.clients.authentication_client_live import AuthenticationClientLive
from dsp_tools.error.exceptions import BadCredentialsError
from dsp_tools.error.exceptions import DspToolsRequestException
from dsp_tools.error.exceptions import FatalNonOkApiResponseCode


@pytest.fixture
def auth_client() -> AuthenticationClientLive:
    return AuthenticationClientLive(
        server="http://api.com",
        email="test@example.com",
        password="password123",
    )


def test_get_token_success(auth_client: AuthenticationClientLive):
    expected_token = "test-token-abc123"
    mock_response = Mock(status_code=200, ok=True, headers={})
    mock_response.json.return_value = {"token": expected_token}

    with patch("dsp_tools.clients.authentication_client_live.requests.post", return_value=mock_response):
        token = auth_client.get_token()

    assert token == expected_token


def test_get_token_uses_cached_token(auth_client: AuthenticationClientLive):
    cached_token = "cached-token-xyz"
    auth_client._token = cached_token

    with patch("dsp_tools.clients.authentication_client_live.requests.post") as post_mock:
        token = auth_client.get_token()

    assert token == cached_token
    post_mock.assert_not_called()


def test_get_token_error_responses(auth_client: AuthenticationClientLive):
    mock_response = Mock(status_code=HTTPStatus.BAD_REQUEST.value, ok=False, text="Error", headers={})
    mock_response.json.side_effect = JSONDecodeError("Expecting value", "", 0)
    with patch("dsp_tools.clients.authentication_client_live.requests.post", return_value=mock_response):
        with pytest.raises(FatalNonOkApiResponseCode):
            auth_client.get_token()


def test_get_token_unauthorised_exception(auth_client: AuthenticationClientLive):
    mock_response = Mock(status_code=HTTPStatus.UNAUTHORIZED.value, ok=False, text="Error", headers={})
    mock_response.json.side_effect = JSONDecodeError("Expecting value", "", 0)
    with patch("dsp_tools.clients.authentication_client_live.requests.post", return_value=mock_response):
        with pytest.raises(BadCredentialsError):
            auth_client.get_token()


def test_get_token_request_exception(auth_client: AuthenticationClientLive):
    request_error = RequestException("Connection timeout")
    with patch("dsp_tools.clients.authentication_client_live.requests.post", side_effect=request_error):
        with pytest.raises(DspToolsRequestException):
            auth_client.get_token()
