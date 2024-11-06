from typing import Any
from unittest.mock import Mock
from unittest.mock import patch

import pytest

from dsp_tools.commands.validate_data.api_clients import ListClient
from dsp_tools.commands.validate_data.api_clients import OntologyClient
from dsp_tools.commands.validate_data.api_connection import ApiConnection
from dsp_tools.models.exceptions import InternalError
from dsp_tools.models.exceptions import UserError


@pytest.fixture
def api_con() -> ApiConnection:
    return ApiConnection("http://0.0.0.0:3333")


@pytest.fixture
def ontology_connection(api_con: ApiConnection) -> OntologyClient:
    return OntologyClient(api_con, "9999")


@pytest.fixture
def list_connection(api_con: ApiConnection) -> ListClient:
    return ListClient(api_con, "9999")


class TestOntologyConnection:
    def test_get_ontology_iris_ok(self, ontology_connection: OntologyClient) -> None:
        mock_response = Mock()
        mock_response.ok = True
        mock_response.json.return_value = {"project": {"ontologies": ["onto_iri"]}}
        with patch.object(ontology_connection.api_con, "get_with_endpoint", return_value=mock_response) as patched_get:
            result = ontology_connection._get_ontology_iris()
            assert result == ["onto_iri"]
            patched_get.assert_called_once_with(endpoint="admin/projects/shortcode/9999")

    def test_get_ontology_iris_non_ok_code(self, ontology_connection: OntologyClient) -> None:
        mock_response = Mock()
        mock_response.ok = False
        with patch.object(ontology_connection.api_con, "get_with_endpoint", return_value=mock_response) as patched_get:
            with pytest.raises(InternalError):
                ontology_connection._get_ontology_iris()
            patched_get.assert_called_once_with(endpoint="admin/projects/shortcode/9999")

    def test_get_ontology_iris_no_ontology_key(self, ontology_connection: OntologyClient) -> None:
        mock_response = Mock()
        mock_response.ok = True
        mock_response.json.return_value = {}
        with patch.object(ontology_connection.api_con, "get_with_endpoint", return_value=mock_response) as patched_get:
            with pytest.raises(UserError):
                ontology_connection._get_ontology_iris()
            patched_get.assert_called_once_with(endpoint="admin/projects/shortcode/9999")

    def test_get_one_ontology(self, ontology_connection: OntologyClient) -> None:
        mock_response = Mock()
        mock_response.ok = True
        mock_response.text = "Turtle Text"
        with patch.object(ontology_connection.api_con, "get_with_url", return_value=mock_response) as patched_get:
            result = ontology_connection._get_one_ontology("iri")
            assert result == "Turtle Text"
            patched_get.assert_called_once_with(url="iri", headers={"Accept": "text/turtle"})


class TestListConnection:
    def test_get_all_list_iris(self, list_connection: ListClient) -> None:
        mock_response = Mock()
        mock_response.ok = True
        mock_response.json.return_value = {"lists": []}
        with patch.object(list_connection.api_con, "get_with_endpoint", return_value=mock_response) as patched_get:
            result = list_connection._get_all_list_iris()
            assert result == {"lists": []}
            patched_get.assert_called_once_with(endpoint="admin/lists?9999")

    def test_get_all_list_iris_non_ok_code(self, list_connection: ListClient) -> None:
        mock_response = Mock()
        mock_response.ok = False
        with patch.object(list_connection.api_con, "get_with_endpoint", return_value=mock_response) as patched_get:
            with pytest.raises(InternalError):
                list_connection._get_all_list_iris()
            patched_get.assert_called_once_with(endpoint="admin/lists?9999")

    def test_get_one_list(self, list_connection: ListClient) -> None:
        mock_response = Mock()
        mock_response.ok = True
        mock_response.json.return_value = {"type": "ListGetResponseADM", "list": {}}
        with patch.object(list_connection.api_con, "get_with_endpoint", return_value=mock_response) as patched_get:
            result = list_connection._get_one_list("http://rdfh.ch/lists/9999/WWqeCEj8R_qrK5djsVcHvg")
            assert result == {"type": "ListGetResponseADM", "list": {}}
            patched_get.assert_called_once_with(
                endpoint="admin/lists/http%3A%2F%2Frdfh.ch%2Flists%2F9999%2FWWqeCEj8R_qrK5djsVcHvg"
            )

    def test_get_one_list_non_ok_code(self, list_connection: ListClient) -> None:
        mock_response = Mock()
        mock_response.ok = False
        with patch.object(list_connection.api_con, "get_with_endpoint", return_value=mock_response) as patched_get:
            with pytest.raises(InternalError):
                list_connection._get_one_list("http://rdfh.ch/lists/9999/WWqeCEj8R_qrK5djsVcHvg")
            patched_get.assert_called_once_with(
                endpoint="admin/lists/http%3A%2F%2Frdfh.ch%2Flists%2F9999%2FWWqeCEj8R_qrK5djsVcHvg"
            )

    def test_extract_list_iris(
        self, list_connection: ListClient, response_all_list_one_project: dict[str, Any]
    ) -> None:
        extracted = list_connection._extract_list_iris(response_all_list_one_project)
        expected = {"http://rdfh.ch/lists/9999/list1", "http://rdfh.ch/lists/9999/list2"}
        assert set(extracted) == expected

    def test_extract_list_iris_no_lists(
        self, list_connection: ListClient, response_all_list_one_project_no_lists: dict[str, Any]
    ) -> None:
        extracted = list_connection._extract_list_iris(response_all_list_one_project_no_lists)
        assert not extracted

    def test_reformat_one_list(self, list_connection: ListClient, response_one_list: dict[str, Any]) -> None:
        reformatted = list_connection._reformat_one_list(response_one_list)
        expected_nodes = {"n1", "n1.1", "n1.1.1", "n1.1.2"}
        assert reformatted.list_iri == "http://rdfh.ch/lists/9999/list1"
        assert reformatted.list_name == "firstList"
        assert set(reformatted.nodes) == expected_nodes


if __name__ == "__main__":
    pytest.main([__file__])
