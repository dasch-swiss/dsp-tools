import pytest

from dsp_tools.commands.ingest_xmlupload.bulk_import.check_legal_info import check_legal_info_is_complete
from dsp_tools.commands.ingest_xmlupload.exceptions import LegalInfoMissingError
from dsp_tools.utils.xml_parsing.models.parsed_resource import KnoraFileValueType
from dsp_tools.utils.xml_parsing.models.parsed_resource import ParsedFileBitstream
from dsp_tools.utils.xml_parsing.models.parsed_resource import ParsedFileValue
from dsp_tools.utils.xml_parsing.models.parsed_resource import ParsedFileValueMetadata
from dsp_tools.utils.xml_parsing.models.parsed_resource import ParsedResource

LICENSE = "http://rdfh.ch/licenses/cc-by-4.0"


def _resource(res_id: str, metadata: ParsedFileValueMetadata | None) -> ParsedResource:
    file_value = None
    if metadata:
        file_value = ParsedFileValue(ParsedFileBitstream("a.jpg"), KnoraFileValueType.STILL_IMAGE_FILE, metadata)
    return ParsedResource(res_id, "onto:Image", res_id, None, [], file_value, None)


def test_complete_legal_info_passes() -> None:
    resources = [
        _resource("with_file", ParsedFileValueMetadata(LICENSE, "DaSCH", "auth_1", None)),
        _resource("without_file", None),
    ]
    check_legal_info_is_complete(resources)


@pytest.mark.parametrize(
    "metadata",
    [
        ParsedFileValueMetadata(None, "DaSCH", "auth_1", None),
        ParsedFileValueMetadata(LICENSE, None, "auth_1", None),
        ParsedFileValueMetadata(LICENSE, "DaSCH", None, None),
    ],
)
def test_missing_legal_info_raises(metadata: ParsedFileValueMetadata) -> None:
    resources = [_resource("ok", ParsedFileValueMetadata(LICENSE, "DaSCH", "auth_1", None)), _resource("bad", metadata)]
    with pytest.raises(LegalInfoMissingError) as exc_info:
        check_legal_info_is_complete(resources)
    message = str(exc_info.value)
    assert "  - bad" in message
    assert "  - ok" not in message
