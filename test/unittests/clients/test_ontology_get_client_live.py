from unittest.mock import Mock
from unittest.mock import patch

import pytest

from dsp_tools.clients.ontology_get_client_live import OntologyGetClientLive
from dsp_tools.error.exceptions import InternalError


@pytest.fixture
def api_url() -> str:
    return "http://0.0.0.0:3333"


@pytest.fixture
def ontology_client(api_url: str) -> OntologyGetClientLive:
    return OntologyGetClientLive(api_url, "9999")


class TestOntologyClient:
    def test_get_ontology_iris_ok(self, ontology_client: OntologyGetClientLive) -> None:
        mock_response = Mock(status_code=200, ok=True, headers={})
        mock_response.json.return_value = {"project": {"ontologies": ["onto_iri"]}}
        with patch("dsp_tools.commands.validate_data.api_clients.requests.get", return_value=mock_response) as mock_get:
            result = ontology_client._get_ontology_iris()
        assert result == ["onto_iri"]
        assert mock_get.call_args_list[0][1]["url"] == f"{ontology_client.api_url}/admin/projects/shortcode/9999"

    def test_get_ontology_iris_non_ok_code(self, ontology_client: OntologyGetClientLive) -> None:
        mock_response = Mock(status_code=404, ok=False, headers={})
        mock_response.json.return_value = {}
        with patch("dsp_tools.commands.validate_data.api_clients.requests.get", return_value=mock_response):
            with pytest.raises(InternalError):
                ontology_client._get_ontology_iris()

    def test_get_ontology_iris_no_ontology_key(self, ontology_client: OntologyGetClientLive) -> None:
        mock_response = Mock(status_code=200, ok=True, headers={})
        mock_response.json.return_value = {"foo": "bar"}
        with patch("dsp_tools.commands.validate_data.api_clients.requests.get", return_value=mock_response):
            with pytest.raises(InternalError):
                ontology_client._get_ontology_iris()

    def test_get_one_ontology(self, ontology_client: OntologyGetClientLive) -> None:
        mock_response = Mock(status_code=200, ok=True, headers={}, text="Turtle Text")
        mock_response.json.return_value = {}
        with patch("dsp_tools.commands.validate_data.api_clients.requests.get", return_value=mock_response) as mock_get:
            result = ontology_client._get_one_ontology("iri")
        assert result == "Turtle Text"
        assert mock_get.call_args_list[0][1]["url"] == "iri"
        assert mock_get.call_args_list[0][1]["headers"] == {"Accept": "text/turtle"}


if __name__ == "__main__":
    pytest.main([__file__])
