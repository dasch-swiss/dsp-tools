from pathlib import Path

import pytest
import requests

from dsp_tools.cli.args import ServerCredentials
from dsp_tools.commands.project.create.project_create import create_project
from test.tools_testcontainers import Containers
from test.tools_testcontainers import get_containers


@pytest.fixture()
def containers() -> Containers:  # type: ignore[misc]
    with get_containers() as containers:
        yield containers


def test_create_project(containers: Containers) -> None:  # noqa: ARG001
    api = "http://0.0.0.0:3333"
    user = "root@example.com"
    pw = "test"
    creds = ServerCredentials(user, pw, api)
    get_url = f"{api}/admin/projects/shortcode/4124"
    test_project_minimal_file = Path("testdata/json-project/test-project-minimal.json")
    token = requests.post(f"{api}/v2/authentication", json={"email": user, "password": pw}, timeout=3).json()["token"]
    created = create_project(
        project_file_as_path_or_parsed=test_project_minimal_file.absolute(),
        creds=creds,
        verbose=True,
    )
    assert created
    response = requests.get(get_url, headers={"Authorization": f"Bearer {token}"}, timeout=3)
    assert response.ok
    json = response.json()
    project = json["project"]
    assert project["shortname"] == "minimal-tp"
    assert project["shortcode"] == "4124"
    assert project["ontologies"] == ["http://0.0.0.0:3333/ontology/4124/testonto/v2"]
