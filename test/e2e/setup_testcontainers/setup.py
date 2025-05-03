from __future__ import annotations

import subprocess
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from uuid import uuid4

import regex
from testcontainers.core.network import Network

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
    return ContainerMetadata(
        artifact_dirs=get_artifact_dirs(_uuid),
        versions=_get_image_versions(),
        ports=get_ports(),
        names=_get_container_names(_uuid),
    )


def _get_image_versions() -> ImageVersions:
    def _get_version(docker_compose_content: str, component: str) -> str:
        match = regex.search(rf"image: daschswiss/{component}:([^\n]+)", docker_compose_content)
        return match.group(1) if match else "latest"

    docker_compose_content = Path("src/dsp_tools/resources/start-stack/docker-compose.yml").read_text(encoding="utf-8")
    fuseki = _get_version(docker_compose_content, "apache-jena-fuseki")
    sipi = _get_version(docker_compose_content, "knora-sipi")
    ingest = _get_version(docker_compose_content, "dsp-ingest")
    api = _get_version(docker_compose_content, "knora-api")
    return ImageVersions(fuseki=fuseki, sipi=sipi, ingest=ingest, api=api)


def _get_container_names(_uuid: str) -> ContainerNames:
    prefix = f"testcontainer-{_uuid}"
    return ContainerNames(f"{prefix}-DB", f"{prefix}-SIPI", f"{prefix}-INGEST", f"{prefix}-API")


def _stop_all_containers(containers: Containers) -> None:
    containers.fuseki.stop()
    containers.sipi.stop()
    containers.ingest.stop()
    containers.api.stop()
    print("All containers have been stopped")
