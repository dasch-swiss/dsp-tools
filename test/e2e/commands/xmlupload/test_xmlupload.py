# mypy: disable-error-code="no-untyped-def"

import json
import urllib.parse
from pathlib import Path

import pytest
import requests
from rdflib import Graph

from dsp_tools.commands.xmlupload.xmlupload import xmlupload
from dsp_tools.utils.rdflib_constants import KNORA_API_STR

# ruff: noqa: ARG001 Unused function argument

PROJECT_SHORTCODE = "9999"
ONTO_NAME = "onto"
SECOND_ONTO = "second-onto"


@pytest.fixture(scope="module")
def project_iri(create_generic_project: None, creds) -> str:
    get_project_route = f"{creds.server}/admin/projects/shortcode/{PROJECT_SHORTCODE}"
    project_iri: str = requests.get(get_project_route, timeout=3).json()["project"]["id"]
    return project_iri


@pytest.fixture(scope="module")
def onto_iri(creds) -> str:
    return f"{creds.server}/ontology/{PROJECT_SHORTCODE}/{ONTO_NAME}/v2#"


@pytest.fixture(scope="module")
def class_with_everything_iri(onto_iri) -> str:
    return f"{onto_iri}ClassWithEverything"


@pytest.fixture(scope="module")
def second_onto_iri(creds) -> str:
    return f"{creds.server}/ontology/{PROJECT_SHORTCODE}/{SECOND_ONTO}/v2#"


@pytest.fixture(scope="module")
def _xmlupload(create_generic_project: None, creds) -> None:
    assert xmlupload(Path("testdata/validate-data/generic/minimal_correct.xml"), creds, ".")


@pytest.fixture(scope="module")
def auth_header(create_generic_project: None, creds) -> dict[str, str]:
    payload = {"email": creds.user, "password": creds.password}
    token: str = requests.post(f"{creds.server}/v2/authentication", json=payload, timeout=3).json()["token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(scope="module")
def class_with_everything_resource_graph(
    _xmlupload, class_with_everything_iri, auth_header, project_iri, creds
) -> Graph:
    return _util_request_resources_by_class(class_with_everything_iri, auth_header, project_iri, creds)


def _util_request_resources_by_class(resclass_iri: str, auth_header: dict[str, str], project_iri: str, creds) -> Graph:
    resclass_iri_encoded = urllib.parse.quote_plus(resclass_iri)
    get_resources_route = f"{creds.server}/v2/resources?resourceClass={resclass_iri_encoded}&page=0"
    headers = auth_header | {"X-Knora-Accept-Project": project_iri}
    response = requests.get(get_resources_route, timeout=3, headers=headers).json()
    resources = json.dumps(response)
    g = Graph()
    g.parse(data=resources, format="json-ld")
    return g


class TestResources:
    def test_class_with_everything_all_created(self, class_with_everything_resource_graph):
        assert len(class_with_everything_resource_graph) != 0

    @pytest.mark.usefixtures("_xmlupload")
    def test_second_onto_class(self, second_onto_iri, auth_header, project_iri, creds):
        cls_iri_str = f"{second_onto_iri}SecondOntoClass"
        resources = _util_request_resources_by_class(cls_iri_str, auth_header, project_iri, creds)
        assert len(resources) != 0

    @pytest.mark.usefixtures("_xmlupload")
    def test_region(self, auth_header, project_iri, creds):
        cls_iri_str = f"{KNORA_API_STR}Region"
        resources = _util_request_resources_by_class(cls_iri_str, auth_header, project_iri, creds)
        assert len(resources) != 0

    @pytest.mark.usefixtures("_xmlupload")
    def test_link_obj(self, auth_header, project_iri, creds):
        cls_iri_str = f"{KNORA_API_STR}LinkObj"
        resources = _util_request_resources_by_class(cls_iri_str, auth_header, project_iri, creds)
        assert len(resources) != 0

    @pytest.mark.usefixtures("_xmlupload")
    def test_audio_segment(self, auth_header, project_iri, creds):
        cls_iri_str = f"{KNORA_API_STR}AudioSegment"
        resources = _util_request_resources_by_class(cls_iri_str, auth_header, project_iri, creds)
        assert len(resources) != 0

    @pytest.mark.usefixtures("_xmlupload")
    def test_video_segment(self, auth_header, project_iri, creds):
        cls_iri_str = f"{KNORA_API_STR}VideoSegment"
        resources = _util_request_resources_by_class(cls_iri_str, auth_header, project_iri, creds)
        assert len(resources) != 0
