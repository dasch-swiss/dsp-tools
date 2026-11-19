from pathlib import Path

import pytest
from lxml import etree

from dsp_tools.commands.ingest_xmlupload.exceptions import InvalidIngestInputFilesError
from dsp_tools.commands.ingest_xmlupload.upload_files.upload_files import _get_validated_paths
from dsp_tools.utils.xml_parsing.get_parsed_resources import get_parsed_resources
from dsp_tools.utils.xml_parsing.models.parsed_resource import KnoraFileValueType
from dsp_tools.utils.xml_parsing.models.parsed_resource import ParsedFileBitstream
from dsp_tools.utils.xml_parsing.models.parsed_resource import ParsedFileIiifUri
from dsp_tools.utils.xml_parsing.models.parsed_resource import ParsedFilePlaceholder
from dsp_tools.utils.xml_parsing.models.parsed_resource import ParsedFileValue
from dsp_tools.utils.xml_parsing.models.parsed_resource import ParsedFileValueMetadata
from dsp_tools.utils.xml_parsing.models.parsed_resource import ParsedFileValueValue
from dsp_tools.utils.xml_parsing.models.parsed_resource import ParsedResource


def _file_value(value: ParsedFileValueValue) -> ParsedFileValue:
    metadata = ParsedFileValueMetadata(None, None, None, None)
    return ParsedFileValue(value, KnoraFileValueType.STILL_IMAGE_FILE, metadata)


def _resource(file_value: ParsedFileValue | None) -> ParsedResource:
    return ParsedResource(
        res_id="id",
        res_type=":Image",
        label="label",
        permissions_id=None,
        values=[],
        file_value=file_value,
        migration_metadata=None,
    )


def test_real_bitstream_included() -> None:
    resources = [_resource(_file_value(ParsedFileBitstream("testdata/bitstreams/test.jpg")))]
    assert _get_validated_paths(resources) == {Path("testdata/bitstreams/test.jpg")}


def test_placeholder_skipped() -> None:
    resources = [_resource(_file_value(ParsedFilePlaceholder()))]
    assert _get_validated_paths(resources) == set()


def test_iiif_uri_skipped() -> None:
    resources = [_resource(_file_value(ParsedFileIiifUri("https://example.org/image")))]
    assert _get_validated_paths(resources) == set()


def test_resource_without_file_value_skipped() -> None:
    resources = [_resource(None)]
    assert _get_validated_paths(resources) == set()


def test_mixed_resources() -> None:
    resources = [
        _resource(_file_value(ParsedFileBitstream("testdata/bitstreams/test.jpg"))),
        _resource(_file_value(ParsedFilePlaceholder())),
        _resource(_file_value(ParsedFileIiifUri("https://example.org/image"))),
        _resource(None),
    ]
    assert _get_validated_paths(resources) == {Path("testdata/bitstreams/test.jpg")}


def test_unsupported_file_raises() -> None:
    resources = [_resource(_file_value(ParsedFileBitstream("testdata/invalid-testdata/bitstreams/test.gif")))]
    with pytest.raises(InvalidIngestInputFilesError):
        _get_validated_paths(resources)


def test_placeholder_skipped_through_parser() -> None:
    xml = """
    <knora shortcode="0001" default-ontology="onto">
        <resource label="real" restype=":Image" id="real">
            <bitstream>testdata/bitstreams/test.jpg</bitstream>
        </resource>
        <resource label="placeholder" restype=":Image" id="placeholder">
            <bitstream><placeholder-file type="StillImageRepresentation"/></bitstream>
        </resource>
    </knora>
    """
    root = etree.ElementTree(etree.fromstring(xml)).getroot()
    resources = get_parsed_resources(root, "http://example.com")
    assert _get_validated_paths(resources) == {Path("testdata/bitstreams/test.jpg")}
