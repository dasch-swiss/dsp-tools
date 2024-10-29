from copy import deepcopy
from dataclasses import dataclass
from unittest.mock import Mock

import pytest
from lxml import etree
from requests import Response

import dsp_tools.commands.xmlupload.models.upload_clients
from dsp_tools.commands.xmlupload import xmlupload
from dsp_tools.commands.xmlupload.iri_resolver import IriResolver
from dsp_tools.commands.xmlupload.models.deserialise.xmlresource import XMLResource
from dsp_tools.commands.xmlupload.models.ingest import AssetClient
from dsp_tools.commands.xmlupload.models.ingest import DspIngestClientLive
from dsp_tools.commands.xmlupload.models.upload_clients import UploadClients
from dsp_tools.commands.xmlupload.models.upload_state import UploadState
from dsp_tools.commands.xmlupload.project_client import ProjectInfo
from dsp_tools.commands.xmlupload.stash.stash_models import LinkValueStash
from dsp_tools.commands.xmlupload.stash.stash_models import LinkValueStashItem
from dsp_tools.commands.xmlupload.stash.stash_models import Stash
from dsp_tools.commands.xmlupload.upload_config import UploadConfig
from dsp_tools.models.custom_warnings import DspToolsUserWarning
from dsp_tools.models.exceptions import PermanentTimeOutError
from dsp_tools.models.exceptions import XmlUploadInterruptedError
from dsp_tools.utils.connection import Connection
from dsp_tools.utils.connection_live import ConnectionLive
from test.integration.commands.xmlupload.authentication_client_mock import AuthenticationClientMockBase


@pytest.fixture
def ingest_client_mock():  # type: ignore[no-untyped-def]
    return Mock(spec_set=AssetClient)


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


def test_one_resource_without_links(ingest_client_mock: AssetClient) -> None:
    xml_strings = [
        """
        <resource label="foo_1_label" restype=":foo_1_type" id="foo_1_id">
            <text-prop name=":hasSimpleText"><text encoding="utf8">foo_1 text</text></text-prop>
        </resource>
        """,
    ]
    xml_resources = [XMLResource.from_node(etree.fromstring(xml_str), "my_onto") for xml_str in xml_strings]
    upload_state = UploadState(xml_resources, None, UploadConfig(), {})
    con = Mock(spec_set=ConnectionLive)
    post_responses = [{"@id": "foo_1_iri", "rdfs:label": "foo_1_label"}]
    con.post = Mock(side_effect=post_responses)
    project_client = ProjectClientStub(con, "1234", None)
    clients = dsp_tools.commands.xmlupload.models.upload_clients.UploadClients(
        ingest_client_mock, project_client, ListClientMock()
    )

    xmlupload._upload_resources(clients, upload_state)

    assert len(con.post.call_args_list) == len(post_responses)
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


def test_one_resource_with_link_to_existing_resource(ingest_client_mock: AssetClient) -> None:
    xml_strings = [
        """
        <resource label="foo_1_label" restype=":foo_1_type" id="foo_1_id">
            <resptr-prop name=":hasCustomLink"><resptr>foo_2_id</resptr></resptr-prop>
        </resource>
        """,
    ]
    xml_resources = [XMLResource.from_node(etree.fromstring(xml_str), "my_onto") for xml_str in xml_strings]
    upload_state = UploadState(xml_resources, None, UploadConfig(), {}, [], IriResolver({"foo_2_id": "foo_2_iri"}))
    con = Mock(spec_set=ConnectionLive)
    post_responses = [{"@id": "foo_1_iri", "rdfs:label": "foo_1_label"}]
    con.post = Mock(side_effect=post_responses)
    project_client = ProjectClientStub(con, "1234", None)
    clients = dsp_tools.commands.xmlupload.models.upload_clients.UploadClients(
        ingest_client_mock, project_client, ListClientMock()
    )

    xmlupload._upload_resources(clients, upload_state)

    assert len(con.post.call_args_list) == len(post_responses)
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


def test_2_resources_with_stash_interrupted_by_timeout(ingest_client_mock: AssetClient) -> None:
    _2_resources_with_stash_interrupted_by_error(PermanentTimeOutError(""), "PermanentTimeOutError", ingest_client_mock)


