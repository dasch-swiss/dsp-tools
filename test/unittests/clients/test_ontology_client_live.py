import json
from unittest.mock import Mock

import pytest
import requests
from rdflib import OWL
from rdflib import RDF
from rdflib import RDFS
from rdflib import XSD
from rdflib import BNode
from rdflib import Graph
from rdflib import Literal
from rdflib import Namespace
from rdflib import URIRef
from requests import ReadTimeout
from requests import Response

from dsp_tools.clients.authentication_client import AuthenticationClient
from dsp_tools.clients.ontology_client_live import OntologyClientLive
from dsp_tools.clients.ontology_client_live import _parse_last_modification_date
from dsp_tools.error.exceptions import BadCredentialsError
from dsp_tools.error.exceptions import BaseError
from dsp_tools.error.exceptions import PermanentTimeOutError
from dsp_tools.utils.rdflib_constants import KNORA_API

ONTO = Namespace("http://0.0.0.0:3333/ontology/9999/onto/v2#")
ONTO_IRI = URIRef("http://0.0.0.0:3333/ontology/9999/onto/v2")

TEST_RES_IRI = ONTO.TestResource
TEST_PROP_IRI = ONTO.hasText

LAST_MODIFICATION_DATE = Literal("2025-10-14T13:00:00.000000Z", XSD.dateTimeStamp)


@pytest.fixture
def mock_auth_client() -> Mock:
    mock = Mock(spec=AuthenticationClient)
    mock.server = "http://0.0.0.0:3333"
    mock.get_token.return_value = "test-token-123"
    return mock


@pytest.fixture
def ontology_client(mock_auth_client: Mock) -> OntologyClientLive:
    return OntologyClientLive(
        server="http://0.0.0.0:3333",
        project_shortcode="4123",
        authentication_client=mock_auth_client,
    )


@pytest.fixture
def sample_cardinality_graph() -> Graph:
    g = Graph()
    g.add((ONTO_IRI, RDF.type, OWL.Ontology))
    g.add((ONTO_IRI, KNORA_API.lastModificationDate, LAST_MODIFICATION_DATE))
    bn = BNode()
    g.add((TEST_RES_IRI, RDFS.subClassOf, bn))
    g.add((bn, RDF.type, OWL.Restriction))
    g.add((bn, OWL.cardinality, Literal(1)))
    g.add((bn, OWL.onProperty, TEST_PROP_IRI))
    return g


class TestOntologyClientLive:
    def test_post_resource_cardinalities_success(
        self, ontology_client: OntologyClientLive, sample_cardinality_graph: Graph, monkeypatch: pytest.MonkeyPatch
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
        self, ontology_client: OntologyClientLive, sample_cardinality_graph: Graph, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        mock_response = Mock(spec=Response)
        mock_response.ok = False
        mock_response.status_code = 403

        def mock_post_and_log_request(*_args: object, **_kwargs: object) -> Response:
            return mock_response

        monkeypatch.setattr(ontology_client, "_post_and_log_request", mock_post_and_log_request)

        with pytest.raises(BadCredentialsError) as exc_info:
            ontology_client.post_resource_cardinalities(sample_cardinality_graph)

        assert "administrator" in str(exc_info.value).lower()
        assert "permissions" in str(exc_info.value).lower()

    def test_post_resource_cardinalities_server_error(
        self, ontology_client: OntologyClientLive, sample_cardinality_graph: Graph, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        mock_response = Mock(spec=Response)
        mock_response.ok = False
        mock_response.status_code = 500

        def mock_post_and_log_request(*_args: object, **_kwargs: object) -> Response:
            return mock_response

        monkeypatch.setattr(ontology_client, "_post_and_log_request", mock_post_and_log_request)

        with pytest.raises(BaseError) as exc_info:
            ontology_client.post_resource_cardinalities(sample_cardinality_graph)

        assert "500" in str(exc_info.value)

    def test_post_resource_cardinalities_timeout(
        self, ontology_client: OntologyClientLive, sample_cardinality_graph: Graph, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        def mock_post_and_log_request(*_args: object, **_kwargs: object) -> None:
            raise ReadTimeout("Connection timed out")

        monkeypatch.setattr(ontology_client, "_post_and_log_request", mock_post_and_log_request)

        with pytest.raises(PermanentTimeOutError):
            ontology_client.post_resource_cardinalities(sample_cardinality_graph)

    def test_post_and_log_request_creates_correct_headers(
        self, ontology_client: OntologyClientLive, monkeypatch: pytest.MonkeyPatch
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

        test_data = [{"@id": "test:id", "@type": "owl:Class"}]
        ontology_client._post_and_log_request("http://test.com/api", test_data)

        assert "headers" in captured_kwargs
        headers = captured_kwargs["headers"]
        assert isinstance(headers, dict)
        assert headers["Content-Type"] == "application/json"
        assert headers["Authorization"] == "Bearer test-token-123"

    def test_post_and_log_request_uses_correct_url(
        self, ontology_client: OntologyClientLive, monkeypatch: pytest.MonkeyPatch
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
        test_data = [{"@id": "test:id"}]
        ontology_client._post_and_log_request(test_url, test_data)

        assert captured_url == test_url


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

    def test_parse_response_without_modification_date(self) -> None:
        response_text = json.dumps(
            {
                "@context": {
                    "knora-api": "http://api.knora.org/ontology/knora-api/v2#",
                },
                "rdfs:label": "Test ontology",
            }
        )
        result = _parse_last_modification_date(response_text)
        assert result is None
