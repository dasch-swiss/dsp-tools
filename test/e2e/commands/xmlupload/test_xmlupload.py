# mypy: disable-error-code="no-untyped-def"

import json
import urllib.parse
from pathlib import Path

import pytest
import requests
from rdflib import Graph

from dsp_tools.commands.xmlupload.xmlupload import xmlupload

PROJECT_SHORTCODE = "9999"
ONTO_NAME = "onto"
SECOND_ONTO = "second-onto"


@pytest.fixture(scope="module")
def project_iri(_create_project: None, creds) -> str:
    get_project_route = f"{creds.server}/admin/projects/shortcode/{PROJECT_SHORTCODE}"
    project_iri: str = requests.get(get_project_route, timeout=3).json()["project"]["id"]
    return project_iri


@pytest.fixture(scope="module")
def onto_iri(creds) -> str:
    return f"{creds.server}/ontology/{PROJECT_SHORTCODE}/{ONTO_NAME}/v2"


@pytest.fixture(scope="module")
def second_onto_iri(creds) -> str:
    return f"{creds.server}/ontology/{PROJECT_SHORTCODE}/{SECOND_ONTO}/v2"


@pytest.fixture(scope="module")
def _xmlupload(_create_project: None, creds) -> None:
    assert xmlupload(Path("testdata/validate-data/generic/minimal_correct.xml"), creds, ".")


@pytest.fixture(scope="module")
def auth_header(_create_project: None, creds) -> dict[str, str]:
    payload = {"email": creds.user, "password": creds.password}
    token: str = requests.post(f"{creds.server}/v2/authentication", json=payload, timeout=3).json()["token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(scope="module")
def class_with_everything_resource_graph(_xmlupload, onto_iri, auth_header, project_iri, creds) -> Graph:
    class_iri = f"{onto_iri}ClassWithEverything"
    resources = _util_request_resources_by_class(class_iri, auth_header, project_iri, creds)
    g = Graph()
    g.parse(data=resources, format="json-ld")
    return g


def _util_request_resources_by_class(resclass_iri: str, auth_header: dict[str, str], project_iri: str, creds) -> str:
    resclass_iri_encoded = urllib.parse.quote_plus(resclass_iri)
    get_resources_route = f"{creds.server}/v2/resources?resourceClass={resclass_iri_encoded}&page=0"
    headers = auth_header | {"X-Knora-Accept-Project": project_iri}
    response = requests.get(get_resources_route, timeout=3, headers=headers).json()
    resources = json.dumps(response)
    return resources


class TestResources:
    def test_class_with_everything_all_created(self, class_with_everything_resource_graph):
        assert len(class_with_everything_resource_graph) != 0