def test_2_resources_with_stash_interrupted_by_keyboard(ingest_client_mock: AssetClient) -> None:
    _2_resources_with_stash_interrupted_by_error(KeyboardInterrupt(), "KeyboardInterrupt", ingest_client_mock)


def _2_resources_with_stash_interrupted_by_error(
    err_to_interrupt_with: BaseException, err_as_str: str, ingest_client_mock: AssetClient
) -> None:
    xml_strings = [
        '<resource label="foo_1_label" restype=":foo_1_type" id="foo_1_id"></resource>',
        '<resource label="foo_2_label" restype=":foo_2_type" id="foo_2_id"></resource>',
    ]
    xml_resources = [XMLResource.from_node(etree.fromstring(xml_str), "my_onto") for xml_str in xml_strings]
    link_val_stash_dict = {
        "foo_1_id": [LinkValueStashItem("foo_1_id", "my_onto:foo_1_type", "my_onto:hasCustomLink", "foo_2_id")],
        "foo_2_id": [LinkValueStashItem("foo_2_id", "my_onto:foo_2_type", "my_onto:hasCustomLink", "foo_1_id")],
    }
    stash = Stash(link_value_stash=LinkValueStash(link_val_stash_dict), standoff_stash=None)
    upload_state = UploadState(xml_resources.copy(), deepcopy(stash), UploadConfig(), {})
    con = Mock(spec_set=ConnectionLive)
    post_responses = [
        {"@id": "foo_1_iri", "rdfs:label": "foo_1_label"},
        err_to_interrupt_with,
    ]
    con.post = Mock(side_effect=post_responses)
    project_client = ProjectClientStub(con, "1234", None)
    xmlupload._handle_upload_error = Mock()
    clients = dsp_tools.commands.xmlupload.models.upload_clients.UploadClients(
        ingest_client_mock, project_client, ListClientMock()
    )

    with pytest.warns(DspToolsUserWarning):
        xmlupload._upload_resources(clients, upload_state)

    assert len(con.post.call_args_list) == len(post_responses)
    err_msg = (
        f"There was a {err_as_str} while trying to create resource 'foo_2_id'.\n"
        "It is unclear if the resource 'foo_2_id' was created successfully or not.\n"
        "Please check manually in the DSP-APP or DB.\n"
        "In case of successful creation, call 'resume-xmlupload' with the flag "
        "'--skip-first-resource' to prevent duplication.\n"
        "If not, a normal 'resume-xmlupload' can be started."
    )
    upload_state_expected = UploadState(
        xml_resources[1:], stash, UploadConfig(), {}, [], IriResolver({"foo_1_id": "foo_1_iri"})
    )
    xmlupload._handle_upload_error.assert_called_once_with(XmlUploadInterruptedError(err_msg), upload_state_expected)


def test_2_resources_with_stash(ingest_client_mock: AssetClient) -> None:
    xml_strings = [
        '<resource label="foo_1_label" restype=":foo_1_type" id="foo_1_id"></resource>',
        '<resource label="foo_2_label" restype=":foo_2_type" id="foo_2_id"></resource>',
    ]
    xml_resources = [XMLResource.from_node(etree.fromstring(xml_str), "my_onto") for xml_str in xml_strings]
    link_val_stash_dict = {
        "foo_1_id": [LinkValueStashItem("foo_1_id", "my_onto:foo_1_type", "my_onto:hasCustomLink", "foo_2_id")],
        "foo_2_id": [LinkValueStashItem("foo_2_id", "my_onto:foo_2_type", "my_onto:hasCustomLink", "foo_1_id")],
    }
    stash = Stash(link_value_stash=LinkValueStash(link_val_stash_dict), standoff_stash=None)
    upload_state = UploadState(xml_resources.copy(), deepcopy(stash), UploadConfig(), {})
    con = Mock(spec_set=ConnectionLive)
    post_responses = [
        {"@id": "foo_1_iri", "rdfs:label": "foo_1_label"},
        {"@id": "foo_2_iri", "rdfs:label": "foo_2_label"},
        {},  # uploading a stash doesn't rely on a certain response
        {},  # uploading a stash doesn't rely on a certain response
    ]
    con.post = Mock(side_effect=post_responses)
    project_client = ProjectClientStub(con, "1234", None)
    clients = dsp_tools.commands.xmlupload.models.upload_clients.UploadClients(
        ingest_client_mock, project_client, ListClientMock()
    )

    xmlupload._upload_resources(clients, upload_state)

    assert len(con.post.call_args_list) == len(post_responses)
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


