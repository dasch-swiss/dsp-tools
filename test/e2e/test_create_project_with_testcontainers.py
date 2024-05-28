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


def test_create_project(containers: Containers) -> None:  # noqa: ARG001
    api = "http://0.0.0.0:3333"
    user = "root@example.com"
    pw = "test"
    creds = ServerCredentials(user, pw, api)
    test_project_minimal_file = Path("testdata/json-project/test-project-minimal.json")
    created = create_project(
        project_file_as_path_or_parsed=test_project_minimal_file.absolute(),
        creds=creds,
        verbose=True,
    )
    assert created

    get_project_url = f"{api}/admin/projects/shortcode/4124"
    onto_iri = "http://0.0.0.0:3333/ontology/4124/testonto/v2"
    token = requests.post(f"{api}/v2/authentication", json={"email": user, "password": pw}, timeout=3).json()["token"]

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
