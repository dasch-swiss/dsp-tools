from pytest import fixture

from dsp_tools.connection.connection_live import ConnectionLive
from dsp_tools.utils.xmlupload.project_client import ProjectClient, ProjectClientLive

# pylint: disable=missing-function-docstring,redefined-outer-name


@fixture
def project_client() -> ProjectClient:
    con = ConnectionLive("http://localhost:3333")
    con.login("root@example.com", "test")
    return ProjectClientLive(con, "0001")


def test_get_project_iri(project_client: ProjectClient) -> None:
    project_iri = project_client.get_project_iri()
    assert project_iri == "http://rdfh.ch/projects/0001"


def test_get_ontology_iris(project_client: ProjectClient) -> None:
    ontology_iris = project_client.get_ontology_iris()
    expected = ["http://0.0.0.0:3333/ontology/0001/anything/v2"]
    assert ontology_iris == expected


def test_get_ontology_name_dict(project_client: ProjectClient) -> None:
    ontology_name_dict = project_client.get_ontology_name_dict()
    expected = {"anything": "http://0.0.0.0:3333/ontology/0001/anything/v2"}
    assert ontology_name_dict == expected


def test_get_ontology_iri_dict(project_client: ProjectClient) -> None:
    ontology_name_dict = project_client.get_ontology_iri_dict()
    expected = {"http://0.0.0.0:3333/ontology/0001/anything/v2": "anything"}
    assert ontology_name_dict == expected
