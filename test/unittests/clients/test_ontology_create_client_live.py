import json
from unittest.mock import Mock

import pytest
import requests
from rdflib import XSD
from rdflib import Literal
from rdflib import Namespace
from rdflib import URIRef
from requests import ReadTimeout
from requests import Response

from dsp_tools.clients.authentication_client import AuthenticationClient
from dsp_tools.clients.ontology_create_client_live import OntologyCreateClientLive
from dsp_tools.clients.ontology_create_client_live import _parse_last_modification_date
from dsp_tools.error.custom_warnings import DspToolsUnexpectedStatusCodeWarning
from dsp_tools.error.exceptions import BadCredentialsError
from dsp_tools.error.exceptions import DspToolsRequestException
from dsp_tools.error.exceptions import FatalNonOkApiResponseCode

ONTO = Namespace("http://0.0.0.0:3333/ontology/9999/onto/v2#")
ONTO_IRI = URIRef("http://0.0.0.0:3333/ontology/9999/onto/v2")

TEST_RES_IRI = ONTO.TestResource
TEST_PROP_IRI = ONTO.hasText

LAST_MODIFICATION_DATE = Literal("2025-10-14T13:00:00.000000Z", datatype=XSD.dateTimeStamp)


@pytest.fixture
def mock_auth_client() -> Mock:
    mock = Mock(spec=AuthenticationClient)
    mock.server = "http://0.0.0.0:3333"
    mock.get_token.return_value = "test-token-123"
    return mock


@pytest.fixture
def ontology_client(mock_auth_client: Mock) -> OntologyCreateClientLive:
    return OntologyCreateClientLive(
        server="http://0.0.0.0:3333",
        authentication_client=mock_auth_client,
    )


@pytest.fixture
def sample_cardinality_graph() -> dict[str, object]:
    return {
        "@id": "http://0.0.0.0:3333/ontology/4124/testonto/v2",
        "@type": ["http://www.w3.org/2002/07/owl#Ontology"],
        "http://api.knora.org/ontology/knora-api/v2#lastModificationDate": [
            {"@type": "http://www.w3.org/2001/XMLSchema#dateTimeStamp", "@value": str(LAST_MODIFICATION_DATE)}
        ],
        "@graph": [
            {
                "@id": str(TEST_RES_IRI),
                "@type": ["http://www.w3.org/2002/07/owl#Class"],
                "http://www.w3.org/2000/01/rdf-schema#subClassOf": [{"@id": "_:N114b29af852e4ae59f5500d94e4db2f2"}],
            },
            {
                "@id": "_:N114b29af852e4ae59f5500d94e4db2f2",
                "@type": ["http://www.w3.org/2002/07/owl#Restriction"],
                "http://www.w3.org/2002/07/owl#maxCardinality": [
                    {"@type": "http://www.w3.org/2001/XMLSchema#integer", "@value": 1}
                ],
                "http://www.w3.org/2002/07/owl#onProperty": [{"@id": str(TEST_PROP_IRI)}],
            },
        ],
    }


