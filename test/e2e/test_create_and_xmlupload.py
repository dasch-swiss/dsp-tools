import urllib.parse
from pathlib import Path
from typing import Any
from typing import Iterator

import pytest
import requests

from dsp_tools.cli.args import ServerCredentials
from dsp_tools.commands.project.create.project_create import create_project
from dsp_tools.commands.xmlupload.xmlupload import xmlupload
from test.e2e.tools_testcontainers import get_containers

PROJECT_SHORTCODE = "4124"


@pytest.fixture()
def creds() -> ServerCredentials:
    return ServerCredentials("root@example.com", "test", "http://0.0.0.0:3333")


@pytest.fixture(autouse=True)
def project_created(creds: ServerCredentials) -> Iterator[bool]:
    with get_containers():
        yield create_project(Path("testdata/json-project/test-project-e2e.json"), creds, verbose=True)


@pytest.fixture()
def auth_header(creds: ServerCredentials, project_created: bool) -> dict[str, str]:  # noqa: ARG001
    payload = {"email": creds.user, "password": creds.password}
    token: str = requests.post(f"{creds.server}/v2/authentication", json=payload, timeout=3).json()["token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture()
def project_iri(creds: ServerCredentials, project_created: bool) -> str:  # noqa: ARG001
    get_project_route = f"{creds.server}/admin/projects/shortcode/{PROJECT_SHORTCODE}"
    project_iri: str = requests.get(get_project_route, timeout=3).json()["project"]["id"]
    return project_iri


@pytest.fixture()
def onto_iri(creds: ServerCredentials) -> str:
    return f"{creds.server}/ontology/{PROJECT_SHORTCODE}/testonto/v2"


def test_project(creds: ServerCredentials, auth_header: dict[str, str], project_created: bool, onto_iri: str) -> None:
    assert project_created

    get_project_url = f"{creds.server}/admin/projects/shortcode/{PROJECT_SHORTCODE}"
    project = requests.get(get_project_url, headers=auth_header, timeout=3).json()["project"]
    _check_project(project, onto_iri)

    onto = requests.get(onto_iri, headers=auth_header, timeout=3).json()["@graph"]
    _check_props([elem for elem in onto if elem.get("knora-api:isResourceProperty")])
    _check_resources([elem for elem in onto if elem.get("knora-api:isResourceClass")])


def _check_project(project: dict[str, Any], onto_iri: str) -> None:
    assert project["shortname"] == "minimal-tp"
    assert project["shortcode"] == PROJECT_SHORTCODE
    assert project["longname"] == "minimal test project"
    assert project["description"] == [{"value": "A minimal test project", "language": "en"}]
    assert project["keywords"] == ["minimal"]
    assert project["ontologies"] == [onto_iri]


def _check_props(props: list[dict[str, Any]]) -> None:
    assert len(props) == 1
    assert props[0]["@id"] == "testonto:hasText"
    assert props[0]["rdfs:subPropertyOf"] == {"@id": "knora-api:hasValue"}
    assert props[0]["knora-api:objectType"] == {"@id": "knora-api:TextValue"}
    assert props[0]["rdfs:label"] == "Text"


def _check_resources(resources: list[dict[str, Any]]) -> None:
    assert len(resources) == 2
    assert resources[0]["@id"] == "testonto:ImageResource"
    assert resources[0]["rdfs:label"] == "Image Resource"
    assert resources[1]["@id"] == "testonto:PDFResource"
    assert resources[1]["rdfs:label"] == "PDF Resource"
    assert any(
        card.get("owl:cardinality") == 1
        and card.get("owl:onProperty", {}).get("@id") == "knora-api:hasStillImageFileValue"
        for card in resources[0]["rdfs:subClassOf"]
    )
    assert any(
        card.get("owl:minCardinality") == 0 and card.get("owl:onProperty", {}).get("@id") == "testonto:hasText"
        for card in resources[0]["rdfs:subClassOf"]
    )


def test_xmlupload(
    creds: ServerCredentials, auth_header: dict[str, str], project_created: bool, project_iri: str, onto_iri: str
) -> None:
    assert project_created
    xmlupload_status = xmlupload(Path("testdata/xml-data/test-data-e2e.xml"), creds, ".")
    assert xmlupload_status

    img_resources = _get_resources(f"{onto_iri}#ImageResource", creds, auth_header, project_iri)
    _analyze_img_resources(img_resources)
    pdf_resources = _get_resources(f"{onto_iri}#PDFResource", creds, auth_header, project_iri)
    _analyze_pdf_resources(pdf_resources)


def _get_resources(
    resclass_iri: str, creds: ServerCredentials, auth_header: dict[str, str], project_iri: str
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
    assert res_1.get("knora-api:hasStillImageFileValue")

    res_2 = next(res for res in img_resources if res["rdfs:label"] == "Resource 2")
    assert res_2.get("knora-api:hasStillImageFileValue")
    res_2_text_vals = sorted([x["knora-api:valueAsString"] for x in res_2["testonto:hasText"]])
    assert res_2_text_vals == ["first text value", "second text value"]


def _analyze_pdf_resources(pdf_resources: list[dict[str, Any]]) -> None:
    res_labels = sorted([res["rdfs:label"] for res in pdf_resources])
    assert res_labels == ["Resource 3"]
    res_1 = next(res for res in pdf_resources if res["rdfs:label"] == "Resource 3")
    assert res_1.get("knora-api:hasDocumentFileValue")
