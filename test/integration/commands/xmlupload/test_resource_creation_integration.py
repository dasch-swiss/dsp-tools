from copy import copy
from dataclasses import dataclass
from unittest.mock import Mock

import pytest
from lxml import etree

from dsp_tools.commands.xmlupload import xmlupload
from dsp_tools.commands.xmlupload.iri_resolver import IriResolver
from dsp_tools.commands.xmlupload.models.sipi import Sipi
from dsp_tools.commands.xmlupload.models.upload_state import UploadState
from dsp_tools.commands.xmlupload.models.xmlresource import XMLResource
from dsp_tools.commands.xmlupload.project_client import ProjectInfo
from dsp_tools.commands.xmlupload.stash.stash_models import LinkValueStash
from dsp_tools.commands.xmlupload.stash.stash_models import LinkValueStashItem
from dsp_tools.commands.xmlupload.stash.stash_models import Stash
from dsp_tools.commands.xmlupload.upload_config import UploadConfig
from dsp_tools.models.exceptions import PermanentTimeOutError
from dsp_tools.models.exceptions import XmlUploadInterruptedError
from dsp_tools.utils.connection import Connection
from dsp_tools.utils.connection_live import ConnectionLive


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
            <text-prop name=":hasSimpleText"><text encoding="utf8">foo_1 text</text></text-prop>
        </resource>
        """,
    ]
    xml_resources = [XMLResource(etree.fromstring(xml_str), "my_onto") for xml_str in xml_strings]
    upload_state = UploadState(xml_resources, [], IriResolver(), None, UploadConfig(), {})
    con = Mock(spec=ConnectionLive)
    con.post = Mock(return_value={"@id": "foo_1_iri", "rdfs:label": "foo_1_label"})
    project_client = ProjectClientStub(con, "1234", None)
    xmlupload.upload_resources(upload_state, ".", Sipi(con), project_client, ListClientMock())
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
            <resptr-prop name=":hasCustomLink"><resptr>foo_2_id</resptr></resptr-prop>
        </resource>
        """,
    ]
    xml_resources = [XMLResource(etree.fromstring(xml_str), "my_onto") for xml_str in xml_strings]
    upload_state = UploadState(xml_resources, [], IriResolver({"foo_2_id": "foo_2_iri"}), None, UploadConfig(), {})
    con = Mock(spec=ConnectionLive)
    con.post = Mock(return_value={"@id": "foo_1_iri", "rdfs:label": "foo_1_label"})
    project_client = ProjectClientStub(con, "1234", None)
    xmlupload.upload_resources(upload_state, ".", Sipi(con), project_client, ListClientMock())
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


def test_two_resources_with_stash() -> None:
    xml_strings = [
        '<resource label="foo_1_label" restype=":foo_1_type" id="foo_1_id"></resource>',
        '<resource label="foo_2_label" restype=":foo_2_type" id="foo_2_id"></resource>',
    ]
    xml_resources = [XMLResource(etree.fromstring(xml_str), "my_onto") for xml_str in xml_strings]
    link_val_stash_dict = {
        "foo_1_id": [LinkValueStashItem("foo_1_id", "my_onto:foo_1_type", "my_onto:hasCustomLink", "foo_2_id")],
        "foo_2_id": [LinkValueStashItem("foo_2_id", "my_onto:foo_2_type", "my_onto:hasCustomLink", "foo_1_id")],
    }
    stash = Stash(link_value_stash=LinkValueStash(link_val_stash_dict), standoff_stash=None)
    upload_state = UploadState(xml_resources, [], IriResolver(), stash, UploadConfig(), {})
    con = Mock(spec=ConnectionLive)
    con.post = Mock(
        side_effect=[
            {"@id": "foo_1_iri", "rdfs:label": "foo_1_label"},
            {"@id": "foo_2_iri", "rdfs:label": "foo_2_label"},
            {},
            {},
        ]
    )
    project_client = ProjectClientStub(con, "1234", None)
    xmlupload.upload_resources(upload_state, ".", Sipi(con), project_client, ListClientMock())
    assert len(con.post.call_args_list) == 4
    match con.post.call_args_list[2].kwargs:
        case {
            "route": "/v2/values",
            "data": {
                "@type": "my_onto:foo_1_type",
                "@id": "foo_1_iri",
                "@context": dict(),
                "my_onto:hasCustomLinkValue": {
                    "@type": "knora-api:LinkValue",
                    "knora-api:linkValueHasTargetIri": {"@id": "foo_2_iri"},
                },
            },
        }:
            assert True
        case _:
            pytest.fail("POST request was not sent correctly")
    assert not upload_state.pending_resources
    assert not upload_state.failed_uploads
    assert upload_state.iri_resolver.lookup == {"foo_1_id": "foo_1_iri", "foo_2_id": "foo_2_iri"}
    assert not upload_state.pending_stash or upload_state.pending_stash.is_empty()


