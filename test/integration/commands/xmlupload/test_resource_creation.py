# mypy: disable-error-code="method-assign,no-untyped-def"

from copy import deepcopy
from dataclasses import dataclass
from typing import Any
from typing import cast
from unittest.mock import Mock
from unittest.mock import patch
from uuid import uuid4

import pytest
from requests import Response

from dsp_tools.clients.connection import Connection
from dsp_tools.clients.connection_live import ConnectionLive
from dsp_tools.clients.legal_info_client import LegalInfoClient
from dsp_tools.commands.xmlupload.iri_resolver import IriResolver
from dsp_tools.commands.xmlupload.models.ingest import AssetClient
from dsp_tools.commands.xmlupload.models.ingest import DspIngestClientLive
from dsp_tools.commands.xmlupload.models.processed.res import ProcessedResource
from dsp_tools.commands.xmlupload.models.processed.values import ProcessedLink
from dsp_tools.commands.xmlupload.models.processed.values import ProcessedSimpleText
from dsp_tools.commands.xmlupload.models.upload_clients import UploadClients
from dsp_tools.commands.xmlupload.models.upload_state import UploadState
from dsp_tools.commands.xmlupload.project_client import ProjectInfo
from dsp_tools.commands.xmlupload.stash.stash_models import LinkValueStash
from dsp_tools.commands.xmlupload.stash.stash_models import LinkValueStashItem
from dsp_tools.commands.xmlupload.stash.stash_models import Stash
from dsp_tools.commands.xmlupload.upload_config import UploadConfig
from dsp_tools.commands.xmlupload.xmlupload import _upload_resources
from dsp_tools.error.custom_warnings import DspToolsUserWarning
from dsp_tools.error.exceptions import PermanentTimeOutError
from dsp_tools.error.exceptions import XmlUploadInterruptedError
from test.integration.commands.xmlupload.authentication_client_mock import AuthenticationClientMockBase

RDFS_LABEL = "http://www.w3.org/2000/01/rdf-schema#label"

ONTO = "http://0.0.0.0:3333/ontology/9999/onto/v2#"

LINK_PROP = f"{ONTO}hasCustomLink"
TEXT_PROP = f"{ONTO}hasText"

RES_IRI_NAMESPACE_STR = "http://rdfh.ch/0000/"


@pytest.fixture
def link_val_stash_lookup_two_items() -> dict[str, list[LinkValueStashItem]]:
    return {
        "foo_1_id": [
            LinkValueStashItem(
                "foo_1_id", f"{ONTO}foo_1_type", ProcessedLink("foo_2_id", LINK_PROP, None, None, str(uuid4()))
            )
        ],
        "foo_2_id": [
            LinkValueStashItem(
                "foo_2_id", f"{ONTO}foo_2_type", ProcessedLink("foo_1_id", LINK_PROP, None, None, str(uuid4()))
            )
        ],
    }


@pytest.fixture
def ingest_client_mock():
    return Mock(spec_set=AssetClient)


@pytest.fixture
def legal_info_client_mock():
    return Mock(spec_set=LegalInfoClient)


class ListClientMock:
    def get_list_node_id_to_iri_lookup(self) -> dict[tuple[str, str], str]:
        return dict()


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
        return {"my_onto": "http://0.0.0.0:3333/ontology/9999/onto/v2"}

    def get_ontology_iri_dict(self) -> dict[str, str]:
        raise NotImplementedError("get_project_iri not implemented")


