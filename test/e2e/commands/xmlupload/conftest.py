# mypy: disable-error-code="no-untyped-def"

from pathlib import Path

import pytest
import requests

from dsp_tools.cli.args import ServerCredentials
from dsp_tools.commands.xmlupload.xmlupload import xmlupload

# ruff: noqa: ARG001 Unused function argument

PROJECT_SHORTCODE = "9999"
ONTO_NAME = "onto"
SECOND_ONTO = "second-onto"


@pytest.fixture(scope="module")
def project_iri(create_generic_project, creds: ServerCredentials) -> str:
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
def _xmlupload(create_generic_project, creds) -> None:
    assert xmlupload(Path("testdata/validate-data/generic/minimal_correct.xml"), creds, ".")


@pytest.fixture(scope="module")
def auth_header(create_generic_project, creds) -> dict[str, str]:
    payload = {"email": creds.user, "password": creds.password}
    token: str = requests.post(f"{creds.server}/v2/authentication", json=payload, timeout=3).json()["token"]
    return {"Authorization": f"Bearer {token}"}
