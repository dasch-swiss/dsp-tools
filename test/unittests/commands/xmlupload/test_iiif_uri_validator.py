from unittest.mock import Mock
from unittest.mock import patch

import pytest
from requests import RequestException
from requests import Response

from dsp_tools.commands.xmlupload.iiif_uri_validator import IIIFUriValidator
from dsp_tools.commands.xmlupload.models.input_problems import IIIFUriProblem


@pytest.fixture
def response_404() -> Response:
    mock_response = Response()
    mock_response.status_code = 404
    mock_response._content = b"This is the response text."
    return mock_response


@pytest.fixture
def response_200() -> Response:
    mock_response = Response()
    mock_response.status_code = 200
    mock_response._content = b"This is the response text."
    return mock_response


@pytest.fixture
def request_exception() -> RequestException:
    return RequestException("This is the request exception.")


@pytest.fixture
def empty_validator() -> IIIFUriValidator:
    return IIIFUriValidator([])


@pytest.mark.parametrize(
    ("uri", "expected"),
    [
        (
            "https://iiif.dasch.swiss/0811/1Oi7mdiLsG7-FmFgp0xz2xU.jp2/full/837,530/0/default.jp2",
            "https://iiif.dasch.swiss/0811/1Oi7mdiLsG7-FmFgp0xz2xU.jp2/info.json",
        ),
        (
            "https://iiif.dasch.swiss/0811/1Oi7mdiLsG7-FmFgp0xz2xU.jp2/2048,0,1298,2048/649,1024/0/default.jpg",
            "https://iiif.dasch.swiss/0811/1Oi7mdiLsG7-FmFgp0xz2xU.jp2/info.json",
        ),
        (
            "https://iiif.io/api/image/3.0/example/reference/1-newspaper-p2/full/max/0/default.webp",
            "https://iiif.io/api/image/3.0/example/reference/1-newspaper-p2/info.json",
        ),
        (
            "https://newspapers.library.wales/iiif/2.0/image/4497470/512,2048,512,512/256,/0/default.jpg",
            "https://newspapers.library.wales/iiif/2.0/image/4497470/info.json",
        ),
        (
            "https://example.org/image-service/abcd1234/full/max/0/default.jpg",
            "https://example.org/image-service/abcd1234/info.json",
        ),
        (
            "https://www.example.org/prefix1/abcd1234/80,15,60,75/full/0/native",
            "https://www.example.org/prefix1/abcd1234/info.json",
        ),
        (
            "http://www.example.org/prefix1/abcd1234/80,15,60.6,75/full/0/native.jpg",
            "http://www.example.org/prefix1/abcd1234/info.json",
        ),
        ("bla", "bla/info.json"),
        ("bla/", "bla/info.json"),
    ],
)
def test_make_info_json_uri_correct(empty_validator: IIIFUriValidator, uri: str, expected: str) -> None:
    assert empty_validator._make_info_json_uri(uri) == expected


@patch("dsp_tools.commands.xmlupload.iiif_uri_validator.IIIFUriValidator._make_network_call")
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
    assert result.raised_exception_name == "RequestException"


@patch("dsp_tools.commands.xmlupload.iiif_uri_validator.IIIFUriValidator._make_network_call")
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
    assert not result.raised_exception_name


@patch("dsp_tools.commands.xmlupload.iiif_uri_validator.IIIFUriValidator._make_network_call")
def test_validate_with_good_status_code(
    mock_network_call: Mock, response_200: Response, empty_validator: IIIFUriValidator
) -> None:
    mock_network_call.return_value = response_200
    result = empty_validator._validate_one_uri(
        "https://iiif.dasch.swiss/0811/1Oi7mdiLsG7-FmFgp0xz2xU.jp2/full/837,530/0/default.jp2"
    )
    assert not result


@patch("dsp_tools.commands.xmlupload.iiif_uri_validator.IIIFUriValidator._make_network_call")
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
    assert not result.raised_exception_name


if __name__ == "__main__":
    pytest.main([__file__])
