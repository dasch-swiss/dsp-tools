import pytest

from dsp_tools.commands.xmlupload.models.permission import Permissions
from dsp_tools.commands.xmlupload.models.permission import PermissionValue
from dsp_tools.commands.xmlupload.models.Values_serialise import UploadedFileValue


class TestMakeBitstreamFileValue:
    """Tests UploadedFileValue.serserialise()"""

    def test_zip(self) -> None:
        info = UploadedFileValue("a/b/test.zip", "00001.zip")
        value = info.serialise()
        expected = {
            "knora-api:hasArchiveFileValue": {
                "@type": "knora-api:ArchiveFileValue",
                "knora-api:fileValueHasFilename": "00001.zip",
            }
        }
        assert value == expected

    def test_tar(self) -> None:
        info = UploadedFileValue("a/b/test.tar", "00001.tar")
        value = info.serialise()
        expected = {
            "knora-api:hasArchiveFileValue": {
                "@type": "knora-api:ArchiveFileValue",
                "knora-api:fileValueHasFilename": "00001.tar",
            }
        }
        assert value == expected

    def test_gz(self) -> None:
        info = UploadedFileValue("a/b/test.gz", "00001.gz")
        value = info.serialise()
        expected = {
            "knora-api:hasArchiveFileValue": {
                "@type": "knora-api:ArchiveFileValue",
                "knora-api:fileValueHasFilename": "00001.gz",
            }
        }
        assert value == expected

    def test_z(self) -> None:
        info = UploadedFileValue("a/b/test.z", "00001.z")
        value = info.serialise()
        expected = {
            "knora-api:hasArchiveFileValue": {
                "@type": "knora-api:ArchiveFileValue",
                "knora-api:fileValueHasFilename": "00001.z",
            }
        }
        assert value == expected

    def test_tar_gz(self) -> None:
        info = UploadedFileValue("a/b/test.tar.gz", "00001.tar.gz")
        value = info.serialise()
        expected = {
            "knora-api:hasArchiveFileValue": {
                "@type": "knora-api:ArchiveFileValue",
                "knora-api:fileValueHasFilename": "00001.tar.gz",
            }
        }
        assert value == expected

    def test_tgz(self) -> None:
        info = UploadedFileValue("a/b/test.tgz", "00001.tgz")
        value = info.serialise()
        expected = {
            "knora-api:hasArchiveFileValue": {
                "@type": "knora-api:ArchiveFileValue",
                "knora-api:fileValueHasFilename": "00001.tgz",
            }
        }
        assert value == expected

    def test_gzip(self) -> None:
        info = UploadedFileValue("a/b/test.gzip", "00001.gzip")
        value = info.serialise()
        expected = {
            "knora-api:hasArchiveFileValue": {
                "@type": "knora-api:ArchiveFileValue",
                "knora-api:fileValueHasFilename": "00001.gzip",
            }
        }
        assert value == expected

    def test_7z(self) -> None:
        info = UploadedFileValue("a/b/test.7z", "00001.7z")
        value = info.serialise()
        expected = {
            "knora-api:hasArchiveFileValue": {
                "@type": "knora-api:ArchiveFileValue",
                "knora-api:fileValueHasFilename": "00001.7z",
            }
        }
        assert value == expected

    def test_mp3(self) -> None:
        info = UploadedFileValue("a/b/test.mp3", "00001.mp3")
        value = info.serialise()
        expected = {
            "knora-api:hasAudioFileValue": {
                "@type": "knora-api:AudioFileValue",
                "knora-api:fileValueHasFilename": "00001.mp3",
            }
        }
        assert value == expected

    def test_wav(self) -> None:
        info = UploadedFileValue("a/b/test.wav", "00001.wav")
        value = info.serialise()
        expected = {
            "knora-api:hasAudioFileValue": {
                "@type": "knora-api:AudioFileValue",
                "knora-api:fileValueHasFilename": "00001.wav",
            }
        }
        assert value == expected

    def test_pdf(self) -> None:
        info = UploadedFileValue("a/b/test.pdf", "00001.pdf")
        value = info.serialise()
        expected = {
            "knora-api:hasDocumentFileValue": {
                "@type": "knora-api:DocumentFileValue",
                "knora-api:fileValueHasFilename": "00001.pdf",
            }
        }
        assert value == expected

    def test_doc(self) -> None:
        info = UploadedFileValue("a/b/test.doc", "00001.doc")
        value = info.serialise()
        expected = {
            "knora-api:hasDocumentFileValue": {
                "@type": "knora-api:DocumentFileValue",
                "knora-api:fileValueHasFilename": "00001.doc",
            }
        }
        assert value == expected

    def test_docx(self) -> None:
        info = UploadedFileValue("a/b/test.docx", "00001.docx")
        value = info.serialise()
        expected = {
            "knora-api:hasDocumentFileValue": {
                "@type": "knora-api:DocumentFileValue",
                "knora-api:fileValueHasFilename": "00001.docx",
            }
        }
        assert value == expected

    def test_xls(self) -> None:
        info = UploadedFileValue("a/b/test.xls", "00001.xls")
        value = info.serialise()
        expected = {
            "knora-api:hasDocumentFileValue": {
                "@type": "knora-api:DocumentFileValue",
                "knora-api:fileValueHasFilename": "00001.xls",
            }
        }
        assert value == expected

    def test_xlsx(self) -> None:
        info = UploadedFileValue("a/b/test.xlsx", "00001.xlsx")
        value = info.serialise()
        expected = {
            "knora-api:hasDocumentFileValue": {
                "@type": "knora-api:DocumentFileValue",
                "knora-api:fileValueHasFilename": "00001.xlsx",
            }
        }
        assert value == expected

    def test_ppt(self) -> None:
        info = UploadedFileValue("a/b/test.ppt", "00001.ppt")
        value = info.serialise()
        expected = {
            "knora-api:hasDocumentFileValue": {
                "@type": "knora-api:DocumentFileValue",
                "knora-api:fileValueHasFilename": "00001.ppt",
            }
        }
        assert value == expected

    def test_pptx(self) -> None:
        info = UploadedFileValue("a/b/test.pptx", "00001.pptx")
        value = info.serialise()
        expected = {
            "knora-api:hasDocumentFileValue": {
                "@type": "knora-api:DocumentFileValue",
                "knora-api:fileValueHasFilename": "00001.pptx",
            }
        }
        assert value == expected

    def test_mp4(self) -> None:
        info = UploadedFileValue("a/b/test.mp4", "00001.mp4")
        value = info.serialise()
        expected = {
            "knora-api:hasMovingImageFileValue": {
                "@type": "knora-api:MovingImageFileValue",
                "knora-api:fileValueHasFilename": "00001.mp4",
            }
        }
        assert value == expected

    def test_jpg(self) -> None:
        info = UploadedFileValue("a/b/test.jpg", "00001.jp2")
        value = info.serialise()
        expected = {
            "knora-api:hasStillImageFileValue": {
                "@type": "knora-api:StillImageFileValue",
                "knora-api:fileValueHasFilename": "00001.jp2",
            }
        }
        assert value == expected

    def test_jpeg(self) -> None:
        info = UploadedFileValue("a/b/test.jpeg", "00001.jp2")
        value = info.serialise()
        expected = {
            "knora-api:hasStillImageFileValue": {
                "@type": "knora-api:StillImageFileValue",
                "knora-api:fileValueHasFilename": "00001.jp2",
            }
        }
        assert value == expected

    def test_jp2(self) -> None:
        info = UploadedFileValue("a/b/test.jp2", "00001.jp2")
        value = info.serialise()
        expected = {
            "knora-api:hasStillImageFileValue": {
                "@type": "knora-api:StillImageFileValue",
                "knora-api:fileValueHasFilename": "00001.jp2",
            }
        }
        assert value == expected

    def test_png(self) -> None:
        info = UploadedFileValue("a/b/test.png", "00001.jp2")
        value = info.serialise()
        expected = {
            "knora-api:hasStillImageFileValue": {
                "@type": "knora-api:StillImageFileValue",
                "knora-api:fileValueHasFilename": "00001.jp2",
            }
        }
        assert value == expected

    def test_tif(self) -> None:
        info = UploadedFileValue("a/b/test.tif", "00001.jp2")
        value = info.serialise()
        expected = {
            "knora-api:hasStillImageFileValue": {
                "@type": "knora-api:StillImageFileValue",
                "knora-api:fileValueHasFilename": "00001.jp2",
            }
        }
        assert value == expected

    def test_tiff(self) -> None:
        info = UploadedFileValue("a/b/test.tiff", "00001.jp2")
        value = info.serialise()
        expected = {
            "knora-api:hasStillImageFileValue": {
                "@type": "knora-api:StillImageFileValue",
                "knora-api:fileValueHasFilename": "00001.jp2",
            }
        }
        assert value == expected

    def test_odd(self) -> None:
        info = UploadedFileValue("a/b/test.odd", "00001.odd")
        value = info.serialise()
        expected = {
            "knora-api:hasTextFileValue": {
                "@type": "knora-api:TextFileValue",
                "knora-api:fileValueHasFilename": "00001.odd",
            }
        }
        assert value == expected

    def test_rng(self) -> None:
        info = UploadedFileValue("a/b/test.rng", "00001.rng")
        value = info.serialise()
        expected = {
            "knora-api:hasTextFileValue": {
                "@type": "knora-api:TextFileValue",
                "knora-api:fileValueHasFilename": "00001.rng",
            }
        }
        assert value == expected

    def test_txt(self) -> None:
        info = UploadedFileValue("a/b/test.txt", "00001.txt")
        value = info.serialise()
        expected = {
            "knora-api:hasTextFileValue": {
                "@type": "knora-api:TextFileValue",
                "knora-api:fileValueHasFilename": "00001.txt",
            }
        }
        assert value == expected

    def test_xml(self) -> None:
        info = UploadedFileValue("a/b/test.xml", "00001.xml")
        value = info.serialise()
        expected = {
            "knora-api:hasTextFileValue": {
                "@type": "knora-api:TextFileValue",
                "knora-api:fileValueHasFilename": "00001.xml",
            }
        }
        assert value == expected

    def test_xsd(self) -> None:
        info = UploadedFileValue("a/b/test.xsd", "00001.xsd")
        value = info.serialise()
        expected = {
            "knora-api:hasTextFileValue": {
                "@type": "knora-api:TextFileValue",
                "knora-api:fileValueHasFilename": "00001.xsd",
            }
        }
        assert value == expected

    def test_xsl(self) -> None:
        info = UploadedFileValue("a/b/test.xsl", "00001.xsl")
        value = info.serialise()
        expected = {
            "knora-api:hasTextFileValue": {
                "@type": "knora-api:TextFileValue",
                "knora-api:fileValueHasFilename": "00001.xsl",
            }
        }
        assert value == expected

    def test_xslt(self) -> None:
        info = UploadedFileValue("a/b/test.xslt", "00001.xslt")
        value = info.serialise()
        expected = {
            "knora-api:hasTextFileValue": {
                "@type": "knora-api:TextFileValue",
                "knora-api:fileValueHasFilename": "00001.xslt",
            }
        }
        assert value == expected

    def test_csv(self) -> None:
        info = UploadedFileValue("a/b/test.csv", "00001.csv")
        value = info.serialise()
        expected = {
            "knora-api:hasTextFileValue": {
                "@type": "knora-api:TextFileValue",
                "knora-api:fileValueHasFilename": "00001.csv",
            }
        }
        assert value == expected

    def test_with_permissions(self) -> None:
        permission = Permissions({PermissionValue.CR: ["knora-admin:ProjectAdmin"]})
        info = UploadedFileValue("a/b/test.csv", "00001.csv", str(permission))
        value = info.serialise()
        expected = {
            "knora-api:hasTextFileValue": {
                "@type": "knora-api:TextFileValue",
                "knora-api:hasPermissions": "CR knora-admin:ProjectAdmin",
                "knora-api:fileValueHasFilename": "00001.csv",
            }
        }
        assert value == expected


if __name__ == "__main__":
    pytest.main([__file__])
