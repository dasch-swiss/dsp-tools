from dataclasses import dataclass
from unittest.mock import Mock

import pytest
from lxml import etree

from dsp_tools.commands.xmlupload.iri_resolver import IriResolver
from dsp_tools.commands.xmlupload.models.sipi import Sipi
from dsp_tools.commands.xmlupload.models.upload_state import UploadState
from dsp_tools.commands.xmlupload.models.xmlresource import XMLResource
from dsp_tools.commands.xmlupload.project_client import ProjectInfo
from dsp_tools.commands.xmlupload.upload_config import UploadConfig
from dsp_tools.commands.xmlupload.xmlupload import upload_resources
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


def test_one_resource_without_links() -> None:
    xml_strings = [
        """
        <resource label="foo_1_label" restype=":foo_1_type" id="foo_1_id">
            <text-prop name=":hasSimpleText">
                <text encoding="utf8">foo_1 text</text>
            </text-prop>
        </resource>
        """
    ]
    xml_resources = [XMLResource(etree.fromstring(xml_str), "my_onto") for xml_str in xml_strings]
    upload_state = UploadState(xml_resources, [], IriResolver(), None, UploadConfig(), {})
    con = Mock()
    con.post = Mock(return_value={"@id": "foo_1_iri", "rdfs:label": "foo_1_label"})
    project_client = ProjectClientStub(con, "1234", None)
    upload_resources(upload_state, ".", Sipi(con), project_client, ListClientMock())
    assert len(con.post.call_args_list) == 1
    match con.post.call_args_list[0].kwargs:
        case {
            "route": "/v2/resources",
            "data": {
                "@type": "my_onto:foo_1_type",
                "rdfs:label": "foo_1_label",
                "knora-api:attachedToProject": {"@id": "https://admin.test.dasch.swiss/project/MsOaiQkcQ7-QPxsYBKckfQ"},
                "@context": dict(),
                "my_onto:hasSimpleText": [{"@type": "knora-api:TextValue", "knora-api:valueAsString": "foo_1 text"}],
            },
        }:
            assert True
        case _:
            pytest.fail("POST request was not sent correctly")
    assert not upload_state.pending_resources
    assert not upload_state.failed_uploads
    assert upload_state.iri_resolver.lookup == {"foo_1_id": "foo_1_iri"}
    assert not upload_state.pending_stash


def test_one_resource_with_link_to_existing_resource() -> None:
    xml_strings = [
        """
        <resource label="foo_1_label" restype=":foo_1_type" id="foo_1_id">
            <resptr-prop name=":hasCustomLink">
                <resptr>foo_2_id</resptr>
            </resptr-prop>
        </resource>
        """
    ]
    xml_resources = [XMLResource(etree.fromstring(xml_str), "my_onto") for xml_str in xml_strings]
    upload_state = UploadState(xml_resources, [], IriResolver({"foo_2_id": "foo_2_iri"}), None, UploadConfig(), {})
    con = Mock()
    con.post = Mock(return_value={"@id": "foo_1_iri", "rdfs:label": "foo_1_label"})
    project_client = ProjectClientStub(con, "1234", None)
    upload_resources(upload_state, ".", Sipi(con), project_client, ListClientMock())
    assert len(con.post.call_args_list) == 1
    match con.post.call_args_list[0].kwargs:
        case {
            "route": "/v2/resources",
            "data": {
                "@type": "my_onto:foo_1_type",
                "rdfs:label": "foo_1_label",
                "knora-api:attachedToProject": {"@id": "https://admin.test.dasch.swiss/project/MsOaiQkcQ7-QPxsYBKckfQ"},
                "@context": dict(),
                "my_onto:hasCustomLinkValue": [
                    {"@type": "knora-api:LinkValue", "knora-api:linkValueHasTargetIri": {"@id": "foo_2_iri"}}
                ],
            },
        }:
            assert True
        case _:
            pytest.fail("POST request was not sent correctly")
    assert not upload_state.pending_resources
    assert not upload_state.failed_uploads
    assert upload_state.iri_resolver.lookup == {"foo_1_id": "foo_1_iri", "foo_2_id": "foo_2_iri"}
    assert not upload_state.pending_stash
