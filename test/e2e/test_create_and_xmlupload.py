import json
import urllib.parse
from collections.abc import Iterator
from pathlib import Path
from typing import Any

import pytest
import requests
from rdflib import RDF
from rdflib import RDFS
from rdflib import Graph
from rdflib import Literal
from rdflib import URIRef

from dsp_tools.cli.args import ServerCredentials
from dsp_tools.commands.project.create.project_create_all import create_project
from dsp_tools.commands.xmlupload.xmlupload import xmlupload
from dsp_tools.utils.rdflib_constants import KNORA_API
from test.e2e.setup_testcontainers.ports import ExternalContainerPorts
from test.e2e.setup_testcontainers.setup import get_containers

PROJECT_SHORTCODE = "4125"
E2E_TESTONTO_PREFIX = "e2e-testonto"
SECOND_ONTO_PREFIX = "second-onto"
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
def e2e_testonto_iri(creds: ServerCredentials) -> str:
    return f"{creds.server}/ontology/{PROJECT_SHORTCODE}/{E2E_TESTONTO_PREFIX}/v2"


@pytest.fixture(scope="module")
def second_onto_iri(creds: ServerCredentials) -> str:
    return f"{creds.server}/ontology/{PROJECT_SHORTCODE}/{SECOND_ONTO_PREFIX}/v2"


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


def _get_enabled_licenses(auth_header: dict[str, str], creds: ServerCredentials) -> dict[str, Any]:
    url = (
        f"{creds.server}/admin/projects/shortcode/4125/legal-info/"
        f"licenses?page=1&page-size=25&order=Asc&showOnlyEnabled=true"
    )
    headers = auth_header | {"Accept": "application/json"}
    response = requests.get(url=url, headers=headers, timeout=3).json()
    return dict(response)


@pytest.mark.usefixtures("_xmlupload")
def test_xmlupload(
    auth_header: dict[str, str], project_iri: str, creds: ServerCredentials, e2e_testonto_iri: str
) -> None:
    img_resources = _get_resources(f"{e2e_testonto_iri}#ImageResource", auth_header, project_iri, creds)
    img_graph = Graph()
    img_graph.parse(data=img_resources, format="json-ld")
    _analyze_img_labels(img_graph)
    _analyse_legal_info_of_img_resources(img_graph)
    pdf_resources = _get_resources(f"{e2e_testonto_iri}#PDFResource", auth_header, project_iri, creds)
    _analyze_pdf_resources(pdf_resources)


@pytest.mark.usefixtures("_xmlupload")
def test_all_copyright_holders(auth_header: dict[str, str], creds: ServerCredentials) -> None:
    response = _get_copyright_holders(auth_header, creds)
    assert set(response["data"]) == {
        "DaSCH",
        "Wellcome Collection",
        "Public Domain - Not Protected by Copyright",
        "AI-Generated Content - Not Protected by Copyright",
    }


def _get_copyright_holders(auth_header: dict[str, str], creds: ServerCredentials) -> dict[str, Any]:
    url = f"{creds.server}/admin/projects/shortcode/4125/legal-info/copyright-holders?page=1&page-size=25&order=Asc"
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


def _get_resources(resclass_iri: str, auth_header: dict[str, str], project_iri: str, creds: ServerCredentials) -> str:
    resclass_iri_encoded = urllib.parse.quote_plus(resclass_iri)
    get_resources_route = f"{creds.server}/v2/resources?resourceClass={resclass_iri_encoded}&page=0"
    headers = auth_header | {"X-Knora-Accept-Project": project_iri}
    response = requests.get(get_resources_route, timeout=3, headers=headers).json()
    resources = json.dumps(response)
    return resources


def _analyze_img_labels(img_graph: Graph) -> None:
    labels = {str(x) for x in img_graph.objects(predicate=RDFS.label)}
    assert labels == {
        "Resource 1",
        "Resource 2",
        "ImageResource_uses_doap_should_be_preview",
        "ImageResource_overrides_doap_is_open",
    }


def _analyse_legal_info_of_img_resources(img_graph: Graph) -> None:
    open_permissions = Literal(
        "CR knora-admin:ProjectAdmin|D knora-admin:ProjectMember|V knora-admin:KnownUser,knora-admin:UnknownUser"
    )
    res_1_iri = next(img_graph.subjects(RDFS.label, Literal("Resource 1")))
    assert next(img_graph.objects(res_1_iri, KNORA_API.hasPermissions)) == open_permissions
    file_1_iri = next(img_graph.objects(res_1_iri, KNORA_API.hasStillImageFileValue))
    assert next(img_graph.objects(file_1_iri, RDF.type)) == KNORA_API.StillImageFileValue
    assert next(img_graph.objects(file_1_iri, KNORA_API.hasAuthorship)) == Literal("Johannes Nussbaum")
    assert next(img_graph.objects(file_1_iri, KNORA_API.hasCopyrightHolder)) == Literal("DaSCH")
    assert next(img_graph.objects(file_1_iri, KNORA_API.hasLicense)) == URIRef("http://rdfh.ch/licenses/cc-by-4.0")
    res_2_iri = next(img_graph.subjects(RDFS.label, Literal("Resource 2")))
    file_2_iri = next(img_graph.objects(res_2_iri, KNORA_API.hasStillImageFileValue))
    assert next(img_graph.objects(file_2_iri, RDF.type)) == KNORA_API.StillImageExternalFileValue
    assert next(img_graph.objects(file_2_iri, KNORA_API.hasPermissions)) == open_permissions
    assert next(img_graph.objects(file_2_iri, KNORA_API.hasAuthorship)) == Literal("Cavanagh, Annie")
    assert next(img_graph.objects(file_2_iri, KNORA_API.hasCopyrightHolder)) == Literal("Wellcome Collection")
    assert next(img_graph.objects(file_2_iri, KNORA_API.hasLicense)) == URIRef("http://rdfh.ch/licenses/cc-by-nc-4.0")
    val_with_comment = next(img_graph.subjects(KNORA_API.valueAsString, Literal("first text value")))
    assert next(img_graph.objects(val_with_comment, KNORA_API.valueHasComment)) == Literal("Comment")
    val_with_perm = next(img_graph.subjects(KNORA_API.valueAsString, Literal("second text value")))
    assert next(img_graph.objects(val_with_perm, KNORA_API.hasPermissions)) == open_permissions


def _analyze_pdf_resources(pdf_resources: str) -> None:
    g = Graph()
    g.parse(data=pdf_resources, format="json-ld")
    res_iri = next(g.subjects(RDFS.label, Literal("Resource 3")))
    file_iri = next(g.objects(res_iri, KNORA_API.hasDocumentFileValue))
    open_permissions = Literal(
        "CR knora-admin:ProjectAdmin|D knora-admin:ProjectMember|V knora-admin:KnownUser,knora-admin:UnknownUser"
    )
    assert next(g.objects(file_iri, RDF.type)) == KNORA_API.DocumentFileValue
    assert next(g.objects(file_iri, KNORA_API.hasAuthorship)) == Literal("Nora Ammann")
    assert next(g.objects(file_iri, KNORA_API.hasCopyrightHolder)) == Literal("DaSCH")
    assert next(g.objects(file_iri, KNORA_API.hasLicense)) == URIRef("http://rdfh.ch/licenses/cc-by-4.0")
    assert next(g.objects(file_iri, KNORA_API.hasPermissions)) == open_permissions
