import pytest
from lxml import etree

from dsp_tools.xmllib.internal.serialise_file_value import _serialise_metadata
from dsp_tools.xmllib.internal.serialise_file_value import serialise_file_value
from dsp_tools.xmllib.models.config_options import Permissions
from dsp_tools.xmllib.models.internal.file_values import FileValue
from dsp_tools.xmllib.models.internal.file_values import IIIFUri
from dsp_tools.xmllib.models.internal.file_values import Metadata
from dsp_tools.xmllib.models.licenses.recommended import LicenseRecommended


@pytest.fixture
def metadata_no_permissions() -> Metadata:
    return Metadata(
        license=LicenseRecommended.DSP.UNKNOWN,
        copyright_holder="copyright",
        authorship=("one", "one2"),
        permissions=Permissions.PROJECT_SPECIFIC_PERMISSIONS,
    )


def test_serialise_metadata(metadata_no_permissions: Metadata) -> None:
    expected = {
        "license": "http://rdfh.ch/licenses/unknown",
        "copyright-holder": "copyright",
        "authorship-id": "authorship_1",
    }
    result = _serialise_metadata(metadata_no_permissions, "authorship_1")
    assert result == expected


def test_serialise_metadata_with_permissions() -> None:
    meta = Metadata(
        license=LicenseRecommended.DSP.UNKNOWN,
        copyright_holder="copyright",
        authorship=tuple(["auth"]),
        permissions=Permissions.OPEN,
    )
    expected = {
        "license": "http://rdfh.ch/licenses/unknown",
        "copyright-holder": "copyright",
        "authorship-id": "authorship_2",
        "permissions": "open",
    }
    result = _serialise_metadata(meta, "authorship_2")
    assert result == expected


def test_serialise_file_value_bitstream(metadata_no_permissions: Metadata) -> None:
    val = FileValue("file.jpg", metadata_no_permissions, None)
    result = serialise_file_value(val, "authorship_1")
    expected = (
        b'<bitstream xmlns="https://dasch.swiss/schema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
        b'license="http://rdfh.ch/licenses/unknown" '
        b'copyright-holder="copyright" '
        b'authorship-id="authorship_1"'
        b">file.jpg</bitstream>"
    )
    assert etree.tostring(result) == expected


def test_serialise_file_value_bitstream_with_comment(metadata_no_permissions: Metadata) -> None:
    val = FileValue("file.jpg", metadata_no_permissions, "comment")
    result = serialise_file_value(val, "authorship_1")
    expected = (
        b'<bitstream xmlns="https://dasch.swiss/schema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
        b'license="http://rdfh.ch/licenses/unknown" '
        b'copyright-holder="copyright" '
        b'authorship-id="authorship_1" '
        b'comment="comment"'
        b">file.jpg</bitstream>"
    )
    assert etree.tostring(result) == expected


def test_serialise_file_value_iiif(metadata_no_permissions: Metadata) -> None:
    val = IIIFUri("https://example.org/image.jpg/full/1338%2C/0/default.jpg", metadata_no_permissions, None)
    result = serialise_file_value(val, "authorship_1")
    expected = (
        b'<iiif-uri xmlns="https://dasch.swiss/schema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
        b'license="http://rdfh.ch/licenses/unknown" '
        b'copyright-holder="copyright" '
        b'authorship-id="authorship_1"'
        b">https://example.org/image.jpg/full/1338%2C/0/default.jpg</iiif-uri>"
    )
    assert etree.tostring(result) == expected


def test_serialise_file_value_iiif_with_comment(metadata_no_permissions: Metadata) -> None:
    val = IIIFUri("https://example.org/image.jpg/full/1338%2C/0/default.jpg", metadata_no_permissions, "comment")
    result = serialise_file_value(val, "authorship_1")
    expected = (
        b'<iiif-uri xmlns="https://dasch.swiss/schema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
        b'license="http://rdfh.ch/licenses/unknown" '
        b'copyright-holder="copyright" '
        b'authorship-id="authorship_1" '
        b'comment="comment"'
        b">https://example.org/image.jpg/full/1338%2C/0/default.jpg</iiif-uri>"
    )
    assert etree.tostring(result) == expected


def test_serialise_file_value_iiif_without_legal_info() -> None:
    meta = Metadata(
        license=None,
        copyright_holder=None,
        authorship=None,
        permissions=Permissions.PROJECT_SPECIFIC_PERMISSIONS,
    )
    val = IIIFUri("https://example.org/image.jpg/full/1338%2C/0/default.jpg", meta, None)
    result = serialise_file_value(val, None)
    expected = (
        b'<iiif-uri xmlns="https://dasch.swiss/schema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"'
        b">https://example.org/image.jpg/full/1338%2C/0/default.jpg</iiif-uri>"
    )
    assert etree.tostring(result) == expected


if __name__ == "__main__":
    pytest.main([__file__])
