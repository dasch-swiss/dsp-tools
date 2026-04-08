from copy import deepcopy
from unittest.mock import Mock
from unittest.mock import patch
from uuid import uuid4

import pytest

from dsp_tools.clients.connection_live import ConnectionLive
from dsp_tools.clients.ingest import AssetClient
from dsp_tools.clients.legal_info_client import LegalInfoClient
from dsp_tools.clients.list_client import ListGetClient
from dsp_tools.clients.resource_client_live import ResourceClientLive
from dsp_tools.commands.xmlupload.exceptions import XmlUploadInterruptedError
from dsp_tools.commands.xmlupload.execute_upload import _upload_all_resources
from dsp_tools.commands.xmlupload.iri_resolver import IriResolver
from dsp_tools.commands.xmlupload.models.processed.res import ProcessedResource
from dsp_tools.commands.xmlupload.models.processed.values import ProcessedLink
from dsp_tools.commands.xmlupload.models.processed.values import ProcessedSimpleText
from dsp_tools.commands.xmlupload.models.upload_clients import UploadClients
from dsp_tools.commands.xmlupload.models.upload_state import UploadState
from dsp_tools.commands.xmlupload.stash.stash_models import LinkValueStash
from dsp_tools.commands.xmlupload.stash.stash_models import LinkValueStashItem
from dsp_tools.commands.xmlupload.stash.stash_models import Stash
from dsp_tools.commands.xmlupload.upload_config import UploadConfig
from dsp_tools.error.custom_warnings import DspToolsUserWarning
from dsp_tools.utils.request_utils import ResponseCodeAndText
from test.integration.commands.xmlupload.legal_info_client_mock import LegalInfoClientMockBase

ONTO = "http://0.0.0.0:3333/ontology/9999/onto/v2#"
PROJECT_IRI = "https://admin.test.dasch.swiss/project/MsOaiQkcQ7-QPxsYBKckfQ"
RDFS_LABEL = "http://www.w3.org/2000/01/rdf-schema#label"

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
    return LegalInfoClientMockBase()


@pytest.fixture
def list_client_mock():
    return Mock(spec_set=ListGetClient)


@patch("dsp_tools.commands.xmlupload.execute_upload.ProjectClientLive")
@patch("dsp_tools.commands.xmlupload.execute_upload.ResourceClientLive")
def test_one_resource_without_links(
    mock_resource_client_class: Mock,
    mock_project_client_class: Mock,
    ingest_client_mock: AssetClient,
    legal_info_client_mock: LegalInfoClient,
    list_client_mock,
) -> None:
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
    mock_resource_client = Mock(spec_set=ResourceClientLive)
    mock_resource_client.post_resource = Mock(side_effect=[f"{RES_IRI_NAMESPACE_STR}foo_1_iri"])
    mock_resource_client_class.return_value = mock_resource_client

    mock_project_client = Mock()
    mock_project_client.get_project_iri.return_value = PROJECT_IRI
    mock_project_client_class.return_value = mock_project_client

    clients = UploadClients(ingest_client_mock, list_client_mock, legal_info_client_mock)
    _upload_all_resources(clients, upload_state)

    assert mock_resource_client.post_resource.call_count == 1
    resource_json = mock_resource_client.post_resource.call_args[0][0]
    expected = {
        "@type": "http://0.0.0.0:3333/ontology/9999/onto/v2#foo_1_type",
        RDFS_LABEL: {
            "@type": "http://www.w3.org/2001/XMLSchema#string",
            "@value": "foo_1_label",
        },
        "http://api.knora.org/ontology/knora-api/v2#attachedToProject": {"@id": PROJECT_IRI},
        "@context": {},
        TEXT_PROP: {
            "@type": "http://api.knora.org/ontology/knora-api/v2#TextValue",
            "http://api.knora.org/ontology/knora-api/v2#valueAsString": {
                "@type": "http://www.w3.org/2001/XMLSchema#string",
                "@value": "foo_1 text",
            },
        },
    }
    assert resource_json[TEXT_PROP] == expected[TEXT_PROP]
    expected_project = expected["http://api.knora.org/ontology/knora-api/v2#attachedToProject"]
    assert resource_json["http://api.knora.org/ontology/knora-api/v2#attachedToProject"] == expected_project
    expected_label = expected[RDFS_LABEL]
    assert resource_json[RDFS_LABEL] == expected_label
    assert resource_json["@type"] == expected["@type"]
    assert not upload_state.pending_resources
    assert not upload_state.failed_uploads
    assert upload_state.iri_resolver.lookup == {"foo_1_id": f"{RES_IRI_NAMESPACE_STR}foo_1_iri"}
    assert not upload_state.pending_stash


