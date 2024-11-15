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
from test.e2e.setup_testcontainers import get_containers

CREDS = ServerCredentials("root@example.com", "test", "http://0.0.0.0:3333")
CWD = Path("testdata/dsp-ingest-data/e2e-sample-project")
XML_FILE = Path("data.xml")
MULTIMEDIA_FILE_1 = Path("Bilder Projekt 2024/Côté gauche/Bild A (1).jpg")
MULTIMEDIA_FILE_2 = Path("Bilder Projekt 2024/Côté gauche/Dokument B (2).pdf")
SHORTCODE = "4125"
TMP_FOLDER = TMP_INGEST / "import" / SHORTCODE


@pytest.fixture
def mapping_file(monkeypatch: pytest.MonkeyPatch) -> Iterator[Path]:
    with monkeypatch.context() as m:
        m.chdir(CWD)
        mapping_file = Path(f"mapping-{SHORTCODE}.csv")
        yield mapping_file
        mapping_file.unlink(missing_ok=True)
        for id2iri_mapping in Path(".").glob("*id2iri_mapping*.json"):
            id2iri_mapping.unlink(missing_ok=True)


@pytest.fixture
def _create_project() -> Iterator[None]:
    with get_containers():
        success = create_project(Path("testdata/dsp-ingest-data/e2e-sample-project/project.json"), CREDS, verbose=True)
        assert success
        yield


@pytest.mark.usefixtures("_create_project")
def test_ingest_upload(mapping_file: Path) -> None:
    _test_upload_step()
    _test_ingest_step(mapping_file)
    _test_xmlupload_step()


def _test_upload_step() -> None:
    success = upload_files(XML_FILE, CREDS, Path(".").absolute())
    assert success
    assert {x.relative_to(TMP_FOLDER) for x in TMP_FOLDER.glob("**/*.*")} == {MULTIMEDIA_FILE_1, MULTIMEDIA_FILE_2}


def _test_ingest_step(mapping_file: Path) -> None:
    success = ingest_files(CREDS, SHORTCODE)
    assert success
    assert not {x.relative_to(TMP_FOLDER) for x in TMP_FOLDER.glob("**/*.*")}
    ingested_files = list((SIPI_IMAGES / SHORTCODE).glob("**/*.*"))
    ingested_files_ext = [f.suffixes for f in ingested_files]
    expected_ext = [[".info"], [".jpg", ".orig"], [".jpx"], [".info"], [".pdf", ".orig"], [".pdf"]]
    assert unordered(ingested_files_ext) == expected_ext

    df = pd.read_csv(mapping_file)
    assert df["original"].tolist() == unordered([str(MULTIMEDIA_FILE_1), str(MULTIMEDIA_FILE_2)])


def _test_xmlupload_step() -> None:
    success = ingest_xmlupload(XML_FILE, CREDS)
    assert success
    id2iri_file = list(Path.cwd().glob("*_id2iri_mapping_localhost.json"))[-1]  # choose the most recent one
    id2iri_mapping = json.loads(id2iri_file.read_text(encoding="utf-8"))
    assert sorted(id2iri_mapping.keys()) == ["resource_1", "resource_2", "resource_3"]
    assert all(x.startswith(f"http://rdfh.ch/{SHORTCODE}/") for x in id2iri_mapping.values())
