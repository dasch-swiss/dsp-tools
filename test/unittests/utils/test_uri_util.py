import pytest

from dsp_tools.utils.uri_util import is_iiif_uri


def test_is_iiif_uri_correct() -> None:
    uris_success = [
        "https://iiif.dasch.swiss/0811/1Oi7mdiLsG7-FmFgp0xz2xU.jp2/full/837,530/0/default.jp2",
        "https://iiif.dasch.swiss/0811/1Oi7mdiLsG7-FmFgp0xz2xU.jp2/2048,0,1298,2048/649,1024/0/default.jpg",
        "https://iiif.io/api/image/3.0/example/reference/1-newspaper-p2/full/max/0/default.webp",
        "https://newspapers.library.wales/iiif/2.0/image/4497470/512,2048,512,512/256,/0/default.jpg",
        "https://example.org/image-service/abcd1234/full/max/0/default.jpg",
    ]
    for uri in uris_success:
        assert is_iiif_uri(uri), f"Assertion failed for URI: {uri}"


def test_is_iiif_uri_wrong() -> None:
    uris_success = [
        "http://example.org",
        "https://iiif.dasch.swiss/0811/1Oi7mdiLsG7-FmFgp0xz2xU.jp2/2048,0,1298,2048/649,1024/0/default.jpg3",
    ]
    for uri in uris_success:
        assert not is_iiif_uri(uri), f"Assertion failed for URI: {uri}"


if __name__ == "__main__":
    pytest.main([__file__])