def test_one_resource_without_links(ingest_client_mock: AssetClient, legal_info_client_mock: LegalInfoClient) -> None:
    resources = [
        ProcessedResource(
            "foo_1_id",
            f"{ONTO}foo_1_type",
            "foo_1_label",
            None,
            [ProcessedSimpleText("foo_1 text", TEXT_PROP, None, None)],
        )
    ]
    upload_state = UploadState(resources, None, UploadConfig())
    con = Mock(spec_set=ConnectionLive)
    post_responses = [{"@id": f"{RES_IRI_NAMESPACE_STR}foo_1_iri", RDFS_LABEL: "foo_1_label"}]
    con.post = Mock(side_effect=post_responses)
    project_client = ProjectClientStub(con, "1234", None)

    clients = UploadClients(ingest_client_mock, project_client, ListClientMock(), legal_info_client_mock)
    _upload_resources(clients, upload_state)

    assert len(con.post.call_args_list) == len(post_responses)
    post_call_args = cast(dict[str, Any], con.post.call_args_list[0].kwargs)
    assert len(post_call_args) == 3
    expected = {
        "route": "/v2/resources",
        "data": {
            "@type": "http://0.0.0.0:3333/ontology/9999/onto/v2#foo_1_type",
            "http://www.w3.org/2000/01/rdf-schema#label": {
                "@type": "http://www.w3.org/2001/XMLSchema#string",
                "@value": "foo_1_label",
            },
            "http://api.knora.org/ontology/knora-api/v2#attachedToProject": {
                "@id": "https://admin.test.dasch.swiss/project/MsOaiQkcQ7-QPxsYBKckfQ"
            },
            "@context": {},
            TEXT_PROP: {
                "@type": "http://api.knora.org/ontology/knora-api/v2#TextValue",
                "http://api.knora.org/ontology/knora-api/v2#valueAsString": {
                    "@type": "http://www.w3.org/2001/XMLSchema#string",
                    "@value": "foo_1 text",
                },
            },
        },
    }
    assert post_call_args["route"] == expected["route"]
    assert not post_call_args["headers"]
    assert post_call_args["data"][TEXT_PROP] == expected["data"][TEXT_PROP]  # type: ignore[index]
    expected_project = expected["data"]["http://api.knora.org/ontology/knora-api/v2#attachedToProject"]  # type: ignore[index]
    assert post_call_args["data"]["http://api.knora.org/ontology/knora-api/v2#attachedToProject"] == expected_project
    expected_label = expected["data"]["http://www.w3.org/2000/01/rdf-schema#label"]  # type: ignore[index]
    assert post_call_args["data"]["http://www.w3.org/2000/01/rdf-schema#label"] == expected_label
    assert post_call_args["data"]["@type"] == expected["data"]["@type"]  # type: ignore[index]
    assert not upload_state.pending_resources
    assert not upload_state.failed_uploads
    assert upload_state.iri_resolver.lookup == {"foo_1_id": f"{RES_IRI_NAMESPACE_STR}foo_1_iri"}
    assert not upload_state.pending_stash


def test_one_resource_with_link_to_existing_resource(
    ingest_client_mock: AssetClient, legal_info_client_mock: LegalInfoClient
) -> None:
    resources = [
        ProcessedResource(
            "foo_1_id",
            f"{ONTO}foo_1_type",
            "foo_1_label",
            None,
            [ProcessedLink("foo_2_id", LINK_PROP, None, None, str(uuid4()))],
        )
    ]
    upload_state = UploadState(
        resources,
        None,
        UploadConfig(),
        [],
        IriResolver({"foo_2_id": f"{RES_IRI_NAMESPACE_STR}foo_2_iri"}),
    )
    con = Mock(spec_set=ConnectionLive)
    post_responses = [{"@id": f"{RES_IRI_NAMESPACE_STR}foo_1_iri", RDFS_LABEL: "foo_1_label"}]
    con.post = Mock(side_effect=post_responses)
    project_client = ProjectClientStub(con, "1234", None)
    clients = UploadClients(ingest_client_mock, project_client, ListClientMock(), legal_info_client_mock)
    _upload_resources(clients, upload_state)

    assert len(con.post.call_args_list) == len(post_responses)
    post_call_args = cast(dict[str, Any], con.post.call_args_list[0].kwargs)
    assert len(post_call_args) == 3
    prop_name = f"{LINK_PROP}Value"
    expected = {
        "route": "/v2/resources",
        "data": {
            "@type": "http://0.0.0.0:3333/ontology/9999/onto/v2#foo_1_type",
            "http://www.w3.org/2000/01/rdf-schema#label": {
                "@type": "http://www.w3.org/2001/XMLSchema#string",
                "@value": "foo_1_label",
            },
            "http://api.knora.org/ontology/knora-api/v2#attachedToProject": {
                "@id": "https://admin.test.dasch.swiss/project/MsOaiQkcQ7-QPxsYBKckfQ"
            },
            "@context": {},
            prop_name: {
                "@type": "http://api.knora.org/ontology/knora-api/v2#LinkValue",
                "http://api.knora.org/ontology/knora-api/v2#linkValueHasTargetIri": {
                    "@id": f"{RES_IRI_NAMESPACE_STR}foo_2_iri"
                },
            },
        },
    }
    assert post_call_args["route"] == expected["route"]
    assert not post_call_args["headers"]
    assert post_call_args["data"][prop_name] == expected["data"][prop_name]  # type: ignore[index]
    expected_project = expected["data"]["http://api.knora.org/ontology/knora-api/v2#attachedToProject"]  # type: ignore[index]
    assert post_call_args["data"]["http://api.knora.org/ontology/knora-api/v2#attachedToProject"] == expected_project
    expected_label = expected["data"]["http://www.w3.org/2000/01/rdf-schema#label"]  # type: ignore[index]
    assert post_call_args["data"]["http://www.w3.org/2000/01/rdf-schema#label"] == expected_label
    assert post_call_args["data"]["@type"] == expected["data"]["@type"]  # type: ignore[index]
    assert not upload_state.pending_resources
    assert not upload_state.failed_uploads
    assert upload_state.iri_resolver.lookup == {
        "foo_1_id": f"{RES_IRI_NAMESPACE_STR}foo_1_iri",
        "foo_2_id": f"{RES_IRI_NAMESPACE_STR}foo_2_iri",
    }
    assert not upload_state.pending_stash


