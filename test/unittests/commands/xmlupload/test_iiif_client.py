from unittest.mock import Mock
from unittest.mock import patch

import pytest
from requests import RequestException
from requests import Response

from dsp_tools.commands.xmlupload.iiif_client import IIIFUriValidator
from dsp_tools.commands.xmlupload.models.input_problems import IIIFUriProblem


class TestIIIFMakeInfoJsonUri:
    def test_1(self) -> None:
        test = IIIFUriValidator(
            "https://iiif.dasch.swiss/0811/1Oi7mdiLsG7-FmFgp0xz2xU.jp2/full/837,530/0/default.jp2", True
        )
        assert test._make_info_json_uri() == "https://iiif.dasch.swiss/0811/1Oi7mdiLsG7-FmFgp0xz2xU.jp2/info.json"

    def test_2(self) -> None:
        test = IIIFUriValidator(
            "https://iiif.dasch.swiss/0811/1Oi7mdiLsG7-FmFgp0xz2xU.jp2/2048,0,1298,2048/649,1024/0/default.jpg", True
        )
        assert test._make_info_json_uri() == "https://iiif.dasch.swiss/0811/1Oi7mdiLsG7-FmFgp0xz2xU.jp2/info.json"

    def test_3(self) -> None:
        test = IIIFUriValidator(
            "https://iiif.io/api/image/3.0/example/reference/1-newspaper-p2/full/max/0/default.webp", True
        )

        assert test._make_info_json_uri() == "https://iiif.io/api/image/3.0/example/reference/1-newspaper-p2/info.json"

    def test_4(self) -> None:
        test = IIIFUriValidator(
            "https://newspapers.library.wales/iiif/2.0/image/4497470/512,2048,512,512/256,/0/default.jpg", True
        )
        assert test._make_info_json_uri() == "https://newspapers.library.wales/iiif/2.0/image/4497470/info.json"

    def test_5(self) -> None:
        test = IIIFUriValidator("https://example.org/image-service/abcd1234/full/max/0/default.jpg", True)
        assert test._make_info_json_uri() == "https://example.org/image-service/abcd1234/info.json"

    def test_6(self) -> None:
        test = IIIFUriValidator("https://www.example.org/prefix1/abcd1234/80,15,60,75/full/0/native", True)
        assert test._make_info_json_uri() == "https://www.example.org/prefix1/abcd1234/info.json"

    def test_7(self) -> None:
        test = IIIFUriValidator("http://www.example.org/prefix1/abcd1234/80,15,60.6,75/full/0/native.jpg", True)
        assert test._make_info_json_uri() == "http://www.example.org/prefix1/abcd1234/info.json"


def test_make_info_json_uri_fail_1() -> None:
    test = IIIFUriValidator("bla", False)
    assert test._make_info_json_uri() == "bla/info.json"


def test_make_info_json_uri_fail_2() -> None:
    test = IIIFUriValidator("bla/", False)
    assert test._make_info_json_uri() == "bla/info.json"


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


@patch("dsp_tools.commands.xmlupload.iiif_client.IIIFUriValidator._make_network_call")
def test_validate_with_exception(mock_network_call: Mock, request_exception: RequestException) -> None:
    mock_network_call.return_value = request_exception
    validator = IIIFUriValidator(uri="http://example.com", regex_has_passed=True)
    result = validator.validate()
    assert isinstance(result, IIIFUriProblem)
    assert result.uri == "http://example.com"
    assert result.regex_has_passed
    assert not result.status_code
    assert result.original_text == "This is the request exception."
    assert result.thrown_exception_name == "RequestException"


@patch("dsp_tools.commands.xmlupload.iiif_client.IIIFUriValidator._make_network_call")
def test_validate_with_bad_status_code(mock_network_call: Mock, response_404: Response) -> None:
    mock_network_call.return_value = response_404
    validator = IIIFUriValidator(uri="http://example.com", regex_has_passed=False)
    result = validator.validate()
    assert isinstance(result, IIIFUriProblem)
    assert result.uri == "http://example.com"
    assert not result.regex_has_passed
    assert result.status_code == 404
    assert result.original_text == "This is the response text."
    assert not result.thrown_exception_name


@patch("dsp_tools.commands.xmlupload.iiif_client.IIIFUriValidator._make_network_call")
def test_validate_with_good_status_code(mock_network_call: Mock, response_200: Response) -> None:
    mock_network_call.return_value = response_200
    validator = IIIFUriValidator(uri="http://example.com", regex_has_passed=True)
    result = validator.validate()
    assert not result


@patch("dsp_tools.commands.xmlupload.iiif_client.IIIFUriValidator._make_network_call")
def test_validate_with_failed_regex_good_status_code(mock_network_call: Mock, response_200: Response) -> None:
    mock_network_call.return_value = response_200
    validator = IIIFUriValidator(uri="http://example.com", regex_has_passed=False)
    result = validator.validate()
    assert isinstance(result, IIIFUriProblem)
    assert result.uri == "http://example.com"
    assert not result.regex_has_passed
    assert result.status_code == 200
    assert result.original_text == "This is the response text."
    assert not result.thrown_exception_name


if __name__ == "__main__":
    pytest.main([__file__])
