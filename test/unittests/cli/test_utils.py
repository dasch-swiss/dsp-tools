from unittest.mock import Mock
from unittest.mock import patch

import pytest
import regex
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
    mock_get.return_value = mock_response

    expected_msg = regex.escape(
        "The DSP-API could not be reached. Please check if your stack is healthy "
        "or start a stack with 'dsp-tools start-stack' if none is running."
    )
    with pytest.raises(DspApiNotReachableError, match=expected_msg):
        _check_api_health("http://0.0.0.0:3333")
    mock_get.assert_called_once_with("http://0.0.0.0:3333/health", timeout=2)


@patch("requests.get")
def test_check_api_health_not_healthy_server(mock_get: Mock) -> None:
    mock_response = Mock()
    mock_response.ok = False
    mock_response.status_code = 503
    mock_get.return_value = mock_response

    expected_msg = regex.escape(
        "The DSP-API could not be reached (returned status 503). Please contact the DaSCH engineering team for help."
    )
    with pytest.raises(DspApiNotReachableError, match=expected_msg):
        _check_api_health("https://api.dasch.swiss")
    mock_get.assert_called_once_with("https://api.dasch.swiss/health", timeout=2)


@patch("requests.get")
def test_check_api_health_connection_error(mock_get: Mock) -> None:
    mock_get.side_effect = requests.exceptions.ConnectionError("Connection refused")

    expected_msg = regex.escape(
        "The DSP-API could not be reached. Please check if your stack is healthy "
        "or start a stack with 'dsp-tools start-stack' if none is running."
    )
    with pytest.raises(DspApiNotReachableError, match=expected_msg):
        _check_api_health("http://0.0.0.0:3333")

    mock_get.assert_called_once_with("http://0.0.0.0:3333/health", timeout=2)


@patch("requests.get")
def test_check_api_health_timeout(mock_get: Mock) -> None:
    mock_get.side_effect = requests.exceptions.Timeout("Request timed out")

    expected_msg = regex.escape(
        "The DSP-API could not be reached. Please check if your stack is healthy "
        "or start a stack with 'dsp-tools start-stack' if none is running."
    )
    with pytest.raises(DspApiNotReachableError, match=expected_msg):
        _check_api_health("http://0.0.0.0:3333")

    mock_get.assert_called_once_with("http://0.0.0.0:3333/health", timeout=2)


if __name__ == "__main__":
    pytest.main([__file__])