def test_5_resources_with_stash_and_interrupt_after_2(ingest_client_mock: AssetClient) -> None:
    xml_strings = [
        '<resource label="foo_1_label" restype=":foo_1_type" id="foo_1_id"></resource>',
        '<resource label="foo_2_label" restype=":foo_2_type" id="foo_2_id"></resource>',
        '<resource label="foo_3_label" restype=":foo_3_type" id="foo_3_id"></resource>',
        '<resource label="foo_4_label" restype=":foo_4_type" id="foo_4_id"></resource>',
        '<resource label="foo_5_label" restype=":foo_5_type" id="foo_5_id"></resource>',
    ]
    xml_resources = [XMLResource.from_node(etree.fromstring(xml_str), "my_onto") for xml_str in xml_strings]
    link_val_stash_dict = {
        "foo_1_id": [LinkValueStashItem("foo_1_id", "my_onto:foo_1_type", "my_onto:hasCustomLink", "foo_2_id")],
        "foo_2_id": [LinkValueStashItem("foo_2_id", "my_onto:foo_2_type", "my_onto:hasCustomLink", "foo_1_id")],
    }
    stash = Stash(link_value_stash=LinkValueStash(link_val_stash_dict), standoff_stash=None)
    upload_config = UploadConfig(interrupt_after=2)
    upload_state = UploadState(xml_resources.copy(), deepcopy(stash), upload_config, {})
    con = Mock(spec_set=ConnectionLive)
    post_responses = [
        {"@id": "foo_1_iri", "rdfs:label": "foo_1_label"},
        {"@id": "foo_2_iri", "rdfs:label": "foo_2_label"},
        {"@id": "foo_3_iri", "rdfs:label": "foo_3_label"},
        {"@id": "foo_4_iri", "rdfs:label": "foo_4_label"},
        {"@id": "foo_5_iri", "rdfs:label": "foo_5_label"},
        {},  # uploading a stash doesn't rely on a certain response
        {},  # uploading a stash doesn't rely on a certain response
    ]
    con.post = Mock(side_effect=post_responses)
    project_client = ProjectClientStub(con, "1234", None)
    xmlupload._handle_upload_error = Mock()
    err_msg = "Interrupted: Maximum number of resources was reached (2)"

    client = dsp_tools.commands.xmlupload.models.upload_clients.UploadClients(
        ingest_client_mock, project_client, ListClientMock()
    )

    xmlupload._upload_resources(client, upload_state)
    iri_resolver_expected = IriResolver({"foo_1_id": "foo_1_iri", "foo_2_id": "foo_2_iri"})
    upload_state_expected = UploadState(xml_resources[2:], stash, upload_config, {}, [], iri_resolver_expected)
    xmlupload._handle_upload_error.assert_called_once_with(XmlUploadInterruptedError(err_msg), upload_state_expected)

    xmlupload._handle_upload_error = Mock()
    xmlupload._upload_resources(client, upload_state)
    iri_resolver_expected.lookup.update({"foo_3_id": "foo_3_iri", "foo_4_id": "foo_4_iri"})
    upload_state_expected = UploadState(xml_resources[4:], stash, upload_config, {}, [], iri_resolver_expected)
    xmlupload._handle_upload_error.assert_called_once_with(XmlUploadInterruptedError(err_msg), upload_state_expected)

    xmlupload._handle_upload_error = Mock()
    xmlupload._upload_resources(client, upload_state)
    iri_resolver_expected.lookup.update({"foo_5_id": "foo_5_iri"})
    empty_stash = Stash(standoff_stash=None, link_value_stash=LinkValueStash({}))
    upload_state_expected = UploadState([], empty_stash, upload_config, {}, [], iri_resolver_expected)
    xmlupload._handle_upload_error.assert_not_called()
    assert upload_state == upload_state_expected


