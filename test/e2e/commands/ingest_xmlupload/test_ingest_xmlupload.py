import json
from collections.abc import Iterator
from pathlib import Path

import pandas as pd
import pytest
from pytest_unordered import unordered

from dsp_tools.cli.args import ServerCredentials
from dsp_tools.commands.ingest_xmlupload.create_resources.upload_xml import ingest_xmlupload
from dsp_tools.commands.ingest_xmlupload.ingest_files.ingest_files import ingest_files
from dsp_tools.commands.ingest_xmlupload.upload_files.upload_files import upload_files
from dsp_tools.commands.project.create.project_create_all import create_project
from test.e2e.setup_testcontainers.artifacts import ArtifactDirs
from test.e2e.setup_testcontainers.containers import ContainerMetadata
from test.e2e.setup_testcontainers.setup import get_containers

CWD = Path("testdata/dsp-ingest-data/e2e-sample-project")
XML_FILE = Path("data.xml")
MULTIMEDIA_FILE_1 = Path("Bilder Projekt 2024/Côté gauche/Bild A (1).jpg")
MULTIMEDIA_FILE_2 = Path("Bilder Projekt 2024/Côté gauche/Dokument B (2).pdf")
SHORTCODE = "4126"


@pytest.fixture(scope="module")
def container_metadata() -> Iterator[ContainerMetadata]:
    with get_containers() as metadata:
        yield metadata


@pytest.fixture(scope="module")
def tmp_folder(container_metadata: ContainerMetadata) -> Path:
    return container_metadata.artifact_dirs.tmp_ingest / "import" / SHORTCODE


@pytest.fixture(scope="module")
def creds(container_metadata: ContainerMetadata) -> ServerCredentials:
    return ServerCredentials(
        "root@example.com",
        "test",
        f"http://0.0.0.0:{container_metadata.ports.api}",
        f"http://0.0.0.0:{container_metadata.ports.ingest}",
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
def test_ingest_upload(
    mapping_file: Path, creds: ServerCredentials, container_metadata: ContainerMetadata, tmp_folder: Path
) -> None:
    _test_upload_step(creds, tmp_folder)
    _test_ingest_step(mapping_file, creds, tmp_folder, container_metadata.artifact_dirs)
    _test_xmlupload_step(creds)


def _test_upload_step(creds: ServerCredentials, tmp_folder: Path) -> None:
    success = upload_files(XML_FILE, creds, Path(".").absolute())
    assert success
    assert {x.relative_to(tmp_folder) for x in tmp_folder.glob("**/*.*")} == {MULTIMEDIA_FILE_1, MULTIMEDIA_FILE_2}


def _test_ingest_step(
    mapping_file: Path, creds: ServerCredentials, tmp_folder: Path, artifact_dirs: ArtifactDirs
) -> None:
    success = ingest_files(creds, SHORTCODE)
    assert success
    assert not {x.relative_to(tmp_folder) for x in tmp_folder.glob("**/*.*")}
    ingested_files = list((artifact_dirs.sipi_images / SHORTCODE).glob("**/*.*"))
    ingested_files_ext = [f.suffixes for f in ingested_files]
    expected_ext = [[".info"], [".jpg", ".orig"], [".jpx"], [".info"], [".pdf", ".orig"], [".pdf"]]
    assert unordered(ingested_files_ext) == expected_ext

    df = pd.read_csv(mapping_file)
    assert df["original"].tolist() == unordered([str(MULTIMEDIA_FILE_1), str(MULTIMEDIA_FILE_2)])


def _test_xmlupload_step(creds: ServerCredentials) -> None:
    success = ingest_xmlupload(XML_FILE, creds)
    assert success
    id2iri_file = list(Path.cwd().glob(f"id2iri_{SHORTCODE}_localhost*.json"))[-1]  # choose the most recent one
    id2iri_mapping = json.loads(id2iri_file.read_text(encoding="utf-8"))
    assert sorted(id2iri_mapping.keys()) == ["resource_1", "resource_2", "resource_3"]
    assert all(x.startswith(f"http://rdfh.ch/{SHORTCODE}/") for x in id2iri_mapping.values())