def test_two_resources_with_stash_interrupted_by_timeout() -> None:
    xml_strings = [
        '<resource label="foo_1_label" restype=":foo_1_type" id="foo_1_id"></resource>',
        '<resource label="foo_2_label" restype=":foo_2_type" id="foo_2_id"></resource>',
    ]
    xml_resources = [XMLResource(etree.fromstring(xml_str), "my_onto") for xml_str in xml_strings]
    link_val_stash_dict = {
        "foo_1_id": [LinkValueStashItem("foo_1_id", "my_onto:foo_1_type", "my_onto:hasCustomLink", "foo_2_id")],
        "foo_2_id": [LinkValueStashItem("foo_2_id", "my_onto:foo_2_type", "my_onto:hasCustomLink", "foo_1_id")],
    }
    stash = Stash(link_value_stash=LinkValueStash(link_val_stash_dict), standoff_stash=None)
    upload_state = UploadState(xml_resources.copy(), [], IriResolver(), copy(stash), UploadConfig(), {})
    con = Mock(spec=ConnectionLive)
    con.post = Mock(side_effect=[{"@id": "foo_1_iri", "rdfs:label": "foo_1_label"}, PermanentTimeOutError("")])
    xmlupload._handle_upload_error = Mock()
    project_client = ProjectClientStub(con, "1234", None)
    xmlupload.upload_resources(upload_state, ".", Sipi(con), project_client, ListClientMock())
    err_msg = (
        "There was a PermanentTimeOutError while trying to create resource 'foo_2_id'.\n"
        "It is unclear if the resource 'foo_2_id' was created successfully or not.\n"
        "Please check manually in the DSP-APP or DB.\n"
        "In case of successful creation, call 'resume-xmlupload' with the flag "
        "'--skip-first-resource' to prevent duplication.\n"
        "If not, a normal 'resume-xmlupload' can be started."
    )
    upload_state_expected = UploadState(
        xml_resources[1:], [], IriResolver({"foo_1_id": "foo_1_iri"}), stash, UploadConfig(), {}
    )
    xmlupload._handle_upload_error.assert_called_once_with(XmlUploadInterruptedError(err_msg), upload_state_expected)


def test_two_resources_with_stash_interrupted_by_keyboard() -> None:
    xml_strings = [
        '<resource label="foo_1_label" restype=":foo_1_type" id="foo_1_id"></resource>',
        '<resource label="foo_2_label" restype=":foo_2_type" id="foo_2_id"></resource>',
    ]
    xml_resources = [XMLResource(etree.fromstring(xml_str), "my_onto") for xml_str in xml_strings]
    link_val_stash_dict = {
        "foo_1_id": [LinkValueStashItem("foo_1_id", "my_onto:foo_1_type", "my_onto:hasCustomLink", "foo_2_id")],
        "foo_2_id": [LinkValueStashItem("foo_2_id", "my_onto:foo_2_type", "my_onto:hasCustomLink", "foo_1_id")],
    }
    stash = Stash(link_value_stash=LinkValueStash(link_val_stash_dict), standoff_stash=None)
    upload_state = UploadState(xml_resources.copy(), [], IriResolver(), copy(stash), UploadConfig(), {})
    con = Mock(spec=ConnectionLive)
    con.post = Mock(side_effect=[{"@id": "foo_1_iri", "rdfs:label": "foo_1_label"}, KeyboardInterrupt()])
    xmlupload._handle_upload_error = Mock()
    project_client = ProjectClientStub(con, "1234", None)
    xmlupload.upload_resources(upload_state, ".", Sipi(con), project_client, ListClientMock())
    err_msg = (
        "There was a KeyboardInterrupt while trying to create resource 'foo_2_id'.\n"
        "It is unclear if the resource 'foo_2_id' was created successfully or not.\n"
        "Please check manually in the DSP-APP or DB.\n"
        "In case of successful creation, call 'resume-xmlupload' with the flag "
        "'--skip-first-resource' to prevent duplication.\n"
        "If not, a normal 'resume-xmlupload' can be started."
    )
    upload_state_expected = UploadState(
        xml_resources[1:], [], IriResolver({"foo_1_id": "foo_1_iri"}), stash, UploadConfig(), {}
    )
    xmlupload._handle_upload_error.assert_called_once_with(XmlUploadInterruptedError(err_msg), upload_state_expected)


