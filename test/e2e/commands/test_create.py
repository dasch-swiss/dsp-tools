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


@pytest.fixture(scope="module")
def private_permissions() -> list[dict[str, Any]]:
    return [
        {"additionalInformation": f"{USER_IRI_PREFIX}ProjectAdmin", "name": "CR", "permissionCode": 8},
        {"additionalInformation": f"{USER_IRI_PREFIX}ProjectMember", "name": "D", "permissionCode": 7},
    ]


@pytest.fixture(scope="module")
def public_permissions() -> list[dict[str, Any]]:
    return [
        {"additionalInformation": f"{USER_IRI_PREFIX}ProjectAdmin", "name": "CR", "permissionCode": 8},
        {"additionalInformation": f"{USER_IRI_PREFIX}ProjectMember", "name": "D", "permissionCode": 7},
        {"additionalInformation": f"{USER_IRI_PREFIX}KnownUser", "name": "V", "permissionCode": 2},
        {"additionalInformation": f"{USER_IRI_PREFIX}UnknownUser", "name": "V", "permissionCode": 2},
    ]


@pytest.fixture(scope="module")
def limited_view_permissions() -> list[dict[str, Any]]:
    return [
        {"additionalInformation": f"{USER_IRI_PREFIX}ProjectAdmin", "name": "CR", "permissionCode": 8},
        {"additionalInformation": f"{USER_IRI_PREFIX}ProjectMember", "name": "D", "permissionCode": 7},
        {"additionalInformation": f"{USER_IRI_PREFIX}KnownUser", "name": "RV", "permissionCode": 1},
        {"additionalInformation": f"{USER_IRI_PREFIX}UnknownUser", "name": "RV", "permissionCode": 1},
    ]


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
def test_default_permissions(
    creds: ServerCredentials,
    project_iri: str,
    auth_header: dict[str, str],
    private_permissions: list[dict[str, Any]],
    public_permissions: list[dict[str, Any]],
    limited_view_permissions: list[dict[str, Any]],
) -> None:
    response = requests.get(
        f"{creds.server}/admin/permissions/doap/{urllib.parse.quote_plus(project_iri)}", headers=auth_header, timeout=3
    )
    doaps: list[dict[str, Any]] = response.json()["default_object_access_permissions"]
    NUM_OF_OVERRULES_IN_JSON_FILE = 3
    assert len(doaps) == NUM_OF_OVERRULES_IN_JSON_FILE + 1

    # There is only one standard public DOAP
    public_doap = next(filter(lambda x: x.get("forGroup", "") == f"{USER_IRI_PREFIX}ProjectMember", doaps))
    assert unordered(public_doap["hasPermissions"]) == public_permissions
    assert not public_doap.get("forResourceClass")
    assert not public_doap.get("forProperty")

    # DOAP for resource class: only for class
    priv_res_doap = next(filter(lambda x: x.get("forResourceClass", "").endswith("PrivatePermissionsResource"), doaps))
    assert unordered(priv_res_doap["hasPermissions"]) == private_permissions
    assert not priv_res_doap.get("forProperty")
    assert not priv_res_doap.get("forGroup")

    # DOAP for property: only for property
    priv_prop_doap = next(filter(lambda x: x.get("forProperty", "").endswith("privateProp"), doaps))
    assert unordered(priv_prop_doap["hasPermissions"]) == private_permissions
    assert not priv_prop_doap.get("forResourceClass")
    assert not priv_prop_doap.get("forGroup")

    # DOAP for image: not only for class, but also for knora-base:hasStillImageFileValue
    limited_view_doap = next(filter(lambda x: x.get("forResourceClass", "").endswith("ImageResource"), doaps))
    assert unordered(limited_view_doap["hasPermissions"]) == limited_view_permissions
    assert limited_view_doap["forProperty"] == "http://www.knora.org/ontology/knora-base#hasStillImageFileValue"
    assert not limited_view_doap.get("forGroup")


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