def test_2_resources_with_stash_interrupted_by_timeout(
    link_val_stash_lookup_two_items, ingest_client_mock: AssetClient, legal_info_client_mock: LegalInfoClient
) -> None:
    _2_resources_with_stash_interrupted_by_error(
        link_val_stash_lookup_two_items,
        PermanentTimeOutError(""),
        "PermanentTimeOutError",
        ingest_client_mock,
        legal_info_client_mock,
    )


def test_2_resources_with_stash_interrupted_by_keyboard(
    link_val_stash_lookup_two_items, ingest_client_mock: AssetClient, legal_info_client_mock: LegalInfoClient
) -> None:
    _2_resources_with_stash_interrupted_by_error(
        link_val_stash_lookup_two_items,
        KeyboardInterrupt(),
        "KeyboardInterrupt",
        ingest_client_mock,
        legal_info_client_mock,
    )


def _2_resources_with_stash_interrupted_by_error(
    link_val_stash_lookup_two_items,
    err_to_interrupt_with: BaseException,
    err_as_str: str,
    ingest_client_mock: AssetClient,
    legal_info_client_mock: LegalInfoClient,
) -> None:
    resources = [
        ProcessedResource(f"foo_{i}_id", f"{ONTO}foo_{i}_type", f"foo_{i}_label", None, []) for i in range(1, 3)
    ]
    stash = Stash(link_value_stash=LinkValueStash(link_val_stash_lookup_two_items), standoff_stash=None)
    upload_state = UploadState(resources.copy(), deepcopy(stash), UploadConfig())
    con = Mock(spec_set=ConnectionLive)
    post_responses = [
        {"@id": f"{RES_IRI_NAMESPACE_STR}foo_1_iri", RDFS_LABEL: "foo_1_label"},
        err_to_interrupt_with,
    ]
    con.post = Mock(side_effect=post_responses)
    project_client = ProjectClientStub(con, "1234", None)
    clients = UploadClients(ingest_client_mock, project_client, ListClientMock(), legal_info_client_mock)

    with patch("dsp_tools.commands.xmlupload.xmlupload._handle_upload_error") as _handle_upload_error:
        with pytest.warns(DspToolsUserWarning):
            _upload_resources(clients, upload_state)

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
            resources[1:],
            stash,
            UploadConfig(),
            [],
            IriResolver({"foo_1_id": f"{RES_IRI_NAMESPACE_STR}foo_1_iri"}),
        )
        _handle_upload_error.assert_called_once_with(XmlUploadInterruptedError(err_msg), upload_state_expected)