@patch("dsp_tools.commands.xmlupload.execute_upload.ProjectClientLive")
@patch("dsp_tools.commands.xmlupload.execute_upload.ResourceClientLive")
def test_one_resource_with_link_to_existing_resource(
    mock_resource_client_class: Mock,
    mock_project_client_class: Mock,
    ingest_client_mock: AssetClient,
    legal_info_client_mock: LegalInfoClient,
    list_client_mock,
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
    mock_resource_client = Mock(spec_set=ResourceClientLive)
    mock_resource_client.post_resource = Mock(side_effect=[f"{RES_IRI_NAMESPACE_STR}foo_1_iri"])
    mock_resource_client_class.return_value = mock_resource_client

    mock_project_client = Mock()
    mock_project_client.get_project_iri.return_value = PROJECT_IRI
    mock_project_client_class.return_value = mock_project_client

    clients = UploadClients(ingest_client_mock, list_client_mock, legal_info_client_mock)
    _upload_all_resources(clients, upload_state)

    assert mock_resource_client.post_resource.call_count == 1
    resource_json = mock_resource_client.post_resource.call_args[0][0]
    prop_name = f"{LINK_PROP}Value"
    expected = {
        "@type": "http://0.0.0.0:3333/ontology/9999/onto/v2#foo_1_type",
        RDFS_LABEL: {
            "@type": "http://www.w3.org/2001/XMLSchema#string",
            "@value": "foo_1_label",
        },
        "http://api.knora.org/ontology/knora-api/v2#attachedToProject": {"@id": PROJECT_IRI},
        "@context": {},
        prop_name: {
            "@type": "http://api.knora.org/ontology/knora-api/v2#LinkValue",
            "http://api.knora.org/ontology/knora-api/v2#linkValueHasTargetIri": {
                "@id": f"{RES_IRI_NAMESPACE_STR}foo_2_iri"
            },
        },
    }
    assert resource_json[prop_name] == expected[prop_name]
    expected_project = expected["http://api.knora.org/ontology/knora-api/v2#attachedToProject"]
    assert resource_json["http://api.knora.org/ontology/knora-api/v2#attachedToProject"] == expected_project
    expected_label = expected[RDFS_LABEL]
    assert resource_json[RDFS_LABEL] == expected_label
    assert resource_json["@type"] == expected["@type"]
    assert not upload_state.pending_resources
    assert not upload_state.failed_uploads
    assert upload_state.iri_resolver.lookup == {
        "foo_1_id": f"{RES_IRI_NAMESPACE_STR}foo_1_iri",
        "foo_2_id": f"{RES_IRI_NAMESPACE_STR}foo_2_iri",
    }
    assert not upload_state.pending_stash


@patch("dsp_tools.commands.xmlupload.execute_upload.ProjectClientLive")
@patch("dsp_tools.commands.xmlupload.execute_upload.ResourceClientLive")
def test_2_resources_with_stash_interrupted_by_timeout(
    mock_resource_client_class: Mock,
    mock_project_client_class: Mock,
    link_val_stash_lookup_two_items,
    ingest_client_mock: AssetClient,
    legal_info_client_mock: LegalInfoClient,
    list_client_mock,
) -> None:
    _2_resources_with_stash_interrupted_by_error(
        link_val_stash_lookup_two_items,
        TimeoutError(),
        "TimeoutError",
        ingest_client_mock,
        legal_info_client_mock,
        list_client_mock,
        mock_project_client_class,
        mock_resource_client_class,
    )


@patch("dsp_tools.commands.xmlupload.execute_upload.ProjectClientLive")
@patch("dsp_tools.commands.xmlupload.execute_upload.ResourceClientLive")
def test_2_resources_with_stash_interrupted_by_keyboard(
    mock_resource_client_class: Mock,
    mock_project_client_class: Mock,
    link_val_stash_lookup_two_items,
    ingest_client_mock: AssetClient,
    legal_info_client_mock: LegalInfoClient,
    list_client_mock,
) -> None:
    _2_resources_with_stash_interrupted_by_error(
        link_val_stash_lookup_two_items,
        KeyboardInterrupt(),
        "KeyboardInterrupt",
        ingest_client_mock,
        legal_info_client_mock,
        list_client_mock,
        mock_project_client_class,
        mock_resource_client_class,
    )


def _2_resources_with_stash_interrupted_by_error(
    link_val_stash_lookup_two_items,
    err_to_interrupt_with: BaseException,
    err_as_str: str,
    ingest_client_mock: AssetClient,
    legal_info_client_mock: LegalInfoClient,
    list_client_mock,
    mock_project_client_class: Mock,
    mock_resource_client_class: Mock,
) -> None:
    resources = [
        ProcessedResource(f"foo_{i}_id", f"{ONTO}foo_{i}_type", f"foo_{i}_label", None, []) for i in range(1, 3)
    ]
    stash = Stash(link_value_stash=LinkValueStash(link_val_stash_lookup_two_items), standoff_stash=None)
    upload_state = UploadState(resources.copy(), deepcopy(stash), UploadConfig())
    mock_resource_client = Mock(spec_set=ResourceClientLive)
    mock_resource_client.post_resource = Mock(
        side_effect=[
            f"{RES_IRI_NAMESPACE_STR}foo_1_iri",
            err_to_interrupt_with,
        ]
    )
    mock_resource_client_class.return_value = mock_resource_client

    mock_project_client = Mock()
    mock_project_client.get_project_iri.return_value = PROJECT_IRI
    mock_project_client_class.return_value = mock_project_client

    clients = UploadClients(ingest_client_mock, list_client_mock, legal_info_client_mock)

    with patch("dsp_tools.commands.xmlupload.execute_upload.handle_upload_error") as handle_upload_error:
        with pytest.warns(DspToolsUserWarning):
            _upload_all_resources(clients, upload_state)

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
        handle_upload_error.assert_called_once_with(XmlUploadInterruptedError(err_msg), upload_state_expected)


@patch("dsp_tools.commands.xmlupload.execute_upload.ConnectionLive")
@patch("dsp_tools.commands.xmlupload.execute_upload.ProjectClientLive")
@patch("dsp_tools.commands.xmlupload.execute_upload.ResourceClientLive")
def test_2_resources_with_stash(
    mock_resource_client_class: Mock,
    mock_project_client_class: Mock,
    mock_connection_class: Mock,
    link_val_stash_lookup_two_items,
    ingest_client_mock: AssetClient,
    legal_info_client_mock: LegalInfoClient,
    list_client_mock,
) -> None:
    resources = [
        ProcessedResource(f"foo_{i}_id", f"{ONTO}foo_{i}_type", f"foo_{i}_label", None, []) for i in range(1, 3)
    ]
    stash = Stash(link_value_stash=LinkValueStash(link_val_stash_lookup_two_items), standoff_stash=None)
    upload_state = UploadState(resources.copy(), deepcopy(stash), UploadConfig())
    mock_resource_client = Mock(spec_set=ResourceClientLive)
    mock_resource_client.post_resource = Mock(
        side_effect=[
            f"{RES_IRI_NAMESPACE_STR}foo_1_iri",
            f"{RES_IRI_NAMESPACE_STR}foo_2_iri",
        ]
    )
    mock_resource_client_class.return_value = mock_resource_client

    con = Mock(spec_set=ConnectionLive)
    con.post = Mock(
        side_effect=[
            {},  # uploading a stash doesn't rely on a certain response
            {},  # uploading a stash doesn't rely on a certain response
        ]
    )
    mock_connection_class.return_value = con

    mock_project_client = Mock()
    mock_project_client.get_project_iri.return_value = PROJECT_IRI
    mock_project_client_class.return_value = mock_project_client

    clients = UploadClients(ingest_client_mock, list_client_mock, legal_info_client_mock)

    _upload_all_resources(clients, upload_state)

    post_kwargs = con.post.call_args_list[0].kwargs
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


@patch("dsp_tools.commands.xmlupload.execute_upload.ConnectionLive")
@patch("dsp_tools.commands.xmlupload.execute_upload.ProjectClientLive")
@patch("dsp_tools.commands.xmlupload.execute_upload.ResourceClientLive")
def test_5_resources_with_stash_and_interrupt_after_2(
    mock_resource_client_class: Mock,
    mock_project_client_class: Mock,
    mock_connection_class: Mock,
    link_val_stash_lookup_two_items,
    ingest_client_mock: AssetClient,
    legal_info_client_mock: LegalInfoClient,
    list_client_mock,
) -> None:
    resources = [
        ProcessedResource(f"foo_{i}_id", f"{ONTO}foo_{i}_type", f"foo_{i}_label", None, []) for i in range(1, 6)
    ]
    stash = Stash(link_value_stash=LinkValueStash(link_val_stash_lookup_two_items), standoff_stash=None)
    upload_config = UploadConfig(interrupt_after=2)
    upload_state = UploadState(resources.copy(), deepcopy(stash), upload_config)
    mock_resource_client = Mock(spec_set=ResourceClientLive)
    mock_resource_client.post_resource = Mock(
        side_effect=[
            f"{RES_IRI_NAMESPACE_STR}foo_1_iri",
            f"{RES_IRI_NAMESPACE_STR}foo_2_iri",
            f"{RES_IRI_NAMESPACE_STR}foo_3_iri",
            f"{RES_IRI_NAMESPACE_STR}foo_4_iri",
            f"{RES_IRI_NAMESPACE_STR}foo_5_iri",
        ]
    )
    mock_resource_client_class.return_value = mock_resource_client

    con = Mock(spec_set=ConnectionLive)
    con.post = Mock(side_effect=[{}, {}])
    mock_connection_class.return_value = con

    mock_project_client = Mock()
    mock_project_client.get_project_iri.return_value = PROJECT_IRI
    mock_project_client_class.return_value = mock_project_client

    err_msg = "Interrupted: Maximum number of resources was reached (2)"
    client = UploadClients(ingest_client_mock, list_client_mock, legal_info_client_mock)

    with patch("dsp_tools.commands.xmlupload.execute_upload.handle_upload_error") as handle_upload_error:
        _upload_all_resources(client, upload_state)
        iri_resolver_expected = IriResolver(
            {"foo_1_id": f"{RES_IRI_NAMESPACE_STR}foo_1_iri", "foo_2_id": f"{RES_IRI_NAMESPACE_STR}foo_2_iri"}
        )
        upload_state_expected = UploadState(resources[2:], stash, upload_config, [], iri_resolver_expected)
        handle_upload_error.assert_called_once_with(XmlUploadInterruptedError(err_msg), upload_state_expected)

    with patch("dsp_tools.commands.xmlupload.execute_upload.handle_upload_error") as handle_upload_error:
        _upload_all_resources(client, upload_state)
        iri_resolver_expected.lookup.update(
            {"foo_3_id": f"{RES_IRI_NAMESPACE_STR}foo_3_iri", "foo_4_id": f"{RES_IRI_NAMESPACE_STR}foo_4_iri"}
        )
        upload_state_expected = UploadState(resources[4:], stash, upload_config, [], iri_resolver_expected)
        handle_upload_error.assert_called_once_with(XmlUploadInterruptedError(err_msg), upload_state_expected)

    with patch("dsp_tools.commands.xmlupload.execute_upload.handle_upload_error") as handle_upload_error:
        _upload_all_resources(client, upload_state)
        iri_resolver_expected.lookup.update({"foo_5_id": f"{RES_IRI_NAMESPACE_STR}foo_5_iri"})
        empty_stash = Stash(standoff_stash=None, link_value_stash=LinkValueStash({}))
        upload_state_expected = UploadState([], empty_stash, upload_config, [], iri_resolver_expected)
        handle_upload_error.assert_not_called()
        assert upload_state == upload_state_expected


@patch("dsp_tools.commands.xmlupload.execute_upload.ConnectionLive")
@patch("dsp_tools.commands.xmlupload.execute_upload.ProjectClientLive")
@patch("dsp_tools.commands.xmlupload.execute_upload.ResourceClientLive")
def test_6_resources_with_stash_and_interrupt_after_2(
    mock_resource_client_class: Mock,
    mock_project_client_class: Mock,
    mock_connection_class: Mock,
    link_val_stash_lookup_two_items,
    ingest_client_mock: AssetClient,
    legal_info_client_mock: LegalInfoClient,
    list_client_mock,
) -> None:
    resources = [
        ProcessedResource(f"foo_{i}_id", f"{ONTO}foo_{i}_type", f"foo_{i}_label", None, []) for i in range(1, 7)
    ]
    stash = Stash(link_value_stash=LinkValueStash(link_val_stash_lookup_two_items), standoff_stash=None)
    upload_config = UploadConfig(interrupt_after=2)
    upload_state = UploadState(resources.copy(), deepcopy(stash), upload_config)
    mock_resource_client = Mock(spec_set=ResourceClientLive)
    mock_resource_client.post_resource = Mock(
        side_effect=[
            f"{RES_IRI_NAMESPACE_STR}foo_1_iri",
            f"{RES_IRI_NAMESPACE_STR}foo_2_iri",
            f"{RES_IRI_NAMESPACE_STR}foo_3_iri",
            f"{RES_IRI_NAMESPACE_STR}foo_4_iri",
            f"{RES_IRI_NAMESPACE_STR}foo_5_iri",
            f"{RES_IRI_NAMESPACE_STR}foo_6_iri",
        ]
    )
    mock_resource_client_class.return_value = mock_resource_client

    con = Mock(spec_set=ConnectionLive)
    con.post = Mock(side_effect=[{}, {}])
    mock_connection_class.return_value = con

    mock_project_client = Mock()
    mock_project_client.get_project_iri.return_value = PROJECT_IRI
    mock_project_client_class.return_value = mock_project_client

    err_msg = "Interrupted: Maximum number of resources was reached (2)"
    client = UploadClients(ingest_client_mock, list_client_mock, legal_info_client_mock)

    with patch("dsp_tools.commands.xmlupload.execute_upload.handle_upload_error") as handle_upload_error:
        _upload_all_resources(client, upload_state)
        iri_resolver_expected = IriResolver(
            {"foo_1_id": f"{RES_IRI_NAMESPACE_STR}foo_1_iri", "foo_2_id": f"{RES_IRI_NAMESPACE_STR}foo_2_iri"}
        )
        upload_state_expected = UploadState(resources[2:], stash, upload_config, [], iri_resolver_expected)
        handle_upload_error.assert_called_once_with(XmlUploadInterruptedError(err_msg), upload_state_expected)

    with patch("dsp_tools.commands.xmlupload.execute_upload.handle_upload_error") as handle_upload_error:
        _upload_all_resources(client, upload_state)
        iri_resolver_expected.lookup.update(
            {"foo_3_id": f"{RES_IRI_NAMESPACE_STR}foo_3_iri", "foo_4_id": f"{RES_IRI_NAMESPACE_STR}foo_4_iri"}
        )
        upload_state_expected = UploadState(resources[4:], stash, upload_config, [], iri_resolver_expected)
        handle_upload_error.assert_called_once_with(XmlUploadInterruptedError(err_msg), upload_state_expected)

    with patch("dsp_tools.commands.xmlupload.execute_upload.handle_upload_error") as handle_upload_error:
        _upload_all_resources(client, upload_state)
        iri_resolver_expected.lookup.update(
            {"foo_5_id": f"{RES_IRI_NAMESPACE_STR}foo_5_iri", "foo_6_id": f"{RES_IRI_NAMESPACE_STR}foo_6_iri"}
        )
        upload_state_expected = UploadState([], stash, upload_config, [], iri_resolver_expected)
        handle_upload_error.assert_called_once_with(XmlUploadInterruptedError(err_msg), upload_state_expected)

    with patch("dsp_tools.commands.xmlupload.execute_upload.handle_upload_error") as handle_upload_error:
        _upload_all_resources(client, upload_state)
        empty_stash = Stash(standoff_stash=None, link_value_stash=LinkValueStash({}))
        upload_state_expected = UploadState([], empty_stash, upload_config, [], iri_resolver_expected)
        handle_upload_error.assert_not_called()
        assert upload_state == upload_state_expected


@patch("dsp_tools.commands.xmlupload.execute_upload.ConnectionLive")
@patch("dsp_tools.commands.xmlupload.execute_upload.ProjectClientLive")
@patch("dsp_tools.commands.xmlupload.execute_upload.ResourceClientLive")
def test_logging(
    mock_resource_client_class: Mock,
    mock_project_client_class: Mock,
    mock_connection_class: Mock,
    link_val_stash_lookup_two_items,
    caplog: pytest.LogCaptureFixture,
    ingest_client_mock: AssetClient,
    legal_info_client_mock: LegalInfoClient,
    list_client_mock,
) -> None:
    resources = [
        ProcessedResource(f"foo_{i}_id", f"{ONTO}foo_{i}_type", f"foo_{i}_label", None, []) for i in range(1, 6)
    ]
    stash = Stash(link_value_stash=LinkValueStash(link_val_stash_lookup_two_items), standoff_stash=None)
    upload_config = UploadConfig(interrupt_after=2)
    upload_state = UploadState(resources.copy(), deepcopy(stash), upload_config)
    mock_resource_client = Mock(spec_set=ResourceClientLive)
    mock_resource_client.post_resource = Mock(
        side_effect=[
            f"{RES_IRI_NAMESPACE_STR}foo_1_iri",
            f"{RES_IRI_NAMESPACE_STR}foo_2_iri",
            f"{RES_IRI_NAMESPACE_STR}foo_3_iri",
            f"{RES_IRI_NAMESPACE_STR}foo_4_iri",
            f"{RES_IRI_NAMESPACE_STR}foo_5_iri",
        ]
    )
    mock_resource_client_class.return_value = mock_resource_client

    con = Mock(spec_set=ConnectionLive)
    con.post = Mock(side_effect=[{}, {}])
    mock_connection_class.return_value = con

    mock_project_client = Mock()
    mock_project_client.get_project_iri.return_value = PROJECT_IRI
    mock_project_client_class.return_value = mock_project_client

    clients = UploadClients(ingest_client_mock, list_client_mock, legal_info_client_mock)

    with patch("dsp_tools.commands.xmlupload.execute_upload.handle_upload_error"):
        _upload_all_resources(clients, upload_state)
        assert (
            caplog.records[1].message
            == f"Created resource 1/5: 'foo_1_label' (ID: 'foo_1_id', IRI: '{RES_IRI_NAMESPACE_STR}foo_1_iri')"
        )
        assert (
            caplog.records[3].message
            == f"Created resource 2/5: 'foo_2_label' (ID: 'foo_2_id', IRI: '{RES_IRI_NAMESPACE_STR}foo_2_iri')"
        )
        caplog.clear()

        _upload_all_resources(clients, upload_state)
        assert (
            caplog.records[1].message
            == f"Created resource 3/5: 'foo_3_label' (ID: 'foo_3_id', IRI: '{RES_IRI_NAMESPACE_STR}foo_3_iri')"
        )
        assert (
            caplog.records[3].message
            == f"Created resource 4/5: 'foo_4_label' (ID: 'foo_4_id', IRI: '{RES_IRI_NAMESPACE_STR}foo_4_iri')"
        )
        caplog.clear()

        _upload_all_resources(clients, upload_state)
        assert (
            caplog.records[1].message
            == f"Created resource 5/5: 'foo_5_label' (ID: 'foo_5_id', IRI: '{RES_IRI_NAMESPACE_STR}foo_5_iri')"
        )
        assert caplog.records[3].message == "  Upload resptrs of resource 'foo_1_id'..."
        assert caplog.records[5].message == "  Upload resptrs of resource 'foo_2_id'..."
        caplog.clear()


@patch("dsp_tools.commands.xmlupload.execute_upload.ConnectionLive")
@patch("dsp_tools.commands.xmlupload.execute_upload.ProjectClientLive")
@patch("dsp_tools.commands.xmlupload.execute_upload.ResourceClientLive")
def test_post_requests(
    mock_resource_client_class: Mock,
    mock_project_client_class: Mock,
    mock_connection_class: Mock,
    link_val_stash_lookup_two_items,
    ingest_client_mock: AssetClient,
    legal_info_client_mock: LegalInfoClient,
    list_client_mock,
) -> None:
    resources = [
        ProcessedResource(f"foo_{i}_id", f"{ONTO}foo_{i}_type", f"foo_{i}_label", None, []) for i in range(1, 7)
    ]
    stash = Stash(link_value_stash=LinkValueStash(link_val_stash_lookup_two_items), standoff_stash=None)
    upload_config = UploadConfig(interrupt_after=2)
    upload_state = UploadState(resources.copy(), deepcopy(stash), upload_config)
    mock_resource_client = Mock(spec_set=ResourceClientLive)
    mock_resource_client.post_resource = Mock(
        side_effect=[
            f"{RES_IRI_NAMESPACE_STR}foo_1_iri",
            f"{RES_IRI_NAMESPACE_STR}foo_2_iri",
            f"{RES_IRI_NAMESPACE_STR}foo_3_iri",
            f"{RES_IRI_NAMESPACE_STR}foo_4_iri",
            f"{RES_IRI_NAMESPACE_STR}foo_5_iri",
            f"{RES_IRI_NAMESPACE_STR}foo_6_iri",
        ]
    )
    mock_resource_client_class.return_value = mock_resource_client

    con = Mock(spec_set=ConnectionLive)
    con.post = Mock(side_effect=[{}, {}])
    mock_connection_class.return_value = con

    mock_project_client = Mock()
    mock_project_client.get_project_iri.return_value = PROJECT_IRI
    mock_project_client_class.return_value = mock_project_client

    clients = UploadClients(ingest_client_mock, list_client_mock, legal_info_client_mock)

    with patch("dsp_tools.commands.xmlupload.execute_upload.handle_upload_error"):
        _upload_all_resources(clients, upload_state)
        _upload_all_resources(clients, upload_state)
        _upload_all_resources(clients, upload_state)
        _upload_all_resources(clients, upload_state)
        assert mock_resource_client.post_resource.call_count == 6  # 6 resource creations
        assert len(con.post.call_args_list) == 2  # 2 stash uploads


@patch("dsp_tools.commands.xmlupload.execute_upload.ProjectClientLive")
@patch("dsp_tools.commands.xmlupload.execute_upload.ResourceClientLive")
def test_interruption_if_resource_cannot_be_created_because_of_404(
    mock_resource_client_class: Mock,
    mock_project_client_class: Mock,
    ingest_client_mock: AssetClient,
    legal_info_client_mock: LegalInfoClient,
    list_client_mock,
) -> None:
    resources = [
        ProcessedResource(f"foo_{i}_id", f"{ONTO}foo_{i}_type", f"foo_{i}_label", None, []) for i in range(1, 3)
    ]
    upload_state = UploadState(resources.copy(), Stash(None, None), UploadConfig(), [], IriResolver())
    mock_resource_client = Mock(spec_set=ResourceClientLive)
    mock_resource_client.post_resource = Mock(
        side_effect=[
            ResponseCodeAndText(404, "not found"),  # foo_1 fails
            f"{RES_IRI_NAMESPACE_STR}foo_2_iri",  # foo_2 succeeds
        ]
    )
    mock_resource_client_class.return_value = mock_resource_client

    mock_project_client = Mock()
    mock_project_client.get_project_iri.return_value = PROJECT_IRI
    mock_project_client_class.return_value = mock_project_client

    with patch("dsp_tools.commands.xmlupload.execute_upload.handle_upload_error") as handle_upload_error:
        _upload_all_resources(UploadClients(ingest_client_mock, list_client_mock, legal_info_client_mock), upload_state)
        handle_upload_error.assert_not_called()
        assert upload_state.failed_uploads == ["foo_1_id"]
        assert upload_state.iri_resolver.lookup == {"foo_2_id": f"{RES_IRI_NAMESPACE_STR}foo_2_iri"}
