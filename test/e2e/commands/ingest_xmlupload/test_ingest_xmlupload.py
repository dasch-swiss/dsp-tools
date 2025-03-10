import json
from pathlib import Path
from typing import Iterator

import pandas as pd
import pytest
from pytest_unordered import unordered

from dsp_tools.cli.args import ServerCredentials
from dsp_tools.commands.ingest_xmlupload.create_resources.upload_xml import ingest_xmlupload
from dsp_tools.commands.ingest_xmlupload.ingest_files.ingest_files import ingest_files
from dsp_tools.commands.ingest_xmlupload.upload_files.upload_files import upload_files
from dsp_tools.commands.project.create.project_create import create_project
from test.e2e.setup_testcontainers import SIPI_IMAGES
from test.e2e.setup_testcontainers import TMP_INGEST
from test.e2e.setup_testcontainers import ContainerPorts
from test.e2e.setup_testcontainers import TestContainerFactory

CWD = Path("testdata/dsp-ingest-data/e2e-sample-project")
XML_FILE = Path("data.xml")
MULTIMEDIA_FILE_1 = Path("Bilder Projekt 2024/Côté gauche/Bild A (1).jpg")
MULTIMEDIA_FILE_2 = Path("Bilder Projekt 2024/Côté gauche/Dokument B (2).pdf")
SHORTCODE = "4125"
TMP_FOLDER = TMP_INGEST / "import" / SHORTCODE


@pytest.fixture(scope="module")
def container_ports() -> Iterator[ContainerPorts]:
    with TestContainerFactory.get_containers() as containers:
        yield containers


@pytest.fixture(scope="module")
def creds(container_ports: ContainerPorts) -> ServerCredentials:
    return ServerCredentials(
        "root@example.com",
        "test",
        f"http://0.0.0.0:{container_ports.api_port}",
        f"http://0.0.0.0:{container_ports.ingest_port}",
    )


@pytest.fixture
def mapping_file(monkeypatch: pytest.MonkeyPatch) -> Iterator[Path]:
    with monkeypatch.context() as m:
        m.chdir(CWD)
        mapping_file = Path(f"mapping-{SHORTCODE}.csv")
        yield mapping_file
        mapping_file.unlink(missing_ok=True)
        for id2iri_mapping in Path(".").glob("id2iri_*.json"):
            id2iri_mapping.unlink(missing_ok=True)


@pytest.fixture(scope="module")
def _create_project(creds: ServerCredentials) -> None:
    assert create_project(Path("testdata/dsp-ingest-data/e2e-sample-project/project.json"), creds, verbose=True)


@pytest.mark.usefixtures("_create_project")
def test_ingest_upload(mapping_file: Path, creds: ServerCredentials) -> None:
    _test_upload_step(creds)
    _test_ingest_step(mapping_file, creds)
    _test_xmlupload_step(creds)


def _test_upload_step(creds: ServerCredentials) -> None:
    success = upload_files(XML_FILE, creds, Path(".").absolute())
    assert success
    assert {x.relative_to(TMP_FOLDER) for x in TMP_FOLDER.glob("**/*.*")} == {MULTIMEDIA_FILE_1, MULTIMEDIA_FILE_2}


def _test_ingest_step(mapping_file: Path, creds: ServerCredentials) -> None:
    success = ingest_files(creds, SHORTCODE)
    assert success
    assert not {x.relative_to(TMP_FOLDER) for x in TMP_FOLDER.glob("**/*.*")}
    ingested_files = list((SIPI_IMAGES / SHORTCODE).glob("**/*.*"))
    ingested_files_ext = [f.suffixes for f in ingested_files]
    expected_ext = [[".info"], [".jpg", ".orig"], [".jpx"], [".info"], [".pdf", ".orig"], [".pdf"]]
    assert unordered(ingested_files_ext) == expected_ext

    df = pd.read_csv(mapping_file)
    assert df["original"].tolist() == unordered([str(MULTIMEDIA_FILE_1), str(MULTIMEDIA_FILE_2)])


def _test_xmlupload_step(creds: ServerCredentials) -> None:
    success = ingest_xmlupload(XML_FILE, creds)
    assert success
    id2iri_file = list(Path.cwd().glob("id2iri_4125_localhost*.json"))[-1]  # choose the most recent one
    id2iri_mapping = json.loads(id2iri_file.read_text(encoding="utf-8"))
    assert sorted(id2iri_mapping.keys()) == ["resource_1", "resource_2", "resource_3"]
    assert all(x.startswith(f"http://rdfh.ch/{SHORTCODE}/") for x in id2iri_mapping.values())
