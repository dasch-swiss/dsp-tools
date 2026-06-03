# mypy: disable-error-code="no-untyped-def"
from pathlib import Path

import pytest
from lxml import etree

from dsp_tools.commands.xmlupload.prepare_xml_input.read_validate_xml_file import check_if_bitstreams_exist
from dsp_tools.commands.xmlupload.exceptions import MultimediaFileNotFound


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
    # No real file exists; if placeholder is not skipped, this raises MultimediaFileNotFound
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
    with pytest.raises(MultimediaFileNotFound):
        check_if_bitstreams_exist(root, tmp_path)
