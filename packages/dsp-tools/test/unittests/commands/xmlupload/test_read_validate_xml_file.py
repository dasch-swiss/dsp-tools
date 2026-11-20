# mypy: disable-error-code="no-untyped-def"
import warnings
from pathlib import Path
from unittest.mock import Mock
from unittest.mock import patch

import pytest
from lxml import etree
from requests import Response

from dsp_tools.commands.xmlupload.exceptions import MultimediaFileNotFoundError
from dsp_tools.commands.xmlupload.prepare_xml_input.read_validate_xml_file import check_if_bitstreams_exist
from dsp_tools.commands.xmlupload.prepare_xml_input.read_validate_xml_file import validate_iiif_uris
from dsp_tools.error.custom_warnings import DspToolsUserWarning

NETWORK_CALL = "dsp_tools.commands.xmlupload.prepare_xml_input.iiif_uri_validator.IIIFUriValidator._make_network_call"
REFUSING_HOST = "https://iiif.refusing.org"
GOOD_HOST = "https://iiif.dasch.swiss"


def _make_root(resources_xml: str) -> etree._Element:
    return etree.fromstring(f"<knora>{resources_xml}</knora>")


def test_check_if_bitstreams_exist_skips_placeholder(tmp_path: Path) -> None:
    root = _make_root(
        """<resource id="res_1">
            <bitstream license="http://rdfh.ch/licenses/unknown" copyright-holder="DaSCH" authorship-id="a1">
                <placeholder type="image"/>
            </bitstream>
        </resource>"""
    )
    # No real file exists; if placeholder is not skipped, this raises MultimediaFileNotFoundError
    check_if_bitstreams_exist(root, tmp_path)


def test_check_if_bitstreams_exist_checks_real_file(tmp_path: Path) -> None:
    (tmp_path / "image.jpg").write_bytes(b"")
    root = _make_root(
        """<resource id="res_1">
            <bitstream>image.jpg</bitstream>
        </resource>"""
    )
    check_if_bitstreams_exist(root, tmp_path)


def test_check_if_bitstreams_exist_raises_for_missing_file(tmp_path: Path) -> None:
    root = _make_root(
        """<resource id="res_1">
            <bitstream>missing.jpg</bitstream>
        </resource>"""
    )
    with pytest.raises(MultimediaFileNotFoundError):
        check_if_bitstreams_exist(root, tmp_path)


def _response(status_code: int) -> Response:
    response = Response()
    response.status_code = status_code
    return response


def _iiif_root(uris: list[str]) -> etree._Element:
    return _make_root(
        "".join(f'<resource id="r{i}"><iiif-uri>{uri}</iiif-uri></resource>' for i, uri in enumerate(uris))
    )


def _image_uri(host: str, identifier: str) -> str:
    return f"{host}/0811/{identifier}.jp2/full/max/0/default.jpg"


@patch(NETWORK_CALL)
def test_validate_iiif_uris_stops_calling_refusing_host(mock_call: Mock, capsys: pytest.CaptureFixture[str]) -> None:
    def respond(uri: str) -> Response:
        return _response(403) if uri.startswith(REFUSING_HOST) else _response(200)

    mock_call.side_effect = respond
    uris = [_image_uri(REFUSING_HOST, x) for x in ("a", "b", "c")] + [_image_uri(GOOD_HOST, "d")]
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        validate_iiif_uris(_iiif_root(uris))
    called_uris = [c.args[0] for c in mock_call.call_args_list]
    assert called_uris == [uris[0], uris[3]]
    out = capsys.readouterr().out
    assert "IIIF server: iiif.refusing.org" in out
    assert "Number of IIIF URI(s) that were not checked: 3" in out


@patch(NETWORK_CALL)
def test_validate_iiif_uris_warns_for_invalid_uri(mock_call: Mock) -> None:
    mock_call.return_value = _response(404)
    with pytest.warns(DspToolsUserWarning, match="Status code: 404"):
        validate_iiif_uris(_iiif_root([_image_uri(GOOD_HOST, "a")]))
