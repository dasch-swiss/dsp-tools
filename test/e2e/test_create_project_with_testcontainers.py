from pathlib import Path
from typing import Iterator

import pytest
import requests

from dsp_tools.cli.args import ServerCredentials
from dsp_tools.commands.project.create.project_create import create_project
from test.tools_testcontainers import Containers
from test.tools_testcontainers import get_containers


@pytest.fixture()
def containers() -> Iterator[Containers]:
    with get_containers() as containers:
        yield containers


@pytest.fixture()
def creds() -> ServerCredentials:
    return ServerCredentials("root@example.com", "test", "http://0.0.0.0:3333")


@pytest.fixture()
def token(creds: ServerCredentials) -> str:
    payload = {"email": creds.user, "password": creds.password}
    token: str = requests.post(f"{creds.server}/v2/authentication", json=payload, timeout=3).json()["token"]
    return token


def test_create_project(containers: Containers, creds: ServerCredentials, token: str) -> None:  # noqa: ARG001
    test_project_minimal_file = Path("testdata/json-project/test-project-minimal.json")
    created = create_project(
        project_file_as_path_or_parsed=test_project_minimal_file.absolute(),
        creds=creds,
        verbose=True,
    )
    assert created

    get_project_url = f"{creds.server}/admin/projects/shortcode/4124"
    onto_iri = f"{creds.server}/ontology/4124/testonto/v2"

    get_project_response = requests.get(get_project_url, headers={"Authorization": f"Bearer {token}"}, timeout=3)
    project = get_project_response.json()["project"]
    assert project["shortname"] == "minimal-tp"
    assert project["shortcode"] == "4124"
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
