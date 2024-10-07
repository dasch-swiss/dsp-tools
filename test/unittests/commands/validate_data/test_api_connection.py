from unittest.mock import Mock
from unittest.mock import patch

import pytest

from dsp_tools.commands.validate_data.api_connection import OntologyConnection
from dsp_tools.models.exceptions import UserError


@pytest.fixture
def ontology_connection() -> OntologyConnection:
    return OntologyConnection("http://0.0.0.0:3333", "9999")


def test_get_ontology_iris_ok(ontology_connection: OntologyConnection) -> None:
    mock_response = Mock()
    mock_response.ok = True
    mock_response.json.return_value = {"project": {"ontologies": ["onto_iri"]}}
    with patch.object(ontology_connection, "_get", return_value=mock_response) as patched_get:
        result = ontology_connection._get_ontology_iris()
        assert result == ["onto_iri"]
        patched_get.assert_called_once_with("http://0.0.0.0:3333/admin/projects/shortcode/9999")


def test_get_ontology_iris_non_ok_code(ontology_connection: OntologyConnection) -> None:
    mock_response = Mock()
    mock_response.ok = False
    mock_response.json.return_value = {}
    with patch.object(ontology_connection, "_get", return_value=mock_response) as patched_get:
        with pytest.raises(UserError):
            ontology_connection._get_ontology_iris()
        patched_get.assert_called_once_with("http://0.0.0.0:3333/admin/projects/shortcode/9999")


def test_get_ontology_iris_no_ontology_key(ontology_connection: OntologyConnection) -> None:
    mock_response = Mock()
    mock_response.ok = True
    mock_response.json.return_value = {}
    with patch.object(ontology_connection, "_get", return_value=mock_response) as patched_get:
        with pytest.raises(UserError):
            ontology_connection._get_ontology_iris()
        patched_get.assert_called_once_with("http://0.0.0.0:3333/admin/projects/shortcode/9999")


def test_get_one_ontology(ontology_connection: OntologyConnection) -> None:
    mock_response = Mock()
    mock_response.ok = True
    mock_response.text = "Turtle Text"
    with patch.object(ontology_connection, "_get", return_value=mock_response) as patched_get:
        result = ontology_connection._get_one_ontology("iri")
        assert result == "Turtle Text"
        patched_get.assert_called_once_with("iri", headers={"Accept": "text/turtle"})


if __name__ == "__main__":
    pytest.main([__file__])