def test_6_resources_with_stash_and_interrupt_after_2(ingest_client_mock: AssetClient) -> None:
    xml_strings = [
        '<resource label="foo_1_label" restype=":foo_1_type" id="foo_1_id"></resource>',
        '<resource label="foo_2_label" restype=":foo_2_type" id="foo_2_id"></resource>',
        '<resource label="foo_3_label" restype=":foo_3_type" id="foo_3_id"></resource>',
        '<resource label="foo_4_label" restype=":foo_4_type" id="foo_4_id"></resource>',
        '<resource label="foo_5_label" restype=":foo_5_type" id="foo_5_id"></resource>',
        '<resource label="foo_6_label" restype=":foo_6_type" id="foo_6_id"></resource>',
    ]
    xml_resources = [XMLResource.from_node(etree.fromstring(xml_str), "my_onto") for xml_str in xml_strings]
    link_val_stash_dict = {
        "foo_1_id": [LinkValueStashItem("foo_1_id", "my_onto:foo_1_type", "my_onto:hasCustomLink", "foo_2_id")],
        "foo_2_id": [LinkValueStashItem("foo_2_id", "my_onto:foo_2_type", "my_onto:hasCustomLink", "foo_1_id")],
    }
    stash = Stash(link_value_stash=LinkValueStash(link_val_stash_dict), standoff_stash=None)
    upload_config = UploadConfig(interrupt_after=2)
    upload_state = UploadState(xml_resources.copy(), deepcopy(stash), upload_config, {})
    con = Mock(spec_set=ConnectionLive)
    post_responses = [
        {"@id": "foo_1_iri", "rdfs:label": "foo_1_label"},
        {"@id": "foo_2_iri", "rdfs:label": "foo_2_label"},
        {"@id": "foo_3_iri", "rdfs:label": "foo_3_label"},
        {"@id": "foo_4_iri", "rdfs:label": "foo_4_label"},
        {"@id": "foo_5_iri", "rdfs:label": "foo_5_label"},
        {"@id": "foo_6_iri", "rdfs:label": "foo_6_label"},
        {},  # uploading a stash doesn't rely on a certain response
        {},  # uploading a stash doesn't rely on a certain response
    ]
    con.post = Mock(side_effect=post_responses)
    project_client = ProjectClientStub(con, "1234", None)
    xmlupload._handle_upload_error = Mock()
    err_msg = "Interrupted: Maximum number of resources was reached (2)"

    client = dsp_tools.commands.xmlupload.models.upload_clients.UploadClients(
        ingest_client_mock, project_client, ListClientMock()
    )

    xmlupload._upload_resources(client, upload_state)
    iri_resolver_expected = IriResolver({"foo_1_id": "foo_1_iri", "foo_2_id": "foo_2_iri"})
    upload_state_expected = UploadState(xml_resources[2:], stash, upload_config, {}, [], iri_resolver_expected)
    xmlupload._handle_upload_error.assert_called_once_with(XmlUploadInterruptedError(err_msg), upload_state_expected)

    xmlupload._handle_upload_error = Mock()
    xmlupload._upload_resources(client, upload_state)
    iri_resolver_expected.lookup.update({"foo_3_id": "foo_3_iri", "foo_4_id": "foo_4_iri"})
    upload_state_expected = UploadState(xml_resources[4:], stash, upload_config, {}, [], iri_resolver_expected)
    xmlupload._handle_upload_error.assert_called_once_with(XmlUploadInterruptedError(err_msg), upload_state_expected)

    xmlupload._handle_upload_error = Mock()
    xmlupload._upload_resources(client, upload_state)
    iri_resolver_expected.lookup.update({"foo_5_id": "foo_5_iri", "foo_6_id": "foo_6_iri"})
    upload_state_expected = UploadState([], stash, upload_config, {}, [], iri_resolver_expected)
    xmlupload._handle_upload_error.assert_called_once_with(XmlUploadInterruptedError(err_msg), upload_state_expected)

    xmlupload._handle_upload_error = Mock()
    xmlupload._upload_resources(client, upload_state)
    empty_stash = Stash(standoff_stash=None, link_value_stash=LinkValueStash({}))
    upload_state_expected = UploadState([], empty_stash, upload_config, {}, [], iri_resolver_expected)
    xmlupload._handle_upload_error.assert_not_called()
    assert upload_state == upload_state_expected