def test_2_resources_with_stash(
    link_val_stash_lookup_two_items, ingest_client_mock: AssetClient, legal_info_client_mock: LegalInfoClient
) -> None:
    resources = [
        ProcessedResource(f"foo_{i}_id", f"{ONTO}foo_{i}_type", f"foo_{i}_label", None, []) for i in range(1, 3)
    ]
    stash = Stash(link_value_stash=LinkValueStash(link_val_stash_lookup_two_items), standoff_stash=None)
    upload_state = UploadState(resources.copy(), deepcopy(stash), UploadConfig())
    con = Mock(spec_set=ConnectionLive)
    post_responses = [
        {"@id": f"{RES_IRI_NAMESPACE_STR}foo_1_iri", RDFS_LABEL: "foo_1_label"},
        {"@id": f"{RES_IRI_NAMESPACE_STR}foo_2_iri", RDFS_LABEL: "foo_2_label"},
        {},  # uploading a stash doesn't rely on a certain response
        {},  # uploading a stash doesn't rely on a certain response
    ]
    con.post = Mock(side_effect=post_responses)
    project_client = ProjectClientStub(con, "1234", None)
    clients = UploadClients(ingest_client_mock, project_client, ListClientMock(), legal_info_client_mock)

    _upload_resources(clients, upload_state)

    assert len(con.post.call_args_list) == len(post_responses)
    post_kwargs = con.post.call_args_list[2].kwargs
    match post_kwargs:
        case {
            "route": "/v2/values",
            "data": {
                "@id": "http://rdfh.ch/0000/foo_1_iri",
                "@type": "http://0.0.0.0:3333/ontology/9999/onto/v2#foo_1_type",
                "http://0.0.0.0:3333/ontology/9999/onto/v2#hasCustomLinkValue": {
                    "@type": "http://api.knora.org/ontology/knora-api/v2#LinkValue",
                    "http://api.knora.org/ontology/knora-api/v2#linkValueHasTargetIri": {
                        "@id": "http://rdfh.ch/0000/foo_2_iri"
                    },
                },
            },
        }:
            assert True
        case _:
            pytest.fail("POST request was not sent correctly")
    assert not upload_state.pending_resources
    assert not upload_state.failed_uploads
    assert upload_state.iri_resolver.lookup == {
        "foo_1_id": f"{RES_IRI_NAMESPACE_STR}foo_1_iri",
        "foo_2_id": f"{RES_IRI_NAMESPACE_STR}foo_2_iri",
    }
    assert not upload_state.pending_stash or upload_state.pending_stash.is_empty()


def test_5_resources_with_stash_and_interrupt_after_2(
    link_val_stash_lookup_two_items, ingest_client_mock: AssetClient, legal_info_client_mock: LegalInfoClient
) -> None:
    resources = [
        ProcessedResource(f"foo_{i}_id", f"{ONTO}foo_{i}_type", f"foo_{i}_label", None, []) for i in range(1, 6)
    ]
    stash = Stash(link_value_stash=LinkValueStash(link_val_stash_lookup_two_items), standoff_stash=None)
    upload_config = UploadConfig(interrupt_after=2)
    upload_state = UploadState(resources.copy(), deepcopy(stash), upload_config)
    con = Mock(spec_set=ConnectionLive)
    post_responses = [
        {"@id": f"{RES_IRI_NAMESPACE_STR}foo_1_iri", RDFS_LABEL: "foo_1_label"},
        {"@id": f"{RES_IRI_NAMESPACE_STR}foo_2_iri", RDFS_LABEL: "foo_2_label"},
        {"@id": f"{RES_IRI_NAMESPACE_STR}foo_3_iri", RDFS_LABEL: "foo_3_label"},
        {"@id": f"{RES_IRI_NAMESPACE_STR}foo_4_iri", RDFS_LABEL: "foo_4_label"},
        {"@id": f"{RES_IRI_NAMESPACE_STR}foo_5_iri", RDFS_LABEL: "foo_5_label"},
        {},  # uploading a stash doesn't rely on a certain response
        {},  # uploading a stash doesn't rely on a certain response
    ]
    con.post = Mock(side_effect=post_responses)
    project_client = ProjectClientStub(con, "1234", None)
    err_msg = "Interrupted: Maximum number of resources was reached (2)"
    client = UploadClients(ingest_client_mock, project_client, ListClientMock(), legal_info_client_mock)

    with patch("dsp_tools.commands.xmlupload.xmlupload._handle_upload_error") as _handle_upload_error:
        _upload_resources(client, upload_state)
        iri_resolver_expected = IriResolver(
            {"foo_1_id": f"{RES_IRI_NAMESPACE_STR}foo_1_iri", "foo_2_id": f"{RES_IRI_NAMESPACE_STR}foo_2_iri"}
        )
        upload_state_expected = UploadState(resources[2:], stash, upload_config, [], iri_resolver_expected)
        _handle_upload_error.assert_called_once_with(XmlUploadInterruptedError(err_msg), upload_state_expected)

    with patch("dsp_tools.commands.xmlupload.xmlupload._handle_upload_error") as _handle_upload_error:
        _upload_resources(client, upload_state)
        iri_resolver_expected.lookup.update(
            {"foo_3_id": f"{RES_IRI_NAMESPACE_STR}foo_3_iri", "foo_4_id": f"{RES_IRI_NAMESPACE_STR}foo_4_iri"}
        )
        upload_state_expected = UploadState(resources[4:], stash, upload_config, [], iri_resolver_expected)
        _handle_upload_error.assert_called_once_with(XmlUploadInterruptedError(err_msg), upload_state_expected)

    with patch("dsp_tools.commands.xmlupload.xmlupload._handle_upload_error") as _handle_upload_error:
        _upload_resources(client, upload_state)
        iri_resolver_expected.lookup.update({"foo_5_id": f"{RES_IRI_NAMESPACE_STR}foo_5_iri"})
        empty_stash = Stash(standoff_stash=None, link_value_stash=LinkValueStash({}))
        upload_state_expected = UploadState([], empty_stash, upload_config, [], iri_resolver_expected)
        _handle_upload_error.assert_not_called()
        assert upload_state == upload_state_expected


