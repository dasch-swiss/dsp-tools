import urllib.parse
from collections.abc import Iterator
from pathlib import Path
from typing import Any

import pytest
import requests
from pytest_unordered import unordered

from dsp_tools.cli.args import ServerCredentials
from dsp_tools.commands.project.create.project_create_all import create_project
from test.e2e.setup_testcontainers.ports import ExternalContainerPorts
from test.e2e.setup_testcontainers.setup import get_containers

PROJECT_SHORTCODE = "4125"
E2E_TESTONTO_PREFIX = "e2e-testonto"
SECOND_ONTO_PREFIX = "second-onto"
PROPS_IN_ONTO_JSON = 1
RESCLASSES_IN_ONTO_JSON = 2
USER_IRI_PREFIX = "http://www.knora.org/ontology/knora-admin#"


@pytest.fixture(scope="module")
def container_ports() -> Iterator[ExternalContainerPorts]:
    with get_containers() as metadata:
        yield metadata.ports


@pytest.fixture(scope="module")
def creds(container_ports: ExternalContainerPorts) -> ServerCredentials:
    return ServerCredentials(
        "root@example.com",
        "test",
        f"http://0.0.0.0:{container_ports.api}",
        f"http://0.0.0.0:{container_ports.ingest}",
    )


@pytest.fixture(scope="module")
def e2e_testonto_iri(creds: ServerCredentials) -> str:
    return f"{creds.server}/ontology/{PROJECT_SHORTCODE}/{E2E_TESTONTO_PREFIX}/v2"


@pytest.fixture(scope="module")
def second_onto_iri(creds: ServerCredentials) -> str:
    return f"{creds.server}/ontology/{PROJECT_SHORTCODE}/{SECOND_ONTO_PREFIX}/v2"


@pytest.fixture(scope="module")
def _create_project(creds: ServerCredentials) -> None:
    assert create_project(Path("testdata/json-project/test-project-e2e.json"), creds, verbose=True)


@pytest.fixture(scope="module")
def auth_header(_create_project: None, creds: ServerCredentials) -> dict[str, str]:
    payload = {"email": creds.user, "password": creds.password}
    token: str = requests.post(f"{creds.server}/v2/authentication", json=payload, timeout=3).json()["token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(scope="module")
def project_iri(_create_project: None, creds: ServerCredentials) -> str:
    get_project_route = f"{creds.server}/admin/projects/shortcode/{PROJECT_SHORTCODE}"
    project_iri: str = requests.get(get_project_route, timeout=3).json()["project"]["id"]
    return project_iri


@pytest.mark.usefixtures("_create_project")
def test_project(
    auth_header: dict[str, str], creds: ServerCredentials, e2e_testonto_iri: str, second_onto_iri: str
) -> None:
    get_project_url = f"{creds.server}/admin/projects/shortcode/{PROJECT_SHORTCODE}"
    project = requests.get(get_project_url, headers=auth_header, timeout=3).json()["project"]
    _check_project(project, e2e_testonto_iri, second_onto_iri)

    onto = requests.get(e2e_testonto_iri, headers=auth_header, timeout=3).json()["@graph"]
    _check_props([elem for elem in onto if elem.get("knora-api:isResourceProperty")])
    _check_resclasses([elem for elem in onto if elem.get("knora-api:isResourceClass")])


@pytest.mark.usefixtures("_create_project")
def test_all_get_licenses_enabled(auth_header: dict[str, str], creds: ServerCredentials) -> None:
    response = _get_enabled_licenses(auth_header, creds)
    all_ids = {x["id"] for x in response["data"]}
    assert all_ids == {"http://rdfh.ch/licenses/cc-by-4.0", "http://rdfh.ch/licenses/cc-by-nc-4.0"}


@pytest.mark.usefixtures("_create_project")
def test_default_permissions(creds: ServerCredentials, project_iri: str, auth_header: dict[str, str]) -> None:
    response = requests.get(
        f"{creds.server}/admin/permissions/doap/{urllib.parse.quote_plus(project_iri)}", headers=auth_header, timeout=3
    )
    doaps = response.json()["default_object_access_permissions"]
    assert len(doaps) == 1  # As soon as per-class DOAPs are supported, there will be more

    # The first DOAP is the public one
    assert doaps[0]["forGroup"] == f"{USER_IRI_PREFIX}ProjectMember"
    expected_permissions = [
        {"additionalInformation": f"{USER_IRI_PREFIX}ProjectAdmin", "name": "CR", "permissionCode": 8},
        {"additionalInformation": f"{USER_IRI_PREFIX}ProjectMember", "name": "D", "permissionCode": 7},
        {"additionalInformation": f"{USER_IRI_PREFIX}KnownUser", "name": "V", "permissionCode": 2},
        {"additionalInformation": f"{USER_IRI_PREFIX}UnknownUser", "name": "V", "permissionCode": 2},
    ]
    assert unordered(doaps[0]["hasPermissions"]) == expected_permissions

    # For each class/property which defines their own permissions, there will be a separate DOAP
    pass  # noqa: PIE790


def _get_enabled_licenses(auth_header: dict[str, str], creds: ServerCredentials) -> dict[str, Any]:
    url = (
        f"{creds.server}/admin/projects/shortcode/4125/legal-info/"
        f"licenses?page=1&page-size=25&order=Asc&showOnlyEnabled=true"
    )
    headers = auth_header | {"Accept": "application/json"}
    response = requests.get(url=url, headers=headers, timeout=3).json()
    return dict(response)


def _check_project(project: dict[str, Any], onto_iri: str, second_onto_iri: str) -> None:
    assert project["shortname"] == "e2e-tp"
    assert project["shortcode"] == PROJECT_SHORTCODE
    assert project["longname"] == "e2e test project"
    assert project["description"] == [{"value": "The e2e test project", "language": "en"}]
    assert project["keywords"] == ["e2e-test-project-keyword"]
    assert project["ontologies"] == [onto_iri, second_onto_iri]


def _check_props(props: list[dict[str, Any]]) -> None:
    assert len(props) == PROPS_IN_ONTO_JSON
    assert props[0]["@id"] == f"{E2E_TESTONTO_PREFIX}:hasText"
    assert props[0]["rdfs:subPropertyOf"] == {"@id": "knora-api:hasValue"}
    assert props[0]["knora-api:objectType"] == {"@id": "knora-api:TextValue"}
    assert props[0]["rdfs:label"] == "Text"


def _check_resclasses(resclasses: list[dict[str, Any]]) -> None:
    assert len(resclasses) == RESCLASSES_IN_ONTO_JSON
    res_1, res_2 = resclasses

    assert res_1["@id"] == f"{E2E_TESTONTO_PREFIX}:ImageResource"
    assert res_1["rdfs:label"] == "Image Resource"
    cards_1 = res_1["rdfs:subClassOf"]
    fileval_card = [x for x in cards_1 if x.get("owl:onProperty", {}).get("@id") == "knora-api:hasStillImageFileValue"]
    assert len(fileval_card) == 1
    assert fileval_card[0].get("owl:cardinality") == 1
    hasText_card = [x for x in cards_1 if x.get("owl:onProperty", {}).get("@id") == f"{E2E_TESTONTO_PREFIX}:hasText"]
    assert len(hasText_card) == 1

    assert res_2["@id"] == f"{E2E_TESTONTO_PREFIX}:PDFResource"
    assert res_2["rdfs:label"] == "PDF Resource"