def test_logging(caplog: pytest.LogCaptureFixture, ingest_client_mock: AssetClient) -> None:
    xml_strings = [
        '<resource label="foo_1_label" restype=":foo_1_type" id="foo_1_id"></resource>',
        '<resource label="foo_2_label" restype=":foo_2_type" id="foo_2_id"></resource>',
        '<resource label="foo_3_label" restype=":foo_3_type" id="foo_3_id"></resource>',
        '<resource label="foo_4_label" restype=":foo_4_type" id="foo_4_id"></resource>',
        '<resource label="foo_5_label" restype=":foo_5_type" id="foo_5_id"></resource>',
    ]
    xml_resources = [XMLResource.from_node(etree.fromstring(xml_str), "my_onto") for xml_str in xml_strings]
    link_val_stash_dict = {
        "foo_1_id": [LinkValueStashItem("foo_1_id", "my_onto:foo_1_type", "my_onto:hasCustomLink", "foo_2_id")],
        "foo_2_id": [LinkValueStashItem("foo_2_id", "my_onto:foo_2_type", "my_onto:hasCustomLink", "foo_1_id")],
    }
    stash = Stash(link_value_stash=LinkValueStash(link_val_stash_dict), standoff_stash=None)
    upload_config = UploadConfig(interrupt_after=2)
    upload_state = UploadState(xml_resources.copy(), deepcopy(stash), upload_config, {})
    con = Mock(spec_set=ConnectionLive)
    post_responses = [
        {"@id": "foo_1_iri", "rdfs:label": "foo_1_label"},
        {"@id": "foo_2_iri", "rdfs:label": "foo_2_label"},
        {"@id": "foo_3_iri", "rdfs:label": "foo_3_label"},
        {"@id": "foo_4_iri", "rdfs:label": "foo_4_label"},
        {"@id": "foo_5_iri", "rdfs:label": "foo_5_label"},
        {},  # uploading a stash doesn't rely on a certain response
        {},  # uploading a stash doesn't rely on a certain response
    ]
    con.post = Mock(side_effect=post_responses)
    project_client = ProjectClientStub(con, "1234", None)
    xmlupload._handle_upload_error = Mock()
    clients = dsp_tools.commands.xmlupload.models.upload_clients.UploadClients(
        ingest_client_mock, project_client, ListClientMock()
    )

    xmlupload._upload_resources(clients, upload_state)
    assert caplog.records[1].message == "Created resource 1/5: 'foo_1_label' (ID: 'foo_1_id', IRI: 'foo_1_iri')"
    assert caplog.records[3].message == "Created resource 2/5: 'foo_2_label' (ID: 'foo_2_id', IRI: 'foo_2_iri')"
    caplog.clear()

    xmlupload._upload_resources(clients, upload_state)
    assert caplog.records[1].message == "Created resource 3/5: 'foo_3_label' (ID: 'foo_3_id', IRI: 'foo_3_iri')"
    assert caplog.records[3].message == "Created resource 4/5: 'foo_4_label' (ID: 'foo_4_id', IRI: 'foo_4_iri')"
    caplog.clear()

    xmlupload._upload_resources(clients, upload_state)
    assert caplog.records[1].message == "Created resource 5/5: 'foo_5_label' (ID: 'foo_5_id', IRI: 'foo_5_iri')"
    assert caplog.records[3].message == "  Upload resptrs of resource 'foo_1_id'..."
    assert caplog.records[5].message == "  Upload resptrs of resource 'foo_2_id'..."
    caplog.clear()


