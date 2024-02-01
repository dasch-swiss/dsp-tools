import pytest

from dsp_tools.commands.xmlupload.project_client import ProjectClient, ProjectClientLive
from dsp_tools.utils.connection_live import ConnectionLive


@pytest.fixture()
def project_client() -> ProjectClient:
    con = ConnectionLive("http://localhost:3333")
    con.login("root@example.com", "test")
    return ProjectClientLive(con, "0001")


def test_get_project_iri(project_client: ProjectClient) -> None:
    project_iri = project_client.get_project_iri()
    assert project_iri == "http://rdfh.ch/projects/0001"


def test_get_ontology_name_dict(project_client: ProjectClient) -> None:
    ontology_name_dict = project_client.get_ontology_name_dict()
    expected_key = "anything"
    expected_val = "http://0.0.0.0:3333/ontology/0001/anything/v2"
    assert ontology_name_dict[expected_key] == expected_val


def test_get_ontology_iri_dict(project_client: ProjectClient) -> None:
    ontology_iri_dict = project_client.get_ontology_iri_dict()
    expected_key = "http://0.0.0.0:3333/ontology/0001/anything/v2"
    expected_val = "anything"
    assert ontology_iri_dict[expected_key] == expected_val
