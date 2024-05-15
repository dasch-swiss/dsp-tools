import pytest

from dsp_tools.commands.xmlupload.models.deserialise.xmlresource import BitstreamInfo
from dsp_tools.commands.xmlupload.models.permission import Permissions
from dsp_tools.commands.xmlupload.models.permission import PermissionValue
from dsp_tools.commands.xmlupload.resource_create_client import _make_bitstream_file_value
from dsp_tools.commands.xmlupload.resource_create_client import _to_boolean
from dsp_tools.models.exceptions import BaseError


class TestMakeBitstreamFileValue:
    """Tests the _make_bitstream_file_value function."""

    def test_zip(self) -> None:
        info = BitstreamInfo("a/b/test.zip", "00001.zip")
        value = _make_bitstream_file_value(info)
        expected = {
            "knora-api:hasArchiveFileValue": {
                "@type": "knora-api:ArchiveFileValue",
                "knora-api:fileValueHasFilename": "00001.zip",
            }
        }
        assert value == expected

    def test_tar(self) -> None:
        info = BitstreamInfo("a/b/test.tar", "00001.tar")
        value = _make_bitstream_file_value(info)
        expected = {
            "knora-api:hasArchiveFileValue": {
                "@type": "knora-api:ArchiveFileValue",
                "knora-api:fileValueHasFilename": "00001.tar",
            }
        }
        assert value == expected

    def test_gz(self) -> None:
        info = BitstreamInfo("a/b/test.gz", "00001.gz")
        value = _make_bitstream_file_value(info)
        expected = {
            "knora-api:hasArchiveFileValue": {
                "@type": "knora-api:ArchiveFileValue",
                "knora-api:fileValueHasFilename": "00001.gz",
            }
        }
        assert value == expected

    def test_z(self) -> None:
        info = BitstreamInfo("a/b/test.z", "00001.z")
        value = _make_bitstream_file_value(info)
        expected = {
            "knora-api:hasArchiveFileValue": {
                "@type": "knora-api:ArchiveFileValue",
                "knora-api:fileValueHasFilename": "00001.z",
            }
        }
        assert value == expected

    def test_tar_gz(self) -> None:
        info = BitstreamInfo("a/b/test.tar.gz", "00001.tar.gz")
        value = _make_bitstream_file_value(info)
        expected = {
            "knora-api:hasArchiveFileValue": {
                "@type": "knora-api:ArchiveFileValue",
                "knora-api:fileValueHasFilename": "00001.tar.gz",
            }
        }
        assert value == expected

    def test_tgz(self) -> None:
        info = BitstreamInfo("a/b/test.tgz", "00001.tgz")
        value = _make_bitstream_file_value(info)
        expected = {
            "knora-api:hasArchiveFileValue": {
                "@type": "knora-api:ArchiveFileValue",
                "knora-api:fileValueHasFilename": "00001.tgz",
            }
        }
        assert value == expected

    def test_gzip(self) -> None:
        info = BitstreamInfo("a/b/test.gzip", "00001.gzip")
        value = _make_bitstream_file_value(info)
        expected = {
            "knora-api:hasArchiveFileValue": {
                "@type": "knora-api:ArchiveFileValue",
                "knora-api:fileValueHasFilename": "00001.gzip",
            }
        }
        assert value == expected

    def test_7z(self) -> None:
        info = BitstreamInfo("a/b/test.7z", "00001.7z")
        value = _make_bitstream_file_value(info)
        expected = {
            "knora-api:hasArchiveFileValue": {
                "@type": "knora-api:ArchiveFileValue",
                "knora-api:fileValueHasFilename": "00001.7z",
            }
        }
        assert value == expected

    def test_mp3(self) -> None:
        info = BitstreamInfo("a/b/test.mp3", "00001.mp3")
        value = _make_bitstream_file_value(info)
        expected = {
            "knora-api:hasAudioFileValue": {
                "@type": "knora-api:AudioFileValue",
                "knora-api:fileValueHasFilename": "00001.mp3",
            }
        }
        assert value == expected

    def test_wav(self) -> None:
        info = BitstreamInfo("a/b/test.wav", "00001.wav")
        value = _make_bitstream_file_value(info)
        expected = {
            "knora-api:hasAudioFileValue": {
                "@type": "knora-api:AudioFileValue",
                "knora-api:fileValueHasFilename": "00001.wav",
            }
        }
        assert value == expected

    def test_pdf(self) -> None:
        info = BitstreamInfo("a/b/test.pdf", "00001.pdf")
        value = _make_bitstream_file_value(info)
        expected = {
            "knora-api:hasDocumentFileValue": {
                "@type": "knora-api:DocumentFileValue",
                "knora-api:fileValueHasFilename": "00001.pdf",
            }
        }
        assert value == expected

    def test_doc(self) -> None:
        info = BitstreamInfo("a/b/test.doc", "00001.doc")
        value = _make_bitstream_file_value(info)
        expected = {
            "knora-api:hasDocumentFileValue": {
                "@type": "knora-api:DocumentFileValue",
                "knora-api:fileValueHasFilename": "00001.doc",
            }
        }
        assert value == expected

    def test_docx(self) -> None:
        info = BitstreamInfo("a/b/test.docx", "00001.docx")
        value = _make_bitstream_file_value(info)
        expected = {
            "knora-api:hasDocumentFileValue": {
                "@type": "knora-api:DocumentFileValue",
                "knora-api:fileValueHasFilename": "00001.docx",
            }
        }
        assert value == expected

    def test_xls(self) -> None:
        info = BitstreamInfo("a/b/test.xls", "00001.xls")
        value = _make_bitstream_file_value(info)
        expected = {
            "knora-api:hasDocumentFileValue": {
                "@type": "knora-api:DocumentFileValue",
                "knora-api:fileValueHasFilename": "00001.xls",
            }
        }
        assert value == expected

    def test_xlsx(self) -> None:
        info = BitstreamInfo("a/b/test.xlsx", "00001.xlsx")
        value = _make_bitstream_file_value(info)
        expected = {
            "knora-api:hasDocumentFileValue": {
                "@type": "knora-api:DocumentFileValue",
                "knora-api:fileValueHasFilename": "00001.xlsx",
            }
        }
        assert value == expected

    def test_ppt(self) -> None:
        info = BitstreamInfo("a/b/test.ppt", "00001.ppt")
        value = _make_bitstream_file_value(info)
        expected = {
            "knora-api:hasDocumentFileValue": {
                "@type": "knora-api:DocumentFileValue",
                "knora-api:fileValueHasFilename": "00001.ppt",
            }
        }
        assert value == expected

    def test_pptx(self) -> None:
        info = BitstreamInfo("a/b/test.pptx", "00001.pptx")
        value = _make_bitstream_file_value(info)
        expected = {
            "knora-api:hasDocumentFileValue": {
                "@type": "knora-api:DocumentFileValue",
                "knora-api:fileValueHasFilename": "00001.pptx",
            }
        }
        assert value == expected

    def test_mp4(self) -> None:
        info = BitstreamInfo("a/b/test.mp4", "00001.mp4")
        value = _make_bitstream_file_value(info)
        expected = {
            "knora-api:hasMovingImageFileValue": {
                "@type": "knora-api:MovingImageFileValue",
                "knora-api:fileValueHasFilename": "00001.mp4",
            }
        }
        assert value == expected

    def test_jpg(self) -> None:
        info = BitstreamInfo("a/b/test.jpg", "00001.jp2")
        value = _make_bitstream_file_value(info)
        expected = {
            "knora-api:hasStillImageFileValue": {
                "@type": "knora-api:StillImageFileValue",
                "knora-api:fileValueHasFilename": "00001.jp2",
            }
        }
        assert value == expected

    def test_jpeg(self) -> None:
        info = BitstreamInfo("a/b/test.jpeg", "00001.jp2")
        value = _make_bitstream_file_value(info)
        expected = {
            "knora-api:hasStillImageFileValue": {
                "@type": "knora-api:StillImageFileValue",
                "knora-api:fileValueHasFilename": "00001.jp2",
            }
        }
        assert value == expected

    def test_jp2(self) -> None:
        info = BitstreamInfo("a/b/test.jp2", "00001.jp2")
        value = _make_bitstream_file_value(info)
        expected = {
            "knora-api:hasStillImageFileValue": {
                "@type": "knora-api:StillImageFileValue",
                "knora-api:fileValueHasFilename": "00001.jp2",
            }
        }
        assert value == expected

    def test_png(self) -> None:
        info = BitstreamInfo("a/b/test.png", "00001.jp2")
        value = _make_bitstream_file_value(info)
        expected = {
            "knora-api:hasStillImageFileValue": {
                "@type": "knora-api:StillImageFileValue",
                "knora-api:fileValueHasFilename": "00001.jp2",
            }
        }
        assert value == expected

    def test_tif(self) -> None:
        info = BitstreamInfo("a/b/test.tif", "00001.jp2")
        value = _make_bitstream_file_value(info)
        expected = {
            "knora-api:hasStillImageFileValue": {
                "@type": "knora-api:StillImageFileValue",
                "knora-api:fileValueHasFilename": "00001.jp2",
            }
        }
        assert value == expected

    def test_tiff(self) -> None:
        info = BitstreamInfo("a/b/test.tiff", "00001.jp2")
        value = _make_bitstream_file_value(info)
        expected = {
            "knora-api:hasStillImageFileValue": {
                "@type": "knora-api:StillImageFileValue",
                "knora-api:fileValueHasFilename": "00001.jp2",
            }
        }
        assert value == expected

    def test_odd(self) -> None:
        info = BitstreamInfo("a/b/test.odd", "00001.odd")
        value = _make_bitstream_file_value(info)
        expected = {
            "knora-api:hasTextFileValue": {
                "@type": "knora-api:TextFileValue",
                "knora-api:fileValueHasFilename": "00001.odd",
            }
        }
        assert value == expected

    def test_rng(self) -> None:
        info = BitstreamInfo("a/b/test.rng", "00001.rng")
        value = _make_bitstream_file_value(info)
        expected = {
            "knora-api:hasTextFileValue": {
                "@type": "knora-api:TextFileValue",
                "knora-api:fileValueHasFilename": "00001.rng",
            }
        }
        assert value == expected

    def test_txt(self) -> None:
        info = BitstreamInfo("a/b/test.txt", "00001.txt")
        value = _make_bitstream_file_value(info)
        expected = {
            "knora-api:hasTextFileValue": {
                "@type": "knora-api:TextFileValue",
                "knora-api:fileValueHasFilename": "00001.txt",
            }
        }
        assert value == expected

    def test_xml(self) -> None:
        info = BitstreamInfo("a/b/test.xml", "00001.xml")
        value = _make_bitstream_file_value(info)
        expected = {
            "knora-api:hasTextFileValue": {
                "@type": "knora-api:TextFileValue",
                "knora-api:fileValueHasFilename": "00001.xml",
            }
        }
        assert value == expected

    def test_xsd(self) -> None:
        info = BitstreamInfo("a/b/test.xsd", "00001.xsd")
        value = _make_bitstream_file_value(info)
        expected = {
            "knora-api:hasTextFileValue": {
                "@type": "knora-api:TextFileValue",
                "knora-api:fileValueHasFilename": "00001.xsd",
            }
        }
        assert value == expected

    def test_xsl(self) -> None:
        info = BitstreamInfo("a/b/test.xsl", "00001.xsl")
        value = _make_bitstream_file_value(info)
        expected = {
            "knora-api:hasTextFileValue": {
                "@type": "knora-api:TextFileValue",
                "knora-api:fileValueHasFilename": "00001.xsl",
            }
        }
        assert value == expected

    def test_xslt(self) -> None:
        info = BitstreamInfo("a/b/test.xslt", "00001.xslt")
        value = _make_bitstream_file_value(info)
        expected = {
            "knora-api:hasTextFileValue": {
                "@type": "knora-api:TextFileValue",
                "knora-api:fileValueHasFilename": "00001.xslt",
            }
        }
        assert value == expected

    def test_csv(self) -> None:
        info = BitstreamInfo("a/b/test.csv", "00001.csv")
        value = _make_bitstream_file_value(info)
        expected = {
            "knora-api:hasTextFileValue": {
                "@type": "knora-api:TextFileValue",
                "knora-api:fileValueHasFilename": "00001.csv",
            }
        }
        assert value == expected

    def test_with_permissions(self) -> None:
        permission = Permissions({PermissionValue.CR: ["knora-admin:ProjectAdmin"]})
        info = BitstreamInfo("a/b/test.csv", "00001.csv", permission)
        value = _make_bitstream_file_value(info)
        expected = {
            "knora-api:hasTextFileValue": {
                "@type": "knora-api:TextFileValue",
                "knora-api:hasPermissions": "CR knora-admin:ProjectAdmin",
                "knora-api:fileValueHasFilename": "00001.csv",
            }
        }
        assert value == expected


def test_to_boolean() -> None:
    assert _to_boolean("true")
    assert _to_boolean("True")
    assert _to_boolean("1")
    assert _to_boolean(1)
    assert _to_boolean(True)
    assert not _to_boolean("false")
    assert not _to_boolean("False")
    assert not _to_boolean("0")
    assert not _to_boolean(0)
    assert not _to_boolean(False)
    with pytest.raises(BaseError):
        _to_boolean("foo")
    with pytest.raises(BaseError):
        _to_boolean(2)


if __name__ == "__main__":
    pytest.main([__file__])