def test_post_requests(ingest_client_mock: AssetClient) -> None:
    xml_strings = [
        '<resource label="foo_1_label" restype=":foo_1_type" id="foo_1_id"></resource>',
        '<resource label="foo_2_label" restype=":foo_2_type" id="foo_2_id"></resource>',
        '<resource label="foo_3_label" restype=":foo_3_type" id="foo_3_id"></resource>',
        '<resource label="foo_4_label" restype=":foo_4_type" id="foo_4_id"></resource>',
        '<resource label="foo_5_label" restype=":foo_5_type" id="foo_5_id"></resource>',
        '<resource label="foo_6_label" restype=":foo_6_type" id="foo_6_id"></resource>',
    ]
    xml_resources = [XMLResource.from_node(etree.fromstring(xml_str), "my_onto") for xml_str in xml_strings]
    link_val_stash_dict = {
        "foo_1_id": [LinkValueStashItem("foo_1_id", "my_onto:foo_1_type", "my_onto:hasCustomLink", "foo_2_id")],
        "foo_2_id": [LinkValueStashItem("foo_2_id", "my_onto:foo_2_type", "my_onto:hasCustomLink", "foo_1_id")],
    }
    stash = Stash(link_value_stash=LinkValueStash(link_val_stash_dict), standoff_stash=None)
    upload_config = UploadConfig(interrupt_after=2)
    upload_state = UploadState(xml_resources.copy(), deepcopy(stash), upload_config, {})
    con = Mock(spec_set=ConnectionLive)
    post_responses = [
        {"@id": "foo_1_iri", "rdfs:label": "foo_1_label"},
        {"@id": "foo_2_iri", "rdfs:label": "foo_2_label"},
        {"@id": "foo_3_iri", "rdfs:label": "foo_3_label"},
        {"@id": "foo_4_iri", "rdfs:label": "foo_4_label"},
        {"@id": "foo_5_iri", "rdfs:label": "foo_5_label"},
        {"@id": "foo_6_iri", "rdfs:label": "foo_6_label"},
        {},  # uploading a stash doesn't rely on a certain response
        {},  # uploading a stash doesn't rely on a certain response
    ]
    con.post = Mock(side_effect=post_responses)
    project_client = ProjectClientStub(con, "1234", None)
    xmlupload._handle_upload_error = Mock()
    clients = dsp_tools.commands.xmlupload.models.upload_clients.UploadClients(
        ingest_client_mock, project_client, ListClientMock()
    )

    xmlupload._upload_resources(clients, upload_state)
    xmlupload._upload_resources(clients, upload_state)
    xmlupload._upload_resources(clients, upload_state)
    xmlupload._upload_resources(clients, upload_state)
    assert len(con.post.call_args_list) == len(post_responses)


def test_interruption_if_resource_cannot_be_created_because_of_404() -> None:
    xml_strings = [
        '<resource label="foo_1_label" restype=":foo_1_type" id="foo_1_id"></resource>',
        '<resource label="foo_2_label" restype=":foo_2_type" id="foo_2_id"></resource>',
    ]
    xml_resources = [XMLResource.from_node(etree.fromstring(xml_str), "my_onto") for xml_str in xml_strings]
    upload_state = UploadState(xml_resources.copy(), Stash(None, None), UploadConfig(), {}, [], IriResolver())
    con = ConnectionLive("foo")
    con._log_request = Mock()  # type: ignore[method-assign]
    con._log_response = Mock()  # type: ignore[method-assign]
    resp_404 = Response()
    resp_404.status_code = 404
    post_responses = [resp_404]
    con.session.request = Mock(side_effect=post_responses)  # type: ignore[method-assign]
    project_client = ProjectClientStub(con, "1234", None)
    xmlupload._handle_upload_error = Mock()
    ingest_client = DspIngestClientLive("", AuthenticationClientMockBase(), "1234", ".")

    xmlupload._upload_resources(UploadClients(ingest_client, project_client, ListClientMock()), upload_state)
    msg = (
        "Lost connection to DSP server, probably because the server is down. "
        "Please continue later with 'resume-xmlupload'. Reason for this failure: "
        "Permanently unable to execute the network action. "
    )
    assert len(xmlupload._handle_upload_error.call_args_list) == 1
    err_actual: XmlUploadInterruptedError = xmlupload._handle_upload_error.call_args_list[0].args[0]
    upload_state_actual: UploadState = xmlupload._handle_upload_error.call_args_list[0].args[1]
    assert msg in err_actual.message
    assert upload_state_actual == upload_state
