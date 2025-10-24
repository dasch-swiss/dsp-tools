# mypy: disable-error-code="no-untyped-def"

from unittest.mock import Mock

import pytest
from requests import Response

from dsp_tools.clients.authentication_client import AuthenticationClient
from dsp_tools.clients.metadata_client import MetadataClient


@pytest.fixture
def mock_auth_client() -> Mock:
    mock = Mock(spec=AuthenticationClient)
    mock.server = "http://0.0.0.0:3333"
    mock.get_token.return_value = "test-token-123"
    return mock


@pytest.fixture
def metadata_client(mock_auth_client: Mock) -> MetadataClient:
    return MetadataClient(
        server="http://0.0.0.0:3333",
        authentication_client=mock_auth_client,
    )


@pytest.fixture
def ok_response():
    return [
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


@pytest.fixture
def non_ok_response():
    return {"message": "Project with shortcode 9999 not found."}


def test_get_resource_metadata_ok(metadata_client, ok_response):
    mock_response = Mock(spec=Response)
    mock_response.ok = True
    mock_response.status_code = 200
    mock_response.text = ok_response


def test_get_resource_metadata_non_ok(metadata_client, non_ok_response):
    mock_response = Mock(spec=Response)
    mock_response.ok = False
    mock_response.status_code = 403
    mock_response.text = non_ok_response


def test_get_resource_metadata_error_raised(metadata_client):
    pass