def test_6_resources_with_stash_and_interrupt_after_2(
    link_val_stash_lookup_two_items, ingest_client_mock: AssetClient, legal_info_client_mock: LegalInfoClient
) -> None:
    resources = [
        ProcessedResource(f"foo_{i}_id", f"{ONTO}foo_{i}_type", f"foo_{i}_label", None, []) for i in range(1, 7)
    ]
    stash = Stash(link_value_stash=LinkValueStash(link_val_stash_lookup_two_items), standoff_stash=None)
    upload_config = UploadConfig(interrupt_after=2)
    upload_state = UploadState(resources.copy(), deepcopy(stash), upload_config)
    con = Mock(spec_set=ConnectionLive)
    post_responses = [
        {"@id": f"{RES_IRI_NAMESPACE_STR}foo_1_iri", RDFS_LABEL: "foo_1_label"},
        {"@id": f"{RES_IRI_NAMESPACE_STR}foo_2_iri", RDFS_LABEL: "foo_2_label"},
        {"@id": f"{RES_IRI_NAMESPACE_STR}foo_3_iri", RDFS_LABEL: "foo_3_label"},
        {"@id": f"{RES_IRI_NAMESPACE_STR}foo_4_iri", RDFS_LABEL: "foo_4_label"},
        {"@id": f"{RES_IRI_NAMESPACE_STR}foo_5_iri", RDFS_LABEL: "foo_5_label"},
        {"@id": f"{RES_IRI_NAMESPACE_STR}foo_6_iri", RDFS_LABEL: "foo_6_label"},
        {},  # uploading a stash doesn't rely on a certain response
        {},  # uploading a stash doesn't rely on a certain response
    ]
    con.post = Mock(side_effect=post_responses)
    project_client = ProjectClientStub(con, "1234", None)
    err_msg = "Interrupted: Maximum number of resources was reached (2)"
    client = UploadClients(ingest_client_mock, project_client, ListClientMock(), legal_info_client_mock)

    with patch("dsp_tools.commands.xmlupload.xmlupload._handle_upload_error") as _handle_upload_error:
        _upload_resources(client, upload_state)
        iri_resolver_expected = IriResolver(
            {"foo_1_id": f"{RES_IRI_NAMESPACE_STR}foo_1_iri", "foo_2_id": f"{RES_IRI_NAMESPACE_STR}foo_2_iri"}
        )
        upload_state_expected = UploadState(resources[2:], stash, upload_config, [], iri_resolver_expected)
        _handle_upload_error.assert_called_once_with(XmlUploadInterruptedError(err_msg), upload_state_expected)

    with patch("dsp_tools.commands.xmlupload.xmlupload._handle_upload_error") as _handle_upload_error:
        _upload_resources(client, upload_state)
        iri_resolver_expected.lookup.update(
            {"foo_3_id": f"{RES_IRI_NAMESPACE_STR}foo_3_iri", "foo_4_id": f"{RES_IRI_NAMESPACE_STR}foo_4_iri"}
        )
        upload_state_expected = UploadState(resources[4:], stash, upload_config, [], iri_resolver_expected)
        _handle_upload_error.assert_called_once_with(XmlUploadInterruptedError(err_msg), upload_state_expected)

    with patch("dsp_tools.commands.xmlupload.xmlupload._handle_upload_error") as _handle_upload_error:
        _upload_resources(client, upload_state)
        iri_resolver_expected.lookup.update(
            {"foo_5_id": f"{RES_IRI_NAMESPACE_STR}foo_5_iri", "foo_6_id": f"{RES_IRI_NAMESPACE_STR}foo_6_iri"}
        )
        upload_state_expected = UploadState([], stash, upload_config, [], iri_resolver_expected)
        _handle_upload_error.assert_called_once_with(XmlUploadInterruptedError(err_msg), upload_state_expected)

    with patch("dsp_tools.commands.xmlupload.xmlupload._handle_upload_error") as _handle_upload_error:
        _upload_resources(client, upload_state)
        empty_stash = Stash(standoff_stash=None, link_value_stash=LinkValueStash({}))
        upload_state_expected = UploadState([], empty_stash, upload_config, [], iri_resolver_expected)
        _handle_upload_error.assert_not_called()
        assert upload_state == upload_state_expected


