import urllib.parse
from pathlib import Path
from typing import Any
from typing import Iterator

import pytest
import requests

from dsp_tools.cli.args import ServerCredentials
from dsp_tools.commands.project.create.project_create_all import create_project
from dsp_tools.commands.xmlupload.xmlupload import xmlupload
from test.e2e.setup_testcontainers.ports import ExternalContainerPorts
from test.e2e.setup_testcontainers.setup import get_containers

PROJECT_SHORTCODE = "4125"
ONTO_NAME = "e2e-testonto"
PROPS_IN_ONTO_JSON = 1
RESCLASSES_IN_ONTO_JSON = 2


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
def onto_iri(creds: ServerCredentials) -> str:
    return f"{creds.server}/ontology/{PROJECT_SHORTCODE}/{ONTO_NAME}/v2"


@pytest.fixture(scope="module")
def _create_project(creds: ServerCredentials) -> None:
    assert create_project(Path("testdata/json-project/test-project-e2e.json"), creds, verbose=True)


@pytest.fixture(scope="module")
def _xmlupload(_create_project: None, creds: ServerCredentials) -> Iterator[None]:
    assert xmlupload(Path("testdata/xml-data/test-data-e2e.xml"), creds, ".")
    yield
    if found := list(Path.cwd().glob(f"id2iri_{PROJECT_SHORTCODE}_localhost_*.json")):
        found[0].unlink()


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
def test_project(auth_header: dict[str, str], creds: ServerCredentials, onto_iri: str) -> None:
    get_project_url = f"{creds.server}/admin/projects/shortcode/{PROJECT_SHORTCODE}"
    project = requests.get(get_project_url, headers=auth_header, timeout=3).json()["project"]
    _check_project(project, onto_iri)

    onto = requests.get(onto_iri, headers=auth_header, timeout=3).json()["@graph"]
    _check_props([elem for elem in onto if elem.get("knora-api:isResourceProperty")])
    _check_resclasses([elem for elem in onto if elem.get("knora-api:isResourceClass")])


@pytest.mark.usefixtures("_xmlupload")
def test_xmlupload(auth_header: dict[str, str], project_iri: str, creds: ServerCredentials, onto_iri: str) -> None:
    img_resources = _get_resources(f"{onto_iri}#ImageResource", auth_header, project_iri, creds)
    _analyze_img_resources(img_resources)
    pdf_resources = _get_resources(f"{onto_iri}#PDFResource", auth_header, project_iri, creds)
    _analyze_pdf_resources(pdf_resources)


@pytest.mark.usefixtures("_xmlupload")
def test_all_copyright_holders(auth_header: dict[str, str], creds: ServerCredentials) -> None:
    response = _get_copyright_holders(auth_header, creds)
    assert response["data"] == ["DaSCH"]


def _get_copyright_holders(auth_header: dict[str, str], creds: ServerCredentials) -> dict[str, Any]:
    url = f"{creds.server}/admin/projects/shortcode/4125/legal-info/copyright-holders?page=1&page-size=25&order=Asc"
    headers = auth_header | {"Accept": "application/json"}
    response = requests.get(url=url, headers=headers, timeout=3).json()
    return dict(response)


def _check_project(project: dict[str, Any], onto_iri: str) -> None:
    assert project["shortname"] == "e2e-tp"
    assert project["shortcode"] == PROJECT_SHORTCODE
    assert project["longname"] == "e2e test project"
    assert project["description"] == [{"value": "The e2e test project", "language": "en"}]
    assert project["keywords"] == ["e2e-test-projec-keyword"]
    assert project["ontologies"] == [onto_iri]


def _check_props(props: list[dict[str, Any]]) -> None:
    assert len(props) == PROPS_IN_ONTO_JSON
    assert props[0]["@id"] == f"{ONTO_NAME}:hasText"
    assert props[0]["rdfs:subPropertyOf"] == {"@id": "knora-api:hasValue"}
    assert props[0]["knora-api:objectType"] == {"@id": "knora-api:TextValue"}
    assert props[0]["rdfs:label"] == "Text"


def _check_resclasses(resclasses: list[dict[str, Any]]) -> None:
    assert len(resclasses) == RESCLASSES_IN_ONTO_JSON
    res_1, res_2 = resclasses

    assert res_1["@id"] == f"{ONTO_NAME}:ImageResource"
    assert res_1["rdfs:label"] == "Image Resource"
    cards_1 = res_1["rdfs:subClassOf"]
    fileval_card = [x for x in cards_1 if x.get("owl:onProperty", {}).get("@id") == "knora-api:hasStillImageFileValue"]
    assert len(fileval_card) == 1
    assert fileval_card[0].get("owl:cardinality") == 1
    hasText_card = [x for x in cards_1 if x.get("owl:onProperty", {}).get("@id") == f"{ONTO_NAME}:hasText"]
    assert len(hasText_card) == 1

    assert res_2["@id"] == f"{ONTO_NAME}:PDFResource"
    assert res_2["rdfs:label"] == "PDF Resource"


def _get_resources(
    resclass_iri: str, auth_header: dict[str, str], project_iri: str, creds: ServerCredentials
) -> list[dict[str, Any]]:
    resclass_iri_encoded = urllib.parse.quote_plus(resclass_iri)
    get_resources_route = f"{creds.server}/v2/resources?resourceClass={resclass_iri_encoded}&page=0"
    headers = auth_header | {"X-Knora-Accept-Project": project_iri}
    response = requests.get(get_resources_route, timeout=3, headers=headers).json()
    resources: list[dict[str, Any]] = response.get("@graph", [response])
    return resources


def _analyze_img_resources(img_resources: list[dict[str, Any]]) -> None:
    res_labels = sorted([res["rdfs:label"] for res in img_resources])
    assert res_labels == ["Resource 1", "Resource 2"]

    res_1 = next(res for res in img_resources if res["rdfs:label"] == "Resource 1")
    file_val = res_1["knora-api:hasStillImageFileValue"]
    assert file_val["knora-api:hasAuthorship"] == "Johannes Nussbaum"
    assert file_val["knora-api:hasCopyrightHolder"] == "DaSCH"
    assert file_val["knora-api:hasLicense"]["@id"] == "http://rdfh.ch/licenses/cc-by-4.0"

    res_2 = next(res for res in img_resources if res["rdfs:label"] == "Resource 2")
    assert res_2.get("knora-api:hasStillImageFileValue")
    res_2_text_vals = sorted([x["knora-api:valueAsString"] for x in res_2[f"{ONTO_NAME}:hasText"]])
    assert res_2_text_vals == ["first text value", "second text value"]


def _analyze_pdf_resources(pdf_resources: list[dict[str, Any]]) -> None:
    res_labels = sorted([res["rdfs:label"] for res in pdf_resources])
    assert res_labels == ["Resource 3"]
    res_1 = next(res for res in pdf_resources if res["rdfs:label"] == "Resource 3")
    assert res_1.get("knora-api:hasDocumentFileValue")
