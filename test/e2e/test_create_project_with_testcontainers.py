import urllib.parse
from pathlib import Path
from typing import Iterator

import pytest
import requests

from dsp_tools.cli.args import ServerCredentials
from dsp_tools.commands.project.create.project_create import create_project
from dsp_tools.commands.xmlupload.xmlupload import xmlupload
from test.tools_testcontainers import get_containers

PROJECT_SHORTCODE = "4124"


@pytest.fixture()
def creds() -> ServerCredentials:
    return ServerCredentials("root@example.com", "test", "http://0.0.0.0:3333")


@pytest.fixture(autouse=True)
def project(creds: ServerCredentials) -> Iterator[bool]:
    with get_containers():
        yield create_project(Path("testdata/json-project/test-project-e2e.json"), creds, verbose=True)


@pytest.fixture()
def token(creds: ServerCredentials, project: bool) -> str:  # noqa: ARG001
    payload = {"email": creds.user, "password": creds.password}
    token: str = requests.post(f"{creds.server}/v2/authentication", json=payload, timeout=3).json()["token"]
    return token


@pytest.mark.usefixtures("project")
def testproject(creds: ServerCredentials, token: str) -> None:
    get_project_url = f"{creds.server}/admin/projects/shortcode/{PROJECT_SHORTCODE}"
    onto_iri = f"{creds.server}/ontology/{PROJECT_SHORTCODE}/testonto/v2"

    get_project_response = requests.get(get_project_url, headers={"Authorization": f"Bearer {token}"}, timeout=3)
    project = get_project_response.json()["project"]
    assert project["shortname"] == "minimal-tp"
    assert project["shortcode"] == PROJECT_SHORTCODE
    assert project["longname"] == "minimal test project"
    assert project["description"] == [{"value": "A minimal test project", "language": "en"}]
    assert project["keywords"] == ["minimal"]
    assert project["ontologies"] == [onto_iri]

    get_onto_response = requests.get(onto_iri, headers={"Authorization": f"Bearer {token}"}, timeout=3)
    onto = get_onto_response.json()["@graph"]
    props = [elem for elem in onto if elem.get("knora-api:isResourceProperty")]
    assert len(props) == 1
    assert props[0]["@id"] == "testonto:hasText"
    assert props[0]["rdfs:subPropertyOf"] == {"@id": "knora-api:hasValue"}
    assert props[0]["knora-api:objectType"] == {"@id": "knora-api:TextValue"}
    assert props[0]["rdfs:label"] == "Text"

    resources = [elem for elem in onto if elem.get("knora-api:isResourceClass")]
    assert len(resources) == 1
    assert resources[0]["@id"] == "testonto:minimalResource"
    assert resources[0]["rdfs:label"] == "Minimal Resource"
    assert resources[0]["@id"] == "testonto:minimalResource"


@pytest.mark.usefixtures("project")
def test_xmlupload(creds: ServerCredentials, token: str) -> None:
    success = xmlupload(Path("testdata/xml-data/test-data-e2e.xml"), creds, ".")
    assert success

    resclass_iri = "http://0.0.0.0:3333/ontology/4124/testonto/v2#minimalResource"
    resclass_iri_encoded = urllib.parse.quote_plus(resclass_iri)

    get_project_route = f"{creds.server}/admin/projects/shortcode/{PROJECT_SHORTCODE}"
    project_iri = requests.get(get_project_route, timeout=3).json()["project"]["id"]
    get_resources_route = f"{creds.server}/v2/resources?resourceClass={resclass_iri_encoded}&page=0"
    headers = {"X-Knora-Accept-Project": project_iri, "Authorization": f"Bearer {token}"}
    response = requests.get(get_resources_route, timeout=3, headers=headers).json()
    res_iris = [x["@id"] for x in response["@graph"]]
    assert len(res_iris) == 2