def test_logging(
    link_val_stash_lookup_two_items,
    caplog: pytest.LogCaptureFixture,
    ingest_client_mock: AssetClient,
    legal_info_client_mock: LegalInfoClient,
) -> None:
    resources = [
        ProcessedResource(f"foo_{i}_id", f"{ONTO}foo_{i}_type", f"foo_{i}_label", None, []) for i in range(1, 6)
    ]
    stash = Stash(link_value_stash=LinkValueStash(link_val_stash_lookup_two_items), standoff_stash=None)
    upload_config = UploadConfig(interrupt_after=2)
    upload_state = UploadState(resources.copy(), deepcopy(stash), upload_config)
    con = Mock(spec_set=ConnectionLive)
    post_responses = [
        {"@id": f"{RES_IRI_NAMESPACE_STR}foo_1_iri", RDFS_LABEL: "foo_1_label"},
        {"@id": f"{RES_IRI_NAMESPACE_STR}foo_2_iri", RDFS_LABEL: "foo_2_label"},
        {"@id": f"{RES_IRI_NAMESPACE_STR}foo_3_iri", RDFS_LABEL: "foo_3_label"},
        {"@id": f"{RES_IRI_NAMESPACE_STR}foo_4_iri", RDFS_LABEL: "foo_4_label"},
        {"@id": f"{RES_IRI_NAMESPACE_STR}foo_5_iri", RDFS_LABEL: "foo_5_label"},
        {},  # uploading a stash doesn't rely on a certain response
        {},  # uploading a stash doesn't rely on a certain response
    ]
    con.post = Mock(side_effect=post_responses)
    project_client = ProjectClientStub(con, "1234", None)
    clients = UploadClients(ingest_client_mock, project_client, ListClientMock(), legal_info_client_mock)

    with patch("dsp_tools.commands.xmlupload.xmlupload._handle_upload_error"):
        _upload_resources(clients, upload_state)
        assert (
            caplog.records[1].message
            == f"Created resource 1/5: 'foo_1_label' (ID: 'foo_1_id', IRI: '{RES_IRI_NAMESPACE_STR}foo_1_iri')"
        )
        assert (
            caplog.records[3].message
            == f"Created resource 2/5: 'foo_2_label' (ID: 'foo_2_id', IRI: '{RES_IRI_NAMESPACE_STR}foo_2_iri')"
        )
        caplog.clear()

        _upload_resources(clients, upload_state)
        assert (
            caplog.records[1].message
            == f"Created resource 3/5: 'foo_3_label' (ID: 'foo_3_id', IRI: '{RES_IRI_NAMESPACE_STR}foo_3_iri')"
        )
        assert (
            caplog.records[3].message
            == f"Created resource 4/5: 'foo_4_label' (ID: 'foo_4_id', IRI: '{RES_IRI_NAMESPACE_STR}foo_4_iri')"
        )
        caplog.clear()

        _upload_resources(clients, upload_state)
        assert (
            caplog.records[1].message
            == f"Created resource 5/5: 'foo_5_label' (ID: 'foo_5_id', IRI: '{RES_IRI_NAMESPACE_STR}foo_5_iri')"
        )
        assert caplog.records[3].message == "  Upload resptrs of resource 'foo_1_id'..."
        assert caplog.records[5].message == "  Upload resptrs of resource 'foo_2_id'..."
        caplog.clear()


