import pytest

from dsp_tools.utils.uri_util import is_iiif_uri


class TestIsIIIFUriCorrect:
    def test_1(self) -> None:
        assert is_iiif_uri("https://iiif.dasch.swiss/0811/1Oi7mdiLsG7-FmFgp0xz2xU.jp2/full/837,530/0/default.jp2")

    def test_2(self) -> None:
        assert is_iiif_uri(
            "https://iiif.dasch.swiss/0811/1Oi7mdiLsG7-FmFgp0xz2xU.jp2/2048,0,1298,2048/649,1024/0/default.jpg"
        )

    def test_3(self) -> None:
        assert is_iiif_uri("https://iiif.io/api/image/3.0/example/reference/1-newspaper-p2/full/max/0/default.webp")

    def test_4(self) -> None:
        assert is_iiif_uri(
            "https://newspapers.library.wales/iiif/2.0/image/4497470/512,2048,512,512/256,/0/default.jpg"
        )

    def test_5(self) -> None:
        assert is_iiif_uri("https://example.org/image-service/abcd1234/full/max/0/default.jpg")

    def test_6(self) -> None:
        assert is_iiif_uri("https://www.example.org/prefix1/abcd1234/80,15,60,75/full/0/native")

    def test_7(self) -> None:
        assert is_iiif_uri("http://www.example.org/prefix1/abcd1234/80,15,60.6,75/full/0/native.jpg")

    def test_8(self) -> None:
        assert is_iiif_uri("http://www.example.org/prefix1/abcd1234/pct:10.5,10,80,70/full/0/native.jpg")

    def test_9(self) -> None:
        assert is_iiif_uri("http://www.example.org/prefix1/abcd1234/full/full/0/native.jpg")

    def test_10(self) -> None:
        assert is_iiif_uri("http://www.example.org/prefix1/abcd1234/full/600,/0/colour.jpg")

    def test_11(self) -> None:
        assert is_iiif_uri("http://www.example.org/prefix1/abcd1234/full/600,/!1/color.jpg")

    def test_12(self) -> None:
        assert is_iiif_uri("http://www.example.org/prefix1/abcd1234/full/600,/0/grey.jpg")

    def test_13(self) -> None:
        assert is_iiif_uri("http://www.example.org/prefix1/abcd1234/full/600,/0/bitonal.JPG")

    def test_14(self) -> None:
        assert is_iiif_uri("http://www.example.org/prefix1/prefix2/prefix3/prefix4/abcd1234/full/full/0/default.jpg")

    def test_15(self) -> None:
        assert is_iiif_uri("https://www.example.org/prefix1/prefix2/prefix3/prefix4/abcd1234/full/full/!90/gray.webp")

    def test_16(self) -> None:
        assert is_iiif_uri("http://www.example.org/prefix1/prefix2/prefix3/prefix4/abcd1234/full/max/0/default.jpg")

    def test_17(self) -> None:
        assert is_iiif_uri("http://www.example.org/prefix1/abcd1234/80,15,60,75/full/0/native")

    def test_18(self) -> None:
        assert is_iiif_uri("https://www.example.org/prefix1/prefix2/prefix3/prefix4/abcd1234/full/%5Emax/0/gray.webp")

    def test_19(self) -> None:
        assert is_iiif_uri("https://iiif.dasch.swiss/0811/1Oi7mdiLsG7-FmFgp0xz2xU.jp2/full/max/0/default.jpg")

    def test_20(self) -> None:
        assert is_iiif_uri("http://www.example.org/prefix1/prefix2/prefix3/abcd1234/80,15,60,75/full/0/native")


class TestIsIIIFUriWrong:
    def test_1(self) -> None:
        assert not is_iiif_uri("http://example.org")

    def test_2(self) -> None:
        assert not is_iiif_uri(
            "https://iiif.dasch.swiss/0811/1Oi7mdiLsG7-FmFgp0xz2xU.jp2/2048,0,1298,2048/649,1024/0/default.jpg3"
        )

    def test_3(self) -> None:
        assert not is_iiif_uri("https://iiif.ub.unibe.ch/image/v2.1/632664f2-20cb-43e4-8584-2fa3988c63a2/info.json")

    def test_4(self) -> None:
        assert not is_iiif_uri("https://iiif.dasch.swiss/0811/5Jd909CLmCJ-BUUL1DDOXGJ.jp2/info.json")

    def test_5(self) -> None:
        assert not is_iiif_uri("ftp://www.example.org/prefix1/prefix2/prefix3/prefix4/abcd1234/kljg/%5Emax/0/gray.webp")

    def test_6(self) -> None:
        assert not is_iiif_uri("http://www.example.org/prefix1/abcd1234/80.,15,60,75/full/0/native")

    def test_7(self) -> None:
        assert not is_iiif_uri("http://www.example.org/prefix1/abcd1234/.80,15,60,75/full/0/native")

    def test_8(self) -> None:
        assert not is_iiif_uri("http://www.example.org/prefix1/abcd1234/full/0/native.jpg")


if __name__ == "__main__":
    pytest.main([__file__])
