# pylint: disable=missing-class-docstring
# ruff: noqa: D102 (undocumented-public-method)

from dataclasses import dataclass, field
from test.unittests.commands.xmlupload.connection_mock import ConnectionMockBase
from typing import Any

from dsp_tools.commands.xmlupload.project_client import ProjectClientLive


@dataclass
class ConnectionMock(ConnectionMockBase):
    get_responses: list[dict[str, Any]] = field(default_factory=list)

    def get(self, route: str, headers: dict[str, str] | None = None) -> dict[str, Any]:
        return self.get_responses.pop(0)


class TestProjectClientLive:
    """Test the ProjectClientLive class."""

    def test_get_project_iri(self) -> None:
        project_iri_response = {"project": {"id": "http://www.example.org/projects#a"}}
        project_ontologies_response = {"@id": "http://www.example.org/ontologies/a.1/v2"}
        con = ConnectionMock([project_iri_response, project_ontologies_response])
        project_client = ProjectClientLive(con, "")
        project_iri = project_client.get_project_iri()
        expected = "http://www.example.org/projects#a"
        assert project_iri == expected

    def test_get_ontology_iris(self) -> None:
        project_iri_response = {"project": {"id": "http://www.example.org/projects#a"}}
        project_ontologies_response = {"@id": "http://www.example.org/ontologies/a.1/v2"}
        con = ConnectionMock([project_iri_response, project_ontologies_response])
        project_client = ProjectClientLive(con, "")
        ontology_iris = project_client.get_ontology_iris()
        expected = ["http://www.example.org/ontologies/a.1/v2"]
        assert ontology_iris == expected

    def test_get_ontology_name_dict(self) -> None:
        project_iri_response = {"project": {"id": "http://www.example.org/projects#a"}}
        project_ontologies_response = {
            "@graph": [
                {"@id": "http://www.example.org/ontologies/a.1/v2"},
                {"@id": "http://www.example.org/ontologies/a.2/v2"},
            ]
        }
        con = ConnectionMock([project_iri_response, project_ontologies_response])
        project_client = ProjectClientLive(con, "")
        ontology_name_dict = project_client.get_ontology_name_dict()
        expected = {
            "a.1": "http://www.example.org/ontologies/a.1/v2",
            "a.2": "http://www.example.org/ontologies/a.2/v2",
        }
        assert ontology_name_dict == expected

    def test_get_ontology_iri_dict(self) -> None:
        project_iri_response = {"project": {"id": "http://www.example.org/projects#a"}}
        project_ontologies_response = {
            "@graph": [
                {"@id": "http://www.example.org/ontologies/a.1/v2"},
                {"@id": "http://www.example.org/ontologies/a.2/v2"},
            ]
        }
        con = ConnectionMock([project_iri_response, project_ontologies_response])
        project_client = ProjectClientLive(con, "")
        ontology_iri_dict = project_client.get_ontology_iri_dict()
        expected = {
            "http://www.example.org/ontologies/a.1/v2": "a.1",
            "http://www.example.org/ontologies/a.2/v2": "a.2",
        }
        assert ontology_iri_dict == expected