def test_post_requests(
    link_val_stash_lookup_two_items, ingest_client_mock: AssetClient, legal_info_client_mock: LegalInfoClient
) -> None:
    resources = [
        ProcessedResource(f"foo_{i}_id", f"{ONTO}foo_{i}_type", f"foo_{i}_label", None, []) for i in range(1, 7)
    ]
    stash = Stash(link_value_stash=LinkValueStash(link_val_stash_lookup_two_items), standoff_stash=None)
    upload_config = UploadConfig(interrupt_after=2)
    upload_state = UploadState(resources.copy(), deepcopy(stash), upload_config)
    con = Mock(spec_set=ConnectionLive)
    post_responses = [
        {"@id": f"{RES_IRI_NAMESPACE_STR}foo_1_iri", RDFS_LABEL: "foo_1_label"},
        {"@id": f"{RES_IRI_NAMESPACE_STR}foo_2_iri", RDFS_LABEL: "foo_2_label"},
        {"@id": f"{RES_IRI_NAMESPACE_STR}foo_3_iri", RDFS_LABEL: "foo_3_label"},
        {"@id": f"{RES_IRI_NAMESPACE_STR}foo_4_iri", RDFS_LABEL: "foo_4_label"},
        {"@id": f"{RES_IRI_NAMESPACE_STR}foo_5_iri", RDFS_LABEL: "foo_5_label"},
        {"@id": f"{RES_IRI_NAMESPACE_STR}foo_6_iri", RDFS_LABEL: "foo_6_label"},
        {},  # uploading a stash doesn't rely on a certain response
        {},  # uploading a stash doesn't rely on a certain response
    ]
    con.post = Mock(side_effect=post_responses)
    project_client = ProjectClientStub(con, "1234", None)
    clients = UploadClients(ingest_client_mock, project_client, ListClientMock(), legal_info_client_mock)

    with patch("dsp_tools.commands.xmlupload.xmlupload._handle_upload_error"):
        _upload_resources(clients, upload_state)
        _upload_resources(clients, upload_state)
        _upload_resources(clients, upload_state)
        _upload_resources(clients, upload_state)
        assert len(con.post.call_args_list) == len(post_responses)


def test_interruption_if_resource_cannot_be_created_because_of_404(legal_info_client_mock: LegalInfoClient) -> None:
    resources = [
        ProcessedResource(f"foo_{i}_id", f"{ONTO}foo_{i}_type", f"foo_{i}_label", None, []) for i in range(1, 3)
    ]
    upload_state = UploadState(resources.copy(), Stash(None, None), UploadConfig(), [], IriResolver())
    con = ConnectionLive("foo")
    resp_404 = Response()
    resp_404.status_code = 404
    post_responses = [resp_404]
    con.session.request = Mock(side_effect=post_responses)
    project_client = ProjectClientStub(con, "1234", None)
    ingest_client = DspIngestClientLive("", AuthenticationClientMockBase(), "1234", ".")

    with patch("dsp_tools.commands.xmlupload.xmlupload._handle_upload_error") as _handle_upload_error:
        _upload_resources(
            UploadClients(ingest_client, project_client, ListClientMock(), legal_info_client_mock), upload_state
        )
        msg = (
            "Lost connection to DSP server, probably because the server is down. "
            "Please continue later with 'resume-xmlupload'. Reason for this failure: "
            "Permanently unable to execute the network action."
        )
        assert len(_handle_upload_error.call_args_list) == 1
        err_actual: XmlUploadInterruptedError = _handle_upload_error.call_args_list[0].args[0]
        upload_state_actual: UploadState = _handle_upload_error.call_args_list[0].args[1]
        assert msg in err_actual.message
        assert upload_state_actual == upload_state
