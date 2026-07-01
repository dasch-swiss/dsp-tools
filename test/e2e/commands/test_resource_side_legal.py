import json
import shutil
from collections.abc import Iterator
from pathlib import Path

import pytest
import requests
from rdflib import Literal

from dsp_tools.cli.args import ServerCredentials
from dsp_tools.commands.create.create import create
from dsp_tools.commands.get.get import get_project
from dsp_tools.commands.xmlupload.upload_config import UploadConfig
from dsp_tools.commands.xmlupload.xmlupload import xmlupload
from dsp_tools.utils.rdf_constants import KNORA_API
from test.e2e.commands.xmlupload.utils import util_get_res_iri_from_label
from test.e2e.commands.xmlupload.utils import util_request_resources_by_class

PROJECT_SHORTCODE = "0099"
ONTO_NAME = "legalonto"
DATA_LICENSE = "http://rdfh.ch/licenses/cc-by-4.0"
DATA_COPYRIGHT_HOLDER = "DaSCH"
DATA_AUTHORSHIP = ["Default Author One", "Default Author Two"]


@pytest.fixture(scope="module")
def project_file() -> Path:
    return Path("testdata/json-project/resource-side-legal-0099.json")


@pytest.fixture(scope="module")
def xml_file() -> Path:
    return Path("testdata/xml-data/resource-side-legal-0099.xml")


@pytest.fixture(scope="module")
def tmp_dir() -> Iterator[Path]:
    out = Path("testdata/tmp")
    out.mkdir(exist_ok=True)
    yield out
    shutil.rmtree(out)


@pytest.fixture(scope="module")
def auth_header(creds: ServerCredentials) -> dict[str, str]:
    payload = {"email": creds.user, "password": creds.password}
    token: str = requests.post(f"{creds.server}/v2/authentication", json=payload, timeout=3).json()["token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(scope="module")
def project_iri(creds: ServerCredentials) -> str:
    route = f"{creds.server}/admin/projects/shortcode/{PROJECT_SHORTCODE}"
    project_iri: str = requests.get(route, timeout=3).json()["project"]["id"]
    return project_iri


@pytest.fixture(scope="module")
def class_iri(creds: ServerCredentials) -> str:
    return f"{creds.server}/ontology/{PROJECT_SHORTCODE}/{ONTO_NAME}/v2#LegalResource"


@pytest.mark.order(1)
def test_create_project(creds: ServerCredentials, project_file: Path) -> None:
    assert create(project_file=project_file.absolute(), creds=creds, exit_if_exists=False)


@pytest.mark.order(2)
def test_project_legal_fields_round_trip(creds: ServerCredentials, tmp_dir: Path) -> None:
    """The three project-level legal fields written by `create` are read back by `get`."""
    out_file = tmp_dir / "_resource-side-legal.json"
    assert get_project(
        project_identifier=PROJECT_SHORTCODE,
        outfile_path=str(out_file),
        creds=creds,
        verbose=True,
    )
    returned = json.loads(out_file.read_text(encoding="utf-8"))["project"]
    assert returned["data_license"] == DATA_LICENSE
    assert returned["data_copyright_holder"] == DATA_COPYRIGHT_HOLDER
    assert returned["data_authorship"] == DATA_AUTHORSHIP


@pytest.mark.order(3)
def test_xmlupload(creds: ServerCredentials, xml_file: Path) -> None:
    assert xmlupload(input_file=xml_file, creds=creds, imgdir=".", config=UploadConfig())


@pytest.mark.order(4)
def test_resource_authorship(
    auth_header: dict[str, str], project_iri: str, class_iri: str, creds: ServerCredentials
) -> None:
    """The per-resource `<data-authorship>` is uploaded as `knora-api:hasResourceAuthorship` literals."""
    g = util_request_resources_by_class(class_iri, auth_header, project_iri, creds)

    with_authorship = util_get_res_iri_from_label(g, "resource_with_authorship")
    authors = {str(a) for a in g.objects(with_authorship, KNORA_API.hasResourceAuthorship)}
    assert authors == {"Resource Author One", "Resource Author Two"}
    assert isinstance(next(g.objects(with_authorship, KNORA_API.hasResourceAuthorship)), Literal)

    without_authorship = util_get_res_iri_from_label(g, "resource_without_authorship")
    assert len(list(g.objects(without_authorship, KNORA_API.hasResourceAuthorship))) == 0
