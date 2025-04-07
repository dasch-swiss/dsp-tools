import contextlib
import shutil
from dataclasses import dataclass
from pathlib import Path

E2E_TESTDATA = Path("testdata/e2e").absolute()


@dataclass(frozen=True)
class ArtifactDirs:
    sipi_images: Path
    tmp_sipi: Path
    tmp_ingest: Path
    ingest_db: Path


def get_artifact_dirs(_uuid: str) -> ArtifactDirs:
    dirs = {
        "sipi_images": E2E_TESTDATA / "images" / _uuid,
        "tmp_sipi": E2E_TESTDATA / "tmp-dsp-sipi" / _uuid,
        "tmp_ingest": E2E_TESTDATA / "tmp-dsp-ingest" / _uuid,
        "ingest_db": E2E_TESTDATA / "ingest-db" / _uuid,
    }
    for _dir in dirs.values():
        _dir.mkdir(parents=True)
    return ArtifactDirs(**dirs)


def remove_artifact_dirs(artifact_dirs: ArtifactDirs) -> None:
    for _dir in [artifact_dirs.sipi_images, artifact_dirs.tmp_sipi, artifact_dirs.tmp_ingest, artifact_dirs.ingest_db]:
        with contextlib.suppress(PermissionError):
            shutil.rmtree(_dir)
