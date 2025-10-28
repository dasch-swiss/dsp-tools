# mypy: disable-error-code="no-untyped-def"

from unittest.mock import Mock
from unittest.mock import patch

import pytest
from requests import Response

from dsp_tools.clients.authentication_client import AuthenticationClient
from dsp_tools.clients.metadata_client import ExistingResourcesRetrieved
from dsp_tools.clients.metadata_client_live import MetadataClientLive


@pytest.fixture
def mock_auth_client() -> Mock:
    mock = Mock(spec=AuthenticationClient)
    mock.server = "http://0.0.0.0:3333"
    mock.get_token.return_value = "test-token-123"
    return mock


@pytest.fixture
def metadata_client(mock_auth_client: Mock) -> MetadataClientLive:
    return MetadataClientLive(
        server="http://0.0.0.0:3333",
        authentication_client=mock_auth_client,
    )


@patch("dsp_tools.clients.metadata_client_live.log_response")
@patch("dsp_tools.clients.metadata_client_live.log_request")
def test_get_resource_metadata_ok_with_data(log_request, log_response, metadata_client):  # noqa: ARG001
    expected_data = [
        {
            "resourceClassIri": "http://0.0.0.0:3333/ontology/4124/testonto/v2#minimalResource",
            "resourceIri": "http://rdfh.ch/4124/bPs-3bjqSr2uIJFGO3Joyw",
            "arkUrl": "http://0.0.0.0:3336/ark:/72163/1/4124/bPs=3bjqSr2uIJFGO3Joywb",
            "arkUrlWithTimestamp": "http://0.0.0.0:3336/ark:/72163/1/4124/bPs=3bjqSr2uIJFGO3Joywb.20251024T142527080662792Z",
            "label": "The only resource",
            "resourceCreatorIri": "http://rdfh.ch/users/root",
            "resourceCreationDate": "2025-10-24T14:25:05.092534796Z",
        }
    ]
    mock_response = Mock(spec=Response)
    mock_response.ok = True
    mock_response.status_code = 200
    mock_response.json.return_value = expected_data

    with patch("dsp_tools.clients.metadata_client_live.requests.get") as get_mock:
        get_mock.return_value = mock_response
        response_type, data = metadata_client.get_resource_metadata("4124")

    assert response_type == ExistingResourcesRetrieved.TRUE
    assert data == expected_data


@patch("dsp_tools.clients.metadata_client_live.log_response")
@patch("dsp_tools.clients.metadata_client_live.log_request")
def test_get_resource_metadata_ok_no_data(log_request, log_response, metadata_client):  # noqa: ARG001
    mock_response = Mock(spec=Response)
    mock_response.ok = True
    mock_response.status_code = 200
    mock_response.json.return_value = []

    with patch("dsp_tools.clients.metadata_client_live.requests.get") as get_mock:
        get_mock.return_value = mock_response
        response_type, data = metadata_client.get_resource_metadata("4124")

    assert response_type == ExistingResourcesRetrieved.TRUE
    assert data == []


@patch("dsp_tools.clients.metadata_client_live.log_response")
@patch("dsp_tools.clients.metadata_client_live.log_request")
def test_get_resource_metadata_non_ok(log_request, log_response, metadata_client):  # noqa: ARG001
    mock_response = Mock(spec=Response)
    mock_response.ok = False
    mock_response.status_code = 403
    mock_response.text = {"message": "Some message from the API."}

    with patch("dsp_tools.clients.metadata_client_live.requests.get") as get_mock:
        get_mock.return_value = mock_response
        response_type, data = metadata_client.get_resource_metadata("9999")

    assert response_type == ExistingResourcesRetrieved.FALSE
    assert data == []


@patch("dsp_tools.clients.metadata_client_live.log_request")
def test_get_resource_metadata_error_raised(log_request, metadata_client):  # noqa: ARG001
    with patch("dsp_tools.clients.metadata_client_live.requests.get") as get_mock:
        get_mock.side_effect = Exception("Connection error")
        response_type, data = metadata_client.get_resource_metadata("4124")

    assert response_type == ExistingResourcesRetrieved.FALSE
    assert data == []
