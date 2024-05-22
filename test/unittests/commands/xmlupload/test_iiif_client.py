from unittest.mock import Mock
from unittest.mock import patch

import pytest
from requests import RequestException
from requests import Response

from dsp_tools.commands.xmlupload.iiif_client import IIIFUriValidator
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


@pytest.fixture()
def empty_validator() -> IIIFUriValidator:
    return IIIFUriValidator([])


class TestIIIFMakeInfoJsonUri:
    def test_1(self, empty_validator: IIIFUriValidator) -> None:
        test_uri = "https://iiif.dasch.swiss/0811/1Oi7mdiLsG7-FmFgp0xz2xU.jp2/full/837,530/0/default.jp2"
        expected = "https://iiif.dasch.swiss/0811/1Oi7mdiLsG7-FmFgp0xz2xU.jp2/info.json"
        assert empty_validator._make_info_json_uri(test_uri) == expected

    def test_2(self, empty_validator: IIIFUriValidator) -> None:
        test_uri = "https://iiif.dasch.swiss/0811/1Oi7mdiLsG7-FmFgp0xz2xU.jp2/2048,0,1298,2048/649,1024/0/default.jpg"
        expected = "https://iiif.dasch.swiss/0811/1Oi7mdiLsG7-FmFgp0xz2xU.jp2/info.json"
        assert empty_validator._make_info_json_uri(test_uri) == expected

    def test_3(self, empty_validator: IIIFUriValidator) -> None:
        test_uri = "https://iiif.io/api/image/3.0/example/reference/1-newspaper-p2/full/max/0/default.webp"
        expected = "https://iiif.io/api/image/3.0/example/reference/1-newspaper-p2/info.json"
        assert empty_validator._make_info_json_uri(test_uri) == expected

    def test_4(self, empty_validator: IIIFUriValidator) -> None:
        test_uri = "https://newspapers.library.wales/iiif/2.0/image/4497470/512,2048,512,512/256,/0/default.jpg"
        expected = "https://newspapers.library.wales/iiif/2.0/image/4497470/info.json"
        assert empty_validator._make_info_json_uri(test_uri) == expected

    def test_5(self, empty_validator: IIIFUriValidator) -> None:
        test_uri = "https://example.org/image-service/abcd1234/full/max/0/default.jpg"
        expected = "https://example.org/image-service/abcd1234/info.json"
        assert empty_validator._make_info_json_uri(test_uri) == expected

    def test_6(self, empty_validator: IIIFUriValidator) -> None:
        test_uri = "https://www.example.org/prefix1/abcd1234/80,15,60,75/full/0/native"
        expected = "https://www.example.org/prefix1/abcd1234/info.json"
        assert empty_validator._make_info_json_uri(test_uri) == expected

    def test_7(self, empty_validator: IIIFUriValidator) -> None:
        test_uri = "http://www.example.org/prefix1/abcd1234/80,15,60.6,75/full/0/native.jpg"
        expected = "http://www.example.org/prefix1/abcd1234/info.json"
        assert empty_validator._make_info_json_uri(test_uri) == expected


def test_make_info_json_uri_fail_1(empty_validator: IIIFUriValidator) -> None:
    test_uri = "bla"
    expected = "bla/info.json"
    assert empty_validator._make_info_json_uri(test_uri) == expected


def test_make_info_json_uri_fail_2(empty_validator: IIIFUriValidator) -> None:
    test_uri = "bla/"
    expected = "bla/info.json"
    assert empty_validator._make_info_json_uri(test_uri) == expected


@patch("dsp_tools.commands.xmlupload.iiif_client.IIIFUriValidator._make_network_call")
def test_validate_with_exception(
    mock_network_call: Mock, request_exception: RequestException, empty_validator: IIIFUriValidator
) -> None:
    mock_network_call.return_value = request_exception
    result = empty_validator._validate_one_uri("http://example.com")
    assert isinstance(result, IIIFUriProblem)
    assert result.uri == "http://example.com"
    assert not result.regex_has_passed
    assert not result.status_code
    assert result.original_text == "This is the request exception."
    assert result.thrown_exception_name == "RequestException"


@patch("dsp_tools.commands.xmlupload.iiif_client.IIIFUriValidator._make_network_call")
def test_validate_with_bad_status_code(
    mock_network_call: Mock, response_404: Response, empty_validator: IIIFUriValidator
) -> None:
    mock_network_call.return_value = response_404
    result = empty_validator._validate_one_uri("http://example.com")
    assert isinstance(result, IIIFUriProblem)
    assert result.uri == "http://example.com"
    assert not result.regex_has_passed
    assert result.status_code == 404
    assert result.original_text == "This is the response text."
    assert not result.thrown_exception_name


@patch("dsp_tools.commands.xmlupload.iiif_client.IIIFUriValidator._make_network_call")
def test_validate_with_good_status_code(
    mock_network_call: Mock, response_200: Response, empty_validator: IIIFUriValidator
) -> None:
    mock_network_call.return_value = response_200
    result = empty_validator._validate_one_uri(
        "https://iiif.dasch.swiss/0811/1Oi7mdiLsG7-FmFgp0xz2xU.jp2/full/837,530/0/default.jp2"
    )
    assert not result


@patch("dsp_tools.commands.xmlupload.iiif_client.IIIFUriValidator._make_network_call")
def test_validate_with_failed_regex_good_status_code(
    mock_network_call: Mock, response_200: Response, empty_validator: IIIFUriValidator
) -> None:
    mock_network_call.return_value = response_200
    result = empty_validator._validate_one_uri("http://example.com")
    assert isinstance(result, IIIFUriProblem)
    assert result.uri == "http://example.com"
    assert not result.regex_has_passed
    assert result.status_code == 200
    assert result.original_text == "This is the response text."
    assert not result.thrown_exception_name


if __name__ == "__main__":
    pytest.main([__file__])
