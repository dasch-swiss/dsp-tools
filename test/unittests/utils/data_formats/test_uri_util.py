import pytest

from dsp_tools.utils.data_formats.uri_util import is_iiif_uri


@pytest.mark.parametrize(
    "uri",
    [
        "https://iiif.dasch.swiss/0811/1Oi7mdiLsG7-FmFgp0xz2xU.jp2/full/837,530/0/default.jp2",
        "https://iiif.dasch.swiss/0811/1Oi7mdiLsG7-FmFgp0xz2xU.jp2/2048,0,1298,2048/649,1024/0/default.jpg",
        "https://iiif.io/api/image/3.0/example/reference/1-newspaper-p2/full/max/0/default.webp",
        "https://newspapers.library.wales/iiif/2.0/image/4497470/512,2048,512,512/256,/0/default.jpg",
        "https://example.org/image-service/abcd1234/full/max/0/default.jpg",
        "https://www.example.org/prefix1/abcd1234/80,15,60,75/full/0/native",
        "http://www.example.org/prefix1/abcd1234/80,15,60.6,75/full/0/native.jpg",
        "http://www.example.org/prefix1/abcd1234/pct:10.5,10,80,70/full/0/native.jpg",
        "http://www.example.org/prefix1/abcd1234/full/full/0/native.jpg",
        "http://www.example.org/prefix1/abcd1234/full/600,/0/colour.jpg",
        "http://www.example.org/prefix1/abcd1234/full/600,/!1/color.jpg",
        "http://www.example.org/prefix1/abcd1234/full/600,/0/grey.jpg",
        "http://www.example.org/prefix1/abcd1234/full/600,/0/bitonal.JPG",
        "http://www.example.org/prefix1/prefix2/prefix3/prefix4/abcd1234/full/full/0/default.jpg",
        "https://www.example.org/prefix1/prefix2/prefix3/prefix4/abcd1234/full/full/!90/gray.webp",
        "http://www.example.org/prefix1/prefix2/prefix3/prefix4/abcd1234/full/max/0/default.jpg",
        "http://www.example.org/prefix1/abcd1234/80,15,60,75/full/0/native",
        "https://www.example.org/prefix1/prefix2/prefix3/prefix4/abcd1234/full/%5Emax/0/gray.webp",
        "https://iiif.dasch.swiss/0811/1Oi7mdiLsG7-FmFgp0xz2xU.jp2/full/max/0/default.jpg",
        "http://www.example.org/prefix1/prefix2/prefix3/abcd1234/80,15,60,75/full/0/native",
        "https://iiif.wellcomecollection.org/image/b20432033_B0008608.JP2/full/1338%2C/0/default.jpg",
    ],
)
def test_is_iiif_uri_correct(uri: str) -> None:
    assert is_iiif_uri(uri)


@pytest.mark.parametrize(
    "uri",
    [
        "http://example.org",
        "https://iiif.dasch.swiss/0811/1Oi7mdiLsG7-FmFgp0xz2xU.jp2/2048,0,1298,2048/649,1024/0/default.jpg3",
        "https://iiif.ub.unibe.ch/image/v2.1/632664f2-20cb-43e4-8584-2fa3988c63a2/info.json",
        "https://iiif.dasch.swiss/0811/5Jd909CLmCJ-BUUL1DDOXGJ.jp2/info.json",
        "ftp://www.example.org/prefix1/prefix2/prefix3/prefix4/abcd1234/kljg/%5Emax/0/gray.webp",
        "http://www.example.org/prefix1/abcd1234/80.,15,60,75/full/0/native",
        "http://www.example.org/prefix1/abcd1234/.80,15,60,75/full/0/native",
        "http://www.example.org/prefix1/abcd1234/full/0/native.jpg",
        "http://www.example.org/prefix1/abcd1234/square/-----full/!90/gray.webp",
        "http://www.example.org/prefix1/abcd1234/square/---full/!90/gray.webp",
        "http://www.example.org/prefix1/abcd1234/square/full/---!90/gray.webp",
        "http://www.example.org/prefix1/abcd1234/square/full/!90/---gray.webp",
        "http://www.example.org/prefix1/abcd1234/-----square/full/!90/gray.webp",
    ],
)
def test_is_iiif_uri_wrong(uri: str) -> None:
    assert not is_iiif_uri(uri)


if __name__ == "__main__":
    pytest.main([__file__])
