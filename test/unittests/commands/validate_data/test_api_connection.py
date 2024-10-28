from typing import Any
from unittest.mock import Mock
from unittest.mock import patch

import pytest

from dsp_tools.commands.validate_data.api_connection import ListConnection
from dsp_tools.commands.validate_data.api_connection import OntologyConnection
from dsp_tools.models.exceptions import UserError


@pytest.fixture
def ontology_connection() -> OntologyConnection:
    return OntologyConnection("http://0.0.0.0:3333", "9999")


@pytest.fixture
def list_connection() -> ListConnection:
    return ListConnection("http://0.0.0.0:3333", "9999")


class TestOntologyConnection:
    def test_get_ontology_iris_ok(self, ontology_connection: OntologyConnection) -> None:
        mock_response = Mock()
        mock_response.ok = True
        mock_response.json.return_value = {"project": {"ontologies": ["onto_iri"]}}
        with patch.object(ontology_connection, "_get", return_value=mock_response) as patched_get:
            result = ontology_connection._get_ontology_iris()
            assert result == ["onto_iri"]
            patched_get.assert_called_once_with("http://0.0.0.0:3333/admin/projects/shortcode/9999")

    def test_get_ontology_iris_non_ok_code(self, ontology_connection: OntologyConnection) -> None:
        with patch("requests.get") as patched_get:
            patched_get.return_value.ok = False
            with pytest.raises(UserError):
                ontology_connection._get_ontology_iris()
            patched_get.assert_called_once_with(
                "http://0.0.0.0:3333/admin/projects/shortcode/9999", headers=None, timeout=100
            )

    def test_get_ontology_iris_no_ontology_key(self, ontology_connection: OntologyConnection) -> None:
        mock_response = Mock()
        mock_response.ok = True
        mock_response.json.return_value = {}
        with patch.object(ontology_connection, "_get", return_value=mock_response) as patched_get:
            with pytest.raises(UserError):
                ontology_connection._get_ontology_iris()
            patched_get.assert_called_once_with("http://0.0.0.0:3333/admin/projects/shortcode/9999")

    def test_get_one_ontology(self, ontology_connection: OntologyConnection) -> None:
        mock_response = Mock()
        mock_response.ok = True
        mock_response.text = "Turtle Text"
        with patch.object(ontology_connection, "_get", return_value=mock_response) as patched_get:
            result = ontology_connection._get_one_ontology("iri")
            assert result == "Turtle Text"
            patched_get.assert_called_once_with("iri", headers={"Accept": "text/turtle"})


class TestListConnection:
    def test_get_all_list_iris(self, list_connection: ListConnection) -> None:
        mock_response = Mock()
        mock_response.ok = True
        mock_response.json = {"lists": []}
        with patch.object(list_connection, "_get", return_value=mock_response) as patched_get:
            result = list_connection._get_all_list_iris()
            assert result == {"lists": []}
            patched_get.assert_called_once_with(url="http://0.0.0.0:3333/admin/lists?9999")

    def test_get_all_list_iris_non_ok_code(self, list_connection: ListConnection) -> None:
        with patch("requests.get") as patched_get:
            patched_get.return_value.ok = False
            with pytest.raises(UserError):
                list_connection._get_all_list_iris()
            patched_get.assert_called_once_with(url="http://0.0.0.0:3333/admin/lists?9999", headers=None, timeout=100)

    def test_get_one_list(self, list_connection: ListConnection) -> None:
        mock_response = Mock()
        mock_response.ok = True
        mock_response.json = {"type": "ListGetResponseADM", "list": {}}
        with patch.object(list_connection, "_get", return_value=mock_response) as patched_get:
            result = list_connection._get_one_list("http://rdfh.ch/lists/9999/WWqeCEj8R_qrK5djsVcHvg")
            assert result == {"type": "ListGetResponseADM", "list": {}}
            patched_get.assert_called_once_with(
                url="http://0.0.0.0:3333/admin/lists/http%3A%2F%2Frdfh.ch%2Flists%2F9999%2FWWqeCEj8R_qrK5djsVcHvg",
            )

    def test_get_one_list_non_ok_code(self, list_connection: ListConnection) -> None:
        with patch("requests.get") as patched_get:
            patched_get.return_value.ok = False
            with pytest.raises(UserError):
                list_connection._get_one_list("http://rdfh.ch/lists/9999/WWqeCEj8R_qrK5djsVcHvg")
            patched_get.assert_called_once_with(
                url="http://0.0.0.0:3333/admin/lists/http%3A%2F%2Frdfh.ch%2Flists%2F9999%2FWWqeCEj8R_qrK5djsVcHvg",
                headers=None,
                timeout=100,
            )

    def test_extract_list_iris(
        self, list_connection: ListConnection, response_all_list_one_project: dict[str, Any]
    ) -> None:
        extracted = list_connection._extract_list_iris(response_all_list_one_project)
        expected = {"http://rdfh.ch/lists/9999/list1", "http://rdfh.ch/lists/9999/list2"}
        assert set(extracted) == expected

    def test_extract_list_iris_no_lists(
        self, list_connection: ListConnection, response_all_list_one_project_no_lists: dict[str, Any]
    ) -> None:
        extracted = list_connection._extract_list_iris(response_all_list_one_project_no_lists)
        assert not extracted

    def test_reformat_one_list(self, list_connection: ListConnection, response_one_list: dict[str, Any]) -> None:
        reformatted = list_connection._reformat_one_list(response_one_list)
        expected_nodes = {"n1", "n1.1", "n1.1.1", "n1.1.2"}
        assert reformatted.list_iri == "http://rdfh.ch/lists/9999/list1"
        assert reformatted.list_name == "firstList"
        assert set(reformatted.nodes) == expected_nodes


if __name__ == "__main__":
    pytest.main([__file__])
