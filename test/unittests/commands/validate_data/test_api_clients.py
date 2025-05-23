from typing import Any
from unittest.mock import Mock
from unittest.mock import patch

import pytest

from dsp_tools.commands.validate_data.api_clients import ListClient
from dsp_tools.commands.validate_data.api_clients import OntologyClient
from dsp_tools.error.exceptions import InternalError


@pytest.fixture
def api_url() -> str:
    return "http://0.0.0.0:3333"


@pytest.fixture
def ontology_client(api_url: str) -> OntologyClient:
    return OntologyClient(api_url, "9999")


@pytest.fixture
def list_client(api_url: str) -> ListClient:
    return ListClient(api_url, "9999")


class TestOntologyClient:
    def test_get_ontology_iris_ok(self, ontology_client: OntologyClient) -> None:
        mock_response = Mock(status_code=200, ok=True, headers={})
        mock_response.json.return_value = {"project": {"ontologies": ["onto_iri"]}}
        with patch("dsp_tools.commands.validate_data.api_clients.requests.get", return_value=mock_response) as mock_get:
            result = ontology_client._get_ontology_iris()
        assert result == ["onto_iri"]
        assert mock_get.call_args_list[0][1]["url"] == f"{ontology_client.api_url}/admin/projects/shortcode/9999"

    def test_get_ontology_iris_non_ok_code(self, ontology_client: OntologyClient) -> None:
        mock_response = Mock(status_code=404, ok=False, headers={})
        mock_response.json.return_value = {}
        with patch("dsp_tools.commands.validate_data.api_clients.requests.get", return_value=mock_response):
            with pytest.raises(InternalError):
                ontology_client._get_ontology_iris()

    def test_get_ontology_iris_no_ontology_key(self, ontology_client: OntologyClient) -> None:
        mock_response = Mock(status_code=200, ok=True, headers={})
        mock_response.json.return_value = {"foo": "bar"}
        with patch("dsp_tools.commands.validate_data.api_clients.requests.get", return_value=mock_response):
            with pytest.raises(InternalError):
                ontology_client._get_ontology_iris()

    def test_get_one_ontology(self, ontology_client: OntologyClient) -> None:
        mock_response = Mock(status_code=200, ok=True, headers={}, text="Turtle Text")
        mock_response.json.return_value = {}
        with patch("dsp_tools.commands.validate_data.api_clients.requests.get", return_value=mock_response) as mock_get:
            result = ontology_client._get_one_ontology("iri")
        assert result == "Turtle Text"
        assert mock_get.call_args_list[0][1]["url"] == "iri"
        assert mock_get.call_args_list[0][1]["headers"] == {"Accept": "text/turtle"}


class TestListConnection:
    def test_get_all_list_iris(self, list_client: ListClient) -> None:
        mock_response = Mock(status_code=200, ok=True, headers={})
        mock_response.json.return_value = {"lists": []}
        with patch("dsp_tools.commands.validate_data.api_clients.requests.get", return_value=mock_response) as mock_get:
            result = list_client._get_all_list_iris()
        assert result == {"lists": []}
        assert mock_get.call_args_list[0][1]["url"] == f"{list_client.api_url}/admin/lists?projectShortcode=9999"

    def test_get_all_list_iris_non_ok_code(self, list_client: ListClient) -> None:
        mock_response = Mock(status_code=404, ok=False, headers={})
        mock_response.json.return_value = {}
        with patch("dsp_tools.commands.validate_data.api_clients.requests.get", return_value=mock_response):
            with pytest.raises(InternalError):
                list_client._get_all_list_iris()

    def test_get_one_list(self, list_client: ListClient) -> None:
        mock_response = Mock(status_code=200, ok=True, headers={})
        mock_response.json.return_value = {"type": "ListGetResponseADM", "list": {}}
        with patch("dsp_tools.commands.validate_data.api_clients.requests.get", return_value=mock_response) as mock_get:
            result = list_client._get_one_list("http://rdfh.ch/lists/9999/WWqeCEj8R_qrK5djsVcHvg")
        assert result == {"type": "ListGetResponseADM", "list": {}}
        url_expected = f"{list_client.api_url}/admin/lists/http%3A%2F%2Frdfh.ch%2Flists%2F9999%2FWWqeCEj8R_qrK5djsVcHvg"
        assert mock_get.call_args_list[0][1]["url"] == url_expected

    def test_get_one_list_non_ok_code(self, list_client: ListClient) -> None:
        mock_response = Mock(status_code=404, ok=False, headers={})
        mock_response.json.return_value = {}
        with patch("dsp_tools.commands.validate_data.api_clients.requests.get", return_value=mock_response):
            with pytest.raises(InternalError):
                list_client._get_one_list("http://rdfh.ch/lists/9999/WWqeCEj8R_qrK5djsVcHvg")

    def test_extract_list_iris(self, list_client: ListClient, response_all_list_one_project: dict[str, Any]) -> None:
        extracted = list_client._extract_list_iris(response_all_list_one_project)
        expected = {"http://rdfh.ch/lists/9999/list1", "http://rdfh.ch/lists/9999/list2"}
        assert set(extracted) == expected

    def test_extract_list_iris_no_lists(
        self, list_client: ListClient, response_all_list_one_project_no_lists: dict[str, Any]
    ) -> None:
        extracted = list_client._extract_list_iris(response_all_list_one_project_no_lists)
        assert not extracted

    def test_reformat_one_list(self, list_client: ListClient, response_one_list: dict[str, Any]) -> None:
        reformatted = list_client._reformat_one_list(response_one_list)
        sorted_nodes = sorted(reformatted.nodes, key=lambda x: x.name)
        assert reformatted.list_iri == "http://rdfh.ch/lists/9999/list1"
        assert reformatted.list_name == "firstList"
        names = [x.name for x in sorted_nodes]
        assert names == ["n1", "n1.1", "n1.1.1", "n1.1.2"]
        expected_iris = [
            "http://rdfh.ch/lists/9999/n1",
            "http://rdfh.ch/lists/9999/n11",
            "http://rdfh.ch/lists/9999/n111",
            "http://rdfh.ch/lists/9999/n112",
        ]
        iris = [x.iri for x in sorted_nodes]
        assert iris == expected_iris


if __name__ == "__main__":
    pytest.main([__file__])