class TestOntologyClientLive:
    def test_post_resource_cardinalities_success(
        self,
        ontology_client: OntologyCreateClientLive,
        sample_cardinality_graph: dict[str, object],
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        # Mock successful response
        mock_response = Mock(spec=Response)
        mock_response.ok = True
        mock_response.status_code = 200
        mock_response.text = json.dumps(
            {
                "@context": {
                    "knora-api": "http://api.knora.org/ontology/knora-api/v2#",
                    "xsd": "http://www.w3.org/2001/XMLSchema#",
                },
                "knora-api:lastModificationDate": {
                    "@value": str(LAST_MODIFICATION_DATE),
                    "@type": "xsd:dateTimeStamp",
                },
            }
        )

        def mock_post_and_log_request(*_args: object, **_kwargs: object) -> Response:
            return mock_response

        monkeypatch.setattr(ontology_client, "_post_and_log_request", mock_post_and_log_request)

        result = ontology_client.post_resource_cardinalities(sample_cardinality_graph)
        assert result == LAST_MODIFICATION_DATE

    def test_post_resource_cardinalities_forbidden(
        self,
        ontology_client: OntologyCreateClientLive,
        sample_cardinality_graph: dict[str, object],
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        mock_response = Mock(spec=Response)
        mock_response.ok = False
        mock_response.status_code = 403

        def mock_post_and_log_request(*_args: object, **_kwargs: object) -> Response:
            return mock_response

        monkeypatch.setattr(ontology_client, "_post_and_log_request", mock_post_and_log_request)
        with pytest.raises(BadCredentialsError):
            ontology_client.post_resource_cardinalities(sample_cardinality_graph)

    def test_post_resource_cardinalities_server_error(
        self,
        ontology_client: OntologyCreateClientLive,
        sample_cardinality_graph: dict[str, object],
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        mock_response = Mock(spec=Response)
        mock_response.ok = False
        mock_response.status_code = 500
        mock_response.text = "text"

        def mock_post_and_log_request(*_args: object, **_kwargs: object) -> Response:
            return mock_response

        monkeypatch.setattr(ontology_client, "_post_and_log_request", mock_post_and_log_request)
        with pytest.warns(DspToolsUnexpectedStatusCodeWarning):
            result = ontology_client.post_resource_cardinalities(sample_cardinality_graph)
        assert result is None

    def test_post_resource_cardinalities_timeout(
        self,
        ontology_client: OntologyCreateClientLive,
        sample_cardinality_graph: dict[str, object],
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        def mock_post_and_log_request(*_args: object, **_kwargs: object) -> None:
            raise ReadTimeout("Connection timed out")

        monkeypatch.setattr(ontology_client, "_post_and_log_request", mock_post_and_log_request)

        with pytest.raises(DspToolsRequestException):
            ontology_client.post_resource_cardinalities(sample_cardinality_graph)

    def test_post_and_log_request_creates_correct_headers(
        self, ontology_client: OntologyCreateClientLive, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        captured_kwargs: dict[str, object] = {}

        def mock_post(*_args: object, **kwargs: object) -> Response:
            captured_kwargs.update(kwargs)
            mock_response = Mock(spec=Response)
            mock_response.ok = True
            mock_response.status_code = 200
            mock_response.headers = {}
            mock_response.text = ""
            mock_response.json.return_value = {}
            return mock_response

        monkeypatch.setattr(requests, "post", mock_post)

        test_data = {"@id": "test:id", "@type": "owl:Class"}
        ontology_client._post_and_log_request("http://test.com/api", test_data)

        assert "headers" in captured_kwargs
        headers = captured_kwargs["headers"]
        assert isinstance(headers, dict)
        assert headers["Content-Type"] == "application/json"
        assert headers["Authorization"] == "Bearer test-token-123"

    def test_post_and_log_request_uses_correct_url(
        self, ontology_client: OntologyCreateClientLive, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        captured_url: str | None = None

        def mock_post(url: str, *_args: object, **_kwargs: object) -> Response:
            nonlocal captured_url
            captured_url = url
            mock_response = Mock(spec=Response)
            mock_response.ok = True
            mock_response.status_code = 200
            mock_response.headers = {}
            mock_response.text = ""
            mock_response.json.return_value = {}
            return mock_response

        monkeypatch.setattr(requests, "post", mock_post)

        test_url = "http://0.0.0.0:3333/v2/ontologies/cardinalities"
        test_data = {"@id": "test:id"}
        ontology_client._post_and_log_request(test_url, test_data)

        assert captured_url == test_url

    def test_get_last_modification_date_success(
        self, ontology_client: OntologyCreateClientLive, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        mock_response = Mock(spec=Response)
        mock_response.ok = True
        mock_response.status_code = 200
        mock_response.text = json.dumps(
            {
                "@context": {
                    "knora-api": "http://api.knora.org/ontology/knora-api/v2#",
                    "xsd": "http://www.w3.org/2001/XMLSchema#",
                },
                "@id": str(ONTO_IRI),
                "knora-api:lastModificationDate": {
                    "@value": str(LAST_MODIFICATION_DATE),
                    "@type": "xsd:dateTimeStamp",
                },
            }
        )

        def mock_get_and_log_request(*_args: object, **_kwargs: object) -> Response:
            return mock_response

        monkeypatch.setattr(ontology_client, "_get_and_log_request", mock_get_and_log_request)

        result = ontology_client.get_last_modification_date("http://0.0.0.0:3333/project/9999", str(ONTO_IRI))
        assert result == LAST_MODIFICATION_DATE

    def test_get_last_modification_date_unexpected_status_code(
        self, ontology_client: OntologyCreateClientLive, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        mock_response = Mock(spec=Response)
        mock_response.ok = False
        mock_response.status_code = 404
        mock_response.text = "text"

        def mock_get_and_log_request(*_args: object, **_kwargs: object) -> Response:
            return mock_response

        monkeypatch.setattr(ontology_client, "_get_and_log_request", mock_get_and_log_request)

        with pytest.raises(FatalNonOkApiResponseCode):
            ontology_client.get_last_modification_date("http://0.0.0.0:3333/project/9999", str(ONTO_IRI))

    def test_get_last_modification_date_timeout(
        self, ontology_client: OntologyCreateClientLive, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        def mock_get_and_log_request(*_args: object, **_kwargs: object) -> None:
            raise ReadTimeout("Connection timed out")

        monkeypatch.setattr(ontology_client, "_get_and_log_request", mock_get_and_log_request)

        with pytest.raises(DspToolsRequestException):
            ontology_client.get_last_modification_date("http://0.0.0.0:3333/project/9999", str(ONTO_IRI))


class TestParseLastModificationDate:
    def test_parse_valid_response(self) -> None:
        response_text = json.dumps(
            {
                "@context": {
                    "knora-api": "http://api.knora.org/ontology/knora-api/v2#",
                    "xsd": "http://www.w3.org/2001/XMLSchema#",
                },
                "knora-api:lastModificationDate": {
                    "@value": str(LAST_MODIFICATION_DATE),
                    "@type": "xsd:dateTimeStamp",
                },
            }
        )
        result = _parse_last_modification_date(response_text)
        assert result is not None
        assert isinstance(result, Literal)
        assert result == LAST_MODIFICATION_DATE
