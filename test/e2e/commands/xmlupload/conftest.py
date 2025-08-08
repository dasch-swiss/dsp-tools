# mypy: disable-error-code="no-untyped-def"

from pathlib import Path
from tempfile import TemporaryDirectory

import pytest
import requests

from dsp_tools.cli.args import ServerCredentials
from dsp_tools.commands.xmlupload.xmlupload import xmlupload

# ruff: noqa: ARG001 Unused function argument

PROJECT_SHORTCODE_9999 = "9999"
ONTO_NAME_9999 = "onto"
SECOND_ONTO_9999 = "second-onto"


@pytest.fixture(scope="module")
def project_iri_9999(create_generic_project, creds: ServerCredentials) -> str:
    get_project_route = f"{creds.server}/admin/projects/shortcode/{PROJECT_SHORTCODE_9999}"
    project_iri: str = requests.get(get_project_route, timeout=3).json()["project"]["id"]
    return project_iri


@pytest.fixture(scope="module")
def onto_iri_9999(creds) -> str:
    return f"{creds.server}/ontology/{PROJECT_SHORTCODE_9999}/{ONTO_NAME_9999}/v2#"


@pytest.fixture(scope="module")
def class_with_everything_iri_9999(onto_iri_9999) -> str:
    return f"{onto_iri_9999}ClassWithEverything"


@pytest.fixture(scope="module")
def second_onto_iri_9999(creds) -> str:
    return f"{creds.server}/ontology/{PROJECT_SHORTCODE_9999}/{SECOND_ONTO_9999}/v2#"


@pytest.fixture(scope="module")
def _xmlupload_minimal_correct_9999(create_generic_project, creds) -> None:
    """
    If there is more than 1 module, pytest-xdist might execute this fixture for multiple modules at the same time.
    This can lead to the situation that multiple workers start the xmlupload of the same data at the same time.
    Then it can happen that they try to save the id2iri mapping at the same time,
    which fails, because the id2iri mapping is named after the shortcode and the timestamp.
    """
    absolute_xml_path = Path("testdata/validate-data/generic/minimal_correct.xml").absolute()
    original_cwd = Path.cwd()
    with TemporaryDirectory() as tmpdir:
        with pytest.MonkeyPatch.context() as m:
            m.chdir(tmpdir)
            assert xmlupload(absolute_xml_path, creds, str(original_cwd))


@pytest.fixture(scope="module")
def _xmlupload_text_parsing_9999(create_generic_project: None, creds: ServerCredentials) -> None:
    """
    If there is more than 1 module, pytest-xdist might execute this fixture for multiple modules at the same time.
    This can lead to the situation that multiple workers start the xmlupload of the same data at the same time.
    Then it can happen that they try to save the id2iri mapping at the same time,
    which fails, because the id2iri mapping is named after the shortcode and the timestamp.
    """
    absolute_xml_path = Path("testdata/xml-data/generic_project_text_parsing.xml").absolute()
    original_cwd = Path.cwd()
    with TemporaryDirectory() as tmpdir:
        with pytest.MonkeyPatch.context() as m:
            m.chdir(tmpdir)
            assert xmlupload(absolute_xml_path, creds, str(original_cwd))


@pytest.fixture(scope="module")
def auth_header(create_generic_project, creds) -> dict[str, str]:
    payload = {"email": creds.user, "password": creds.password}
    token: str = requests.post(f"{creds.server}/v2/authentication", json=payload, timeout=3).json()["token"]
    return {"Authorization": f"Bearer {token}"}
