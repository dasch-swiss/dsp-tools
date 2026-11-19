from unittest.mock import Mock

import pytest
from lxml import etree

from dsp_tools.clients.project_client import ProjectClient
from dsp_tools.commands.xmlupload.exceptions import InvalidArkError
from dsp_tools.commands.xmlupload.exceptions import MissingProjectDefaultAuthorshipError
from dsp_tools.commands.xmlupload.prepare_xml_input.ark2iri import convert_ark_v0_to_resource_iri
from dsp_tools.commands.xmlupload.xmlupload import _resolve_project_default_authorship


def test_good() -> None:
    ark = "ark:/72163/080c-779b9990a0c3f-6e"
    iri = convert_ark_v0_to_resource_iri(ark)
    assert "http://rdfh.ch/080C/Ef9heHjPWDS7dMR_gGax2Q" == iri


def test_invalid_ark() -> None:
    with pytest.raises(
        InvalidArkError, match=r"converting ARK 'ark:/72163/080c-779b999-0a0c3f-6e'\. The ARK seems to be invalid"
    ):
        convert_ark_v0_to_resource_iri("ark:/72163/080c-779b999-0a0c3f-6e")


def test_invalid_shortcode() -> None:
    with pytest.raises(
        InvalidArkError, match=r"converting ARK 'ark:/72163/080X-779b9990a0c3f-6e'\. Invalid project shortcode '080X'"
    ):
        convert_ark_v0_to_resource_iri("ark:/72163/080X-779b9990a0c3f-6e")


def test_invalid_shortcode_long() -> None:
    with pytest.raises(
        InvalidArkError, match=r"converting ARK 'ark:/72163/080c1-779b9990a0c3f-6e'\. Invalid project shortcode '080C1'"
    ):
        convert_ark_v0_to_resource_iri("ark:/72163/080c1-779b9990a0c3f-6e")


def test_invalid_salsah_id() -> None:
    with pytest.raises(
        InvalidArkError,
        match=r"converting ARK 'ark:/72163/080c-779b99\+90a0c3f-6e'\. Invalid Salsah ID '779b99\+90a0c3f'",
    ):
        convert_ark_v0_to_resource_iri("ark:/72163/080c-779b99+90a0c3f-6e")


class TestResolveProjectDefaultAuthorship:
    def test_marker_absent_returns_none(self) -> None:
        root = etree.Element("knora", attrib={"shortcode": "0001"})
        client = Mock(spec=ProjectClient)
        assert _resolve_project_default_authorship(root, client, "0001") is None
        client.get_default_data_authorship.assert_not_called()

    def test_marker_present_returns_project_default(self) -> None:
        root = etree.Element("knora", attrib={"use-project-default-resource-authorship": "true"})
        client = Mock(spec=ProjectClient)
        client.get_default_data_authorship.return_value = ["Daisy Duck"]
        assert _resolve_project_default_authorship(root, client, "0001") == ["Daisy Duck"]

    def test_marker_present_but_no_default_aborts(self) -> None:
        root = etree.Element("knora", attrib={"use-project-default-resource-authorship": "true"})
        client = Mock(spec=ProjectClient)
        client.get_default_data_authorship.return_value = []
        with pytest.raises(MissingProjectDefaultAuthorshipError):
            _resolve_project_default_authorship(root, client, "0001")


if __name__ == "__main__":
    pytest.main([__file__])