def test_two_resources_with_stash_interrupt_after() -> None:
    xml_strings = [
        '<resource label="foo_1_label" restype=":foo_1_type" id="foo_1_id"></resource>',
        '<resource label="foo_2_label" restype=":foo_2_type" id="foo_2_id"></resource>',
        '<resource label="foo_3_label" restype=":foo_3_type" id="foo_3_id"></resource>',
        '<resource label="foo_4_label" restype=":foo_4_type" id="foo_4_id"></resource>',
        '<resource label="foo_5_label" restype=":foo_5_type" id="foo_5_id"></resource>',
        '<resource label="foo_6_label" restype=":foo_6_type" id="foo_6_id"></resource>',
    ]
    xml_resources = [XMLResource(etree.fromstring(xml_str), "my_onto") for xml_str in xml_strings]
    link_val_stash_dict = {
        "foo_1_id": [LinkValueStashItem("foo_1_id", "my_onto:foo_1_type", "my_onto:hasCustomLink", "foo_2_id")],
        "foo_2_id": [LinkValueStashItem("foo_2_id", "my_onto:foo_2_type", "my_onto:hasCustomLink", "foo_1_id")],
    }
    stash = Stash(link_value_stash=LinkValueStash(link_val_stash_dict), standoff_stash=None)
    upload_config = UploadConfig(interrupt_after=2)
    upload_state = UploadState(xml_resources.copy(), [], IriResolver(), copy(stash), upload_config, {})
    con = Mock(spec=ConnectionLive)
    con.post = Mock(
        side_effect=[
            {"@id": "foo_1_iri", "rdfs:label": "foo_1_label"},
            {"@id": "foo_2_iri", "rdfs:label": "foo_2_label"},
            {"@id": "foo_3_iri", "rdfs:label": "foo_3_label"},
            {"@id": "foo_4_iri", "rdfs:label": "foo_4_label"},
            {"@id": "foo_5_iri", "rdfs:label": "foo_5_label"},
            {"@id": "foo_6_iri", "rdfs:label": "foo_6_label"},
        ]
    )
    xmlupload._handle_upload_error = Mock()
    project_client = ProjectClientStub(con, "1234", None)
    err_msg = "Interrupted: Maximum number of resources was reached (2)"

    xmlupload.upload_resources(upload_state, ".", Sipi(con), project_client, ListClientMock())
    iri_resolver_dict = {"foo_1_id": "foo_1_iri", "foo_2_id": "foo_2_iri"}
    upload_state_expected = UploadState(xml_resources[2:], [], IriResolver(iri_resolver_dict), stash, upload_config, {})
    xmlupload._handle_upload_error.assert_called_once_with(XmlUploadInterruptedError(err_msg), upload_state_expected)

    xmlupload.upload_resources(upload_state, ".", Sipi(con), project_client, ListClientMock())
    iri_resolver_dict.update({"foo_3_id": "foo_3_iri", "foo_4_id": "foo_4_iri"})
    upload_state_expected = UploadState(xml_resources[4:], [], IriResolver(iri_resolver_dict), stash, upload_config, {})
    xmlupload._handle_upload_error.assert_called_once_with(XmlUploadInterruptedError(err_msg), upload_state_expected)

    xmlupload.upload_resources(upload_state, ".", Sipi(con), project_client, ListClientMock())
    iri_resolver_dict.update({"foo_5_id": "foo_5_iri", "foo_6_id": "foo_6_iri"})
    upload_state_expected = UploadState(xml_resources[4:], [], IriResolver(iri_resolver_dict), stash, upload_config, {})
    xmlupload._handle_upload_error.assert_called_once_with(XmlUploadInterruptedError(err_msg), upload_state_expected)
