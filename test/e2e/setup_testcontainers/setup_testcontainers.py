import contextlib
import shutil
import socket
import subprocess
from contextlib import contextmanager
from dataclasses import dataclass
from itertools import count
from pathlib import Path
from typing import Iterator
from uuid import uuid4

import regex
from testcontainers.core.container import DockerContainer
from testcontainers.core.network import Network

from test.e2e.setup_testcontainers.containers import get_all_containers

E2E_TESTDATA = Path("testdata/e2e").absolute()

TESTCONTAINER_PORTS_LOCKFILES = E2E_TESTDATA / "testcontainer_port_lockfiles"
TESTCONTAINER_PORTS_LOCKFILES.mkdir(parents=True, exist_ok=True)
API_INTERNAL_PORT = 3333
INGEST_INTERNAL_PORT = 3340
SIPI_INTERNAL_PORT = 1024
FUSEKI_INTERNAL_PORT = 3030


@dataclass(frozen=True)
class ImageVersions:
    fuseki: str
    sipi: str
    ingest: str
    api: str


@dataclass(frozen=True)
class Containers:
    fuseki: DockerContainer
    sipi: DockerContainer
    ingest: DockerContainer
    api: DockerContainer


@dataclass(frozen=True)
class ContainerNames:
    fuseki: str
    sipi: str
    ingest: str
    api: str


@dataclass(frozen=True)
class ContainerPorts:
    """External ports of the containers"""

    fuseki: int
    sipi: int
    ingest: int
    api: int


def _get_image_versions() -> ImageVersions:
    def _get_image_version(docker_compose_content: str, component: str) -> str:
        match = regex.search(rf"image: daschswiss/{component}:([^\n]+)", docker_compose_content)
        return match.group(1) if match else "latest"

    docker_compose_content = Path("src/dsp_tools/resources/start-stack/docker-compose.yml").read_text(encoding="utf-8")
    fuseki = _get_image_version(docker_compose_content, "apache-jena-fuseki")
    sipi = _get_image_version(docker_compose_content, "knora-sipi")
    ingest = _get_image_version(docker_compose_content, "dsp-ingest")
    api = _get_image_version(docker_compose_content, "knora-api")
    return ImageVersions(fuseki=fuseki, sipi=sipi, ingest=ingest, api=api)


@dataclass(frozen=True)
class ArtifactDirs:
    sipi_images: Path
    tmp_sipi: Path
    tmp_ingest: Path
    ingest_db: Path


def _get_artifact_dirs(_uuid: str) -> ArtifactDirs:
    dirs = {
        "sipi_images": E2E_TESTDATA / "images" / _uuid,
        "tmp_sipi": E2E_TESTDATA / "tmp-dsp-sipi" / _uuid,
        "tmp_ingest": E2E_TESTDATA / "tmp-dsp-ingest" / _uuid,
        "ingest_db": E2E_TESTDATA / "ingest-db" / _uuid,
    }
    for _dir in dirs.values():
        _dir.mkdir(parents=True)
    return ArtifactDirs(**dirs)


def _remove_artifact_dirs(artifact_dirs: ArtifactDirs) -> None:
    for _dir in [artifact_dirs.sipi_images, artifact_dirs.tmp_sipi, artifact_dirs.tmp_ingest, artifact_dirs.ingest_db]:
        with contextlib.suppress(PermissionError):
            shutil.rmtree(_dir)


@dataclass(frozen=True)
class ContainerMetadata:
    artifact_dirs: ArtifactDirs
    versions: ImageVersions
    ports: ContainerPorts
    names: ContainerNames


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
            _release_ports(metadata.ports)
            _remove_artifact_dirs(metadata.artifact_dirs)


def _get_container_metadata() -> ContainerMetadata:
    _uuid = str(uuid4())[:6]
    return ContainerMetadata(
        artifact_dirs=_get_artifact_dirs(_uuid),
        versions=_get_image_versions(),
        ports=_get_ports(),
        names=_get_container_names(_uuid),
    )


def _get_container_names(_uuid: str) -> ContainerNames:
    prefix = f"testcontainer-{_uuid}"
    return ContainerNames(f"{prefix}-DB", f"{prefix}-SIPI", f"{prefix}-INGEST", f"{prefix}-API")


def _get_ports() -> ContainerPorts:
    def _reserve_port(port: int) -> bool:
        with socket.socket() as s:
            if s.connect_ex(("localhost", port)) == 0:
                return False
        try:
            (TESTCONTAINER_PORTS_LOCKFILES / str(port)).touch(exist_ok=False)
        except FileExistsError:
            return False
        return True

    num_of_ports_needed = 4
    port_window: list[int] = []
    for port in count(1025):
        if len(port_window) == num_of_ports_needed:
            break
        if _reserve_port(port):
            port_window.append(port)

    return ContainerPorts(*port_window)


def _release_ports(ports: ContainerPorts) -> None:
    (TESTCONTAINER_PORTS_LOCKFILES / str(ports.fuseki)).unlink()
    (TESTCONTAINER_PORTS_LOCKFILES / str(ports.sipi)).unlink()
    (TESTCONTAINER_PORTS_LOCKFILES / str(ports.ingest)).unlink()
    (TESTCONTAINER_PORTS_LOCKFILES / str(ports.api)).unlink()


def _stop_all_containers(containers: Containers) -> None:
    containers.fuseki.stop()
    containers.sipi.stop()
    containers.ingest.stop()
    containers.api.stop()
    print("All containers have been stopped")
