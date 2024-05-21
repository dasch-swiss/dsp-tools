from unittest.mock import patch

import pytest
from requests import Response
from requests.exceptions import RequestException

from dsp_tools.commands.xmlupload.iiif_client import IIIFUriValidatorLive
from dsp_tools.commands.xmlupload.models.input_problems import IIIFUriProblem


@pytest.fixture()
def response_404() -> Response:
    mock_response = Response()
    mock_response.status_code = 404
    mock_response._content = b"This is the response text."
    return mock_response


@pytest.fixture()
def response_200() -> Response:
    mock_response = Response()
    mock_response.status_code = 200
    mock_response._content = b"This is the response text."
    return mock_response


@pytest.fixture()
def request_exception() -> RequestException:
    return RequestException("This is the request exception.")


@patch("dsp_tools.commands.xmlupload.iiif_client.IIIFUriValidatorLive._make_network_call")
def test_validate_with_exception(mock_network_call, request_exception: RequestException):
    mock_network_call.return_value = request_exception
    validator = IIIFUriValidatorLive(uri="http://example.com", passed_regex=True)
    result = validator.validate()
    assert isinstance(result, IIIFUriProblem)
    assert result.uri == "http://example.com"
    assert result.passed_regex
    assert not result.status_code
    assert not result.response_text
    assert isinstance(result.thrown_exception, RequestException)


@patch("dsp_tools.commands.xmlupload.iiif_client.IIIFUriValidatorLive._make_network_call")
def test_validate_with_bad_status_code(mock_network_call, response_404: Response):
    mock_network_call.return_value = response_404
    validator = IIIFUriValidatorLive(uri="http://example.com", passed_regex=False)
    result = validator.validate()
    assert isinstance(result, IIIFUriProblem)
    assert result.uri == "http://example.com"
    assert not result.passed_regex
    assert result.status_code == 404
    assert result.response_text == "This is the response text."
    assert not result.thrown_exception


@patch("dsp_tools.commands.xmlupload.iiif_client.IIIFUriValidatorLive._make_network_call")
def test_validate_with_good_status_code(mock_network_call, response_200: Response):
    mock_network_call.return_value = response_200
    validator = IIIFUriValidatorLive(uri="http://example.com", passed_regex=True)
    result = validator.validate()
    assert not result


@patch("dsp_tools.commands.xmlupload.iiif_client.IIIFUriValidatorLive._make_network_call")
def test_validate_with_failed_regex_good_status_code(mock_network_call, response_200: Response):
    mock_network_call.return_value = response_200
    validator = IIIFUriValidatorLive(uri="http://example.com", passed_regex=False)
    result = validator.validate()
    assert isinstance(result, IIIFUriProblem)
    assert result.uri == "http://example.com"
    assert not result.passed_regex
    assert result.status_code == 200
    assert result.response_text == "This is the response text."
    assert not result.thrown_exception


if __name__ == "__main__":
    pytest.main([__file__])
