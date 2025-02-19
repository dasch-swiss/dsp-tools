import pytest

from dsp_tools.xmllib.models.config_options import Permissions
from dsp_tools.xmllib.models.file_values import AuthorshipLookup
from dsp_tools.xmllib.models.file_values import FileValue
from dsp_tools.xmllib.models.file_values import IIIFUri
from dsp_tools.xmllib.models.file_values import Metadata
from dsp_tools.xmllib.serialise.serialise_file_value import _serialise_metadata
from dsp_tools.xmllib.serialise.serialise_file_value import serialise_file_value

AUTHOR_LOOKUP = AuthorshipLookup({("one", "one2"): "authorship_1", tuple(["auth"]): "authorship_2"})


@pytest.fixture
def metadata_no_permissions() -> Metadata:
    return Metadata(
        license="license",
        copyright_holder="copyright",
        authorship=("one", "one2"),
        permissions=Permissions.PROJECT_SPECIFIC_PERMISSIONS,
    )


def test_serialise_metadata(metadata_no_permissions: Metadata) -> None:
    expected = {
        "license": "license",
        "copyright-holder": "copyright",
        "authorship-id": "authorship_1",
    }
    result = _serialise_metadata(metadata_no_permissions, AUTHOR_LOOKUP)
    assert result == expected


def test_serialise_metadata_with_permissions() -> None:
    meta = Metadata(
        license="license",
        copyright_holder="copyright",
        authorship=tuple(["auth"]),
        permissions=Permissions.OPEN,
    )
    expected = {
        "license": "license",
        "copyright-holder": "copyright",
        "authorship-id": "authorship_2",
        "permissions": "open",
    }
    result = _serialise_metadata(meta, AUTHOR_LOOKUP)
    assert result == expected


def test_serialise_file_value_bitstream(metadata_no_permissions: Metadata) -> None:
    val = FileValue("file.jpg", metadata_no_permissions, None)
    result = serialise_file_value(val, "authorship_1")
    expected = ""
    assert result == expected


def test_serialise_file_value_bitstream_with_comment(metadata_no_permissions: Metadata) -> None:
    val = FileValue("file.jpg", metadata_no_permissions, "comment")
    result = serialise_file_value(val, "authorship_1")
    expected = ""
    assert result == expected


def test_serialise_file_value_iiif(metadata_no_permissions: Metadata) -> None:
    val = IIIFUri("https://link.org", metadata_no_permissions, None)
    result = serialise_file_value(val, "authorship_1")
    expected = ""
    assert result == expected


def test_serialise_file_value_iiif_with_comment(metadata_no_permissions: Metadata) -> None:
    val = IIIFUri("https://link.org", metadata_no_permissions, "comment")
    result = serialise_file_value(val, "authorship_1")
    expected = ""
    assert result == expected


if __name__ == "__main__":
    pytest.main([__file__])
