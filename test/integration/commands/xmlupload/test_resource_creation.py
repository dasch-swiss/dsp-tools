from dataclasses import dataclass
from test.integration.commands.xmlupload.connection_mock import ConnectionMockBase

from lxml import etree

from dsp_tools.commands.xmlupload.iri_resolver import IriResolver
from dsp_tools.commands.xmlupload.models.sipi import Sipi
from dsp_tools.commands.xmlupload.models.upload_state import UploadState
from dsp_tools.commands.xmlupload.models.xmlresource import XMLResource
from dsp_tools.commands.xmlupload.project_client import ProjectInfo
from dsp_tools.commands.xmlupload.upload_config import UploadConfig
from dsp_tools.commands.xmlupload.xmlupload import _upload_resources
from dsp_tools.utils.connection import Connection


class ListClientMock:
    def get_list_node_id_to_iri_lookup(self) -> dict[str, str]:
        return {}


@dataclass
class ProjectClientStub:
    """Stub class for ProjectClient."""

    con: Connection
    shortcode: str
    project_info: ProjectInfo | None

    def get_project_iri(self) -> str:
        return "https://admin.test.dasch.swiss/project/MsOaiQkcQ7-QPxsYBKckfQ"

    def get_ontology_iris(self) -> list[str]:
        raise NotImplementedError("get_project_iri not implemented")

    def get_ontology_name_dict(self) -> dict[str, str]:
        return {}

    def get_ontology_iri_dict(self) -> dict[str, str]:
        raise NotImplementedError("get_project_iri not implemented")


class ConnectionMock(ConnectionMockBase): ...


def test_happy_path() -> None:
    xml_str = """
    <resource label="foo_1" restype=":foo" id="foo_1">
        <text-prop name=":hasSimpleText">
            <text encoding="utf8">foo_1 text</text>
        </text-prop>
    </resource>
    """
    xml_res = XMLResource(etree.fromstring(xml_str), "default_onto")
    upload_state = UploadState([xml_res], [], IriResolver(), None, UploadConfig(), {})
    project_client = ProjectClientStub(ConnectionMock(), "1234", None)
    _upload_resources(upload_state, ".", Sipi(ConnectionMock()), project_client, ListClientMock())
    assert not upload_state.pending_resources
    assert not upload_state.failed_uploads
    assert upload_state.iri_resolver.lookup
