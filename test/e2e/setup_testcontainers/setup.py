from __future__ import annotations

import subprocess
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from uuid import uuid4

import requests
from testcontainers.core.network import Network

from test.e2e.setup_testcontainers.artifacts import ArtifactDirs
from test.e2e.setup_testcontainers.artifacts import get_artifact_dirs
from test.e2e.setup_testcontainers.artifacts import remove_artifact_dirs
from test.e2e.setup_testcontainers.containers import ContainerMetadata
from test.e2e.setup_testcontainers.containers import ContainerNames
from test.e2e.setup_testcontainers.containers import Containers
from test.e2e.setup_testcontainers.containers import ImageVersions
from test.e2e.setup_testcontainers.containers import get_all_containers
from test.e2e.setup_testcontainers.ports import get_ports
from test.e2e.setup_testcontainers.ports import release_ports


@contextmanager
def get_containers() -> Iterator[ContainerMetadata]:
    if subprocess.run("docker stats --no-stream".split(), check=False).returncode != 0:
        raise RuntimeError("Docker is not running properly")
    with Network() as network:
        metadata = _get_container_metadata()
        containers = get_all_containers(network, metadata)
        try:
            yield metadata
        finally:
            _stop_all_containers(containers)
            release_ports(metadata.ports)
            remove_artifact_dirs(metadata.artifact_dirs)


def _get_container_metadata() -> ContainerMetadata:
    _uuid = str(uuid4())[:6]
    versions = _get_image_versions()
    artifact_dirs = get_artifact_dirs(_uuid)
    _download_sipi_config(versions.sipi, artifact_dirs)
    return ContainerMetadata(
        artifact_dirs=artifact_dirs,
        versions=versions,
        ports=get_ports(),
        names=_get_container_names(_uuid),
    )


def _get_image_versions() -> ImageVersions:
    versions_env_pth = Path("src/dsp_tools/resources/start-stack/versions.env")
    versions: dict[str, str] = {}
    for line in versions_env_pth.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        key, sep, value = stripped.partition("=")
        if sep:
            versions[key.strip()] = value.strip()
    return ImageVersions(
        fuseki=versions["DB"],
        sipi=versions["API"],
        ingest=versions["API"],
        api=versions["API"],
    )


def _download_sipi_config(api_version: str, artifact_dirs: ArtifactDirs) -> None:
    url = f"https://raw.githubusercontent.com/dasch-swiss/dsp-api/{api_version}/modules/sipi/config/sipi.docker-test-config.lua"
    response = requests.get(url, timeout=30)
    if not response.ok:
        raise RuntimeError(f"Failed to download sipi.docker-config.lua from {url}: {response.status_code}")
    (artifact_dirs.sipi_config / "sipi.docker-config.lua").write_text(response.text, encoding="utf-8")


def _get_container_names(_uuid: str) -> ContainerNames:
    prefix = f"testcontainer-{_uuid}"
    return ContainerNames(f"{prefix}-DB", f"{prefix}-SIPI", f"{prefix}-INGEST", f"{prefix}-API")


def _stop_all_containers(containers: Containers) -> None:
    containers.fuseki.stop()
    containers.sipi.stop()
    containers.ingest.stop()
    containers.api.stop()
    print("All containers have been stopped")
