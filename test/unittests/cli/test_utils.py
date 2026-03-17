from unittest.mock import Mock
from unittest.mock import patch

import pytest
import requests

from dsp_tools.cli.exceptions import DspApiNotReachableError
from dsp_tools.cli.utils import _check_api_health


@patch("requests.get")
def test_check_api_health_success(mock_get: Mock) -> None:
    mock_response = Mock()
    mock_response.ok = True
    mock_get.return_value = mock_response

    # Should not raise any exception
    _check_api_health("http://0.0.0.0:3333")
    mock_get.assert_called_once_with("http://0.0.0.0:3333/health", timeout=2)


@patch("requests.get")
def test_check_api_health_not_healthy_local(mock_get: Mock) -> None:
    mock_response = Mock()
    mock_response.ok = False
    mock_response.status_code = 503
    mock_response.text = "Service temporarily unavailable"
    mock_get.return_value = mock_response

    with pytest.raises(DspApiNotReachableError) as exc_info:
        _check_api_health("http://0.0.0.0:3333")

    assert exc_info.value.is_localhost is True
    assert exc_info.value.status_code == 503
    assert exc_info.value.response_text == "Service temporarily unavailable"
    mock_get.assert_called_once_with("http://0.0.0.0:3333/health", timeout=2)


@patch("requests.get")
def test_check_api_health_not_healthy_server(mock_get: Mock) -> None:
    mock_response = Mock()
    mock_response.ok = False
    mock_response.status_code = 400
    mock_response.text = "Bad Request"
    mock_get.return_value = mock_response

    with pytest.raises(DspApiNotReachableError) as exc_info:
        _check_api_health("https://api.dasch.swiss")

    assert exc_info.value.is_localhost is False
    assert exc_info.value.status_code == 400
    assert exc_info.value.response_text == "Bad Request"
    mock_get.assert_called_once_with("https://api.dasch.swiss/health", timeout=2)


@patch("requests.get")
def test_check_api_health_connection_error(mock_get: Mock) -> None:
    mock_get.side_effect = requests.exceptions.ConnectionError("Connection refused")

    with pytest.raises(DspApiNotReachableError) as exc_info:
        _check_api_health("http://0.0.0.0:3333")

    assert exc_info.value.is_localhost is True
    assert exc_info.value.status_code is None
    assert exc_info.value.response_text is None
    mock_get.assert_called_once_with("http://0.0.0.0:3333/health", timeout=2)


@patch("requests.get")
def test_check_api_health_timeout(mock_get: Mock) -> None:
    mock_get.side_effect = requests.exceptions.Timeout("Request timed out")

    with pytest.raises(DspApiNotReachableError) as exc_info:
        _check_api_health("http://0.0.0.0:3333")

    assert exc_info.value.is_localhost is True
    assert exc_info.value.status_code is None
    assert exc_info.value.response_text is None
    mock_get.assert_called_once_with("http://0.0.0.0:3333/health", timeout=2)


if __name__ == "__main__":
    pytest.main([__file__])
