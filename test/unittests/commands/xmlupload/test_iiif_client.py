from dsp_tools.commands.xmlupload.iiif_client import IIIFUriValidatorLive


class TestIIIFMakeInfoJsonUri:
    def test_1(self) -> None:
        test = IIIFUriValidatorLive(
            "https://iiif.dasch.swiss/0811/1Oi7mdiLsG7-FmFgp0xz2xU.jp2/full/837,530/0/default.jp2", True
        )
        assert test._make_info_json_uri() == "https://iiif.dasch.swiss/0811/1Oi7mdiLsG7-FmFgp0xz2xU.jp2/info.json"

    def test_2(self) -> None:
        test = IIIFUriValidatorLive(
            "https://iiif.dasch.swiss/0811/1Oi7mdiLsG7-FmFgp0xz2xU.jp2/2048,0,1298,2048/649,1024/0/default.jpg", True
        )
        assert test._make_info_json_uri() == "https://iiif.dasch.swiss/0811/1Oi7mdiLsG7-FmFgp0xz2xU.jp2/info.json"

    def test_3(self) -> None:
        test = IIIFUriValidatorLive(
            "https://iiif.io/api/image/3.0/example/reference/1-newspaper-p2/full/max/0/default.webp", True
        )

        assert test._make_info_json_uri() == "https://iiif.io/api/image/3.0/example/reference/1-newspaper-p2/info.json"

    def test_4(self) -> None:
        test = IIIFUriValidatorLive(
            "https://newspapers.library.wales/iiif/2.0/image/4497470/512,2048,512,512/256,/0/default.jpg", True
        )
        assert test._make_info_json_uri() == "https://newspapers.library.wales/iiif/2.0/image/4497470/info.json"

    def test_5(self) -> None:
        test = IIIFUriValidatorLive("https://example.org/image-service/abcd1234/full/max/0/default.jpg", True)
        assert test._make_info_json_uri() == "https://example.org/image-service/abcd1234/info.json"

    def test_6(self) -> None:
        test = IIIFUriValidatorLive("https://www.example.org/prefix1/abcd1234/80,15,60,75/full/0/native", True)
        assert test._make_info_json_uri() == "https://www.example.org/prefix1/abcd1234/info.json"

    def test_7(self) -> None:
        test = IIIFUriValidatorLive("http://www.example.org/prefix1/abcd1234/80,15,60.6,75/full/0/native.jpg", True)
        assert test._make_info_json_uri() == "http://www.example.org/prefix1/abcd1234/info.json"


def test_make_info_json_uri_fail_1() -> None:
    test = IIIFUriValidatorLive("bla", False)
    assert test._make_info_json_uri() == "bla/info.json"


def test_make_info_json_uri_fail_2() -> None:
    test = IIIFUriValidatorLive("bla/", False)
    assert test._make_info_json_uri() == "bla/info.json"
