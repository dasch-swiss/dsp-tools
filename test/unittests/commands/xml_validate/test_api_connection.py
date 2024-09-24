from unittest.mock import Mock
from unittest.mock import patch

import pytest

from dsp_tools.commands.xml_validate.api_connection import OntologyConnection
from dsp_tools.models.exceptions import UserError


@pytest.fixture
def ontology_connection() -> OntologyConnection:
    return OntologyConnection("http://example.com", "9999")


def test_get_ontology_iris_ok(ontology_connection: OntologyConnection) -> None:
    mock_response = Mock()
    mock_response.ok = True
    mock_response.json.return_value = {"ontologies": ["onto_iri"]}
    with patch.object(ontology_connection, "get", return_value=mock_response):
        result = ontology_connection._get_ontology_iris()
        assert result == ["onto_iri"]


def test_get_ontology_iris_non_ok_code(ontology_connection: OntologyConnection) -> None:
    mock_response = Mock()
    mock_response.ok = False
    mock_response.json.return_value = {}
    with patch.object(ontology_connection, "get", return_value=mock_response):
        with pytest.raises(UserError):
            ontology_connection._get_ontology_iris()


def test_get_ontology_iris_no_ontology_key(ontology_connection: OntologyConnection) -> None:
    mock_response = Mock()
    mock_response.ok = True
    mock_response.json.return_value = {}
    with patch.object(ontology_connection, "get", return_value=mock_response):
        with pytest.raises(UserError):
            ontology_connection._get_ontology_iris()


def test_get_one_ontology(ontology_connection: OntologyConnection) -> None:
    mock_response = Mock()
    mock_response.ok = True
    mock_response.text = "Turtle Text"
    with patch.object(ontology_connection, "get", return_value=mock_response):
        result = ontology_connection._get_one_ontology("iri")
        assert result == "Turtle Text"


if __name__ == "__main__":
    pytest.main([__file__])
