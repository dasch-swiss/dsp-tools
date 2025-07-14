from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import requests
from testcontainers.core.container import DockerContainer
from testcontainers.core.network import Network
from testcontainers.core.waiting_utils import wait_for_logs

from test.e2e.setup_testcontainers.artifacts import E2E_TESTDATA
from test.e2e.setup_testcontainers.artifacts import ArtifactDirs
from test.e2e.setup_testcontainers.ports import ExternalContainerPorts

FUSEKI_INTERNAL_PORT = 3030
SIPI_INTERNAL_PORT = 1024
INGEST_INTERNAL_PORT = 3340
API_INTERNAL_PORT = 3333


@dataclass(frozen=True)
class Containers:
    fuseki: DockerContainer
    sipi: DockerContainer
    ingest: DockerContainer
    api: DockerContainer


@dataclass(frozen=True)
class ContainerMetadata:
    artifact_dirs: ArtifactDirs
    versions: ImageVersions
    ports: ExternalContainerPorts
    names: ContainerNames


@dataclass(frozen=True)
class ImageVersions:
    fuseki: str
    sipi: str
    ingest: str
    api: str


@dataclass(frozen=True)
class ContainerNames:
    fuseki: str
    sipi: str
    ingest: str
    api: str


def get_all_containers(network: Network, metadata: ContainerMetadata) -> Containers:
    fuseki = _get_fuseki(network, metadata.versions.fuseki, metadata.ports, metadata.names)
    sipi = _get_sipi(network, metadata.versions.sipi, metadata.ports, metadata.names, metadata.artifact_dirs)
    ingest = _get_ingest(network, metadata.versions.ingest, metadata.ports, metadata.names, metadata.artifact_dirs)
    api = _get_api(network, metadata.versions.api, metadata.ports, metadata.names)
    containers = Containers(fuseki=fuseki, sipi=sipi, ingest=ingest, api=api)
    _print_containers_are_ready(containers)
    return containers


def _get_fuseki(
    network: Network, version: str, ports: ExternalContainerPorts, names: ContainerNames
) -> DockerContainer:
    fuseki = (
        DockerContainer(f"daschswiss/apache-jena-fuseki:{version}")
        .with_name(names.fuseki)
        .with_network(network)
        .with_bind_ports(host=ports.fuseki, container=FUSEKI_INTERNAL_PORT)
        .with_env("ADMIN_PASSWORD", "test")
    )
    fuseki.start()
    wait_for_logs(fuseki, f"Server .+ Started .+ on port {FUSEKI_INTERNAL_PORT}")
    print("Fuseki is ready")
    _create_data_set_and_admin_user(ports.fuseki)
    return fuseki


def _create_data_set_and_admin_user(fuseki_external_port: int) -> None:
    repo_config = Path("testdata/e2e/repo_config.ttl").read_text(encoding="utf-8")
    url = f"http://0.0.0.0:{fuseki_external_port}/$/datasets"
    files = {"file": ("file.ttl", repo_config, "text/turtle; charset=utf8")}
    if not requests.post(url, files=files, auth=("admin", "test"), timeout=30).ok:
        raise RuntimeError("Fuseki did not create the dataset")
    print("Dataset created")

    admin_user_data = Path("testdata/e2e/admin_user_data.ttl").read_text(encoding="utf-8")
    url = f"http://0.0.0.0:{fuseki_external_port}/knora-test/data?graph=http://www.knora.org/data/admin"
    files = {"file": ("file.ttl", admin_user_data, "text/turtle; charset: utf-8")}
    if not requests.post(url, files=files, auth=("admin", "test"), timeout=30).ok:
        raise RuntimeError("Fuseki did not create the admin user")
    print("Admin user created")


def _get_sipi(
    network: Network, version: str, ports: ExternalContainerPorts, names: ContainerNames, artifact_dirs: ArtifactDirs
) -> DockerContainer:
    sipi = (
        DockerContainer(f"daschswiss/knora-sipi:{version}")
        .with_name(names.sipi)
        .with_network(network)
        .with_bind_ports(host=ports.sipi, container=SIPI_INTERNAL_PORT)
        .with_env("KNORA_WEBAPI_KNORA_API_EXTERNAL_HOST", "0.0.0.0")  # noqa: S104
        .with_env("KNORA_WEBAPI_KNORA_API_EXTERNAL_PORT", ports.api)
        .with_command("--config=/sipi/config/sipi.docker-config.lua")
        .with_volume_mapping(artifact_dirs.tmp_sipi, "/tmp", "rw")  # noqa: S108
        .with_volume_mapping(E2E_TESTDATA, "/sipi/config", "rw")
        .with_volume_mapping(artifact_dirs.sipi_images, "/sipi/images", "rw")
    )
    sipi.start()
    wait_for_logs(sipi, f"Server listening on HTTP port {SIPI_INTERNAL_PORT}")
    print("Sipi is ready")
    return sipi


def _get_ingest(
    network: Network, version: str, ports: ExternalContainerPorts, names: ContainerNames, artifact_dirs: ArtifactDirs
) -> DockerContainer:
    ingest = (
        DockerContainer(f"daschswiss/dsp-ingest:{version}")
        .with_name(names.ingest)
        .with_network(network)
        .with_bind_ports(host=ports.ingest, container=INGEST_INTERNAL_PORT)
        .with_env("STORAGE_ASSET_DIR", "/opt/images")
        .with_env("STORAGE_TEMP_DIR", "/opt/tmp")
        # other containers are addressed with http://<service_name>:<internal_port>
        .with_env("JWT_ISSUER", f"http://{names.api}:{ports.api}")
        .with_env("JWT_SECRET", "UP 4888, nice 4-8-4 steam engine")
        .with_env("SIPI_USE_LOCAL_DEV", "false")
        .with_env("ALLOW_ERASE_PROJECTS", "true")
        .with_env("DB_JDBC_URL", "jdbc:sqlite:/opt/db/ingest.sqlite")
        .with_volume_mapping(artifact_dirs.sipi_images, "/opt/images", "rw")
        .with_volume_mapping(artifact_dirs.tmp_ingest, "/opt/tmp", "rw")
        .with_volume_mapping(artifact_dirs.ingest_db, "/opt/db", "rw")
    )
    ingest.start()
    wait_for_logs(ingest, "Started dsp-ingest")
    print("Ingest is ready")
    return ingest


def _get_api(network: Network, version: str, ports: ExternalContainerPorts, names: ContainerNames) -> DockerContainer:
    api = (
        DockerContainer(f"daschswiss/knora-api:{version}")
        .with_name(names.api)
        .with_network(network)
        # other containers are addressed with http://<service_name>:<internal_port>
        .with_env("KNORA_WEBAPI_DSP_INGEST_BASE_URL", f"http://{names.ingest}:{INGEST_INTERNAL_PORT}")
        .with_env("KNORA_WEBAPI_JWT_ISSUER", f"http://{names.api}:{ports.api}")
        .with_env("KNORA_WEBAPI_KNORA_API_EXTERNAL_PORT", ports.api)
        .with_env("KNORA_WEBAPI_TRIPLESTORE_HOST", names.fuseki)
        .with_env("KNORA_WEBAPI_TRIPLESTORE_FUSEKI_REPOSITORY_NAME", "knora-test")
        .with_env("KNORA_WEBAPI_TRIPLESTORE_FUSEKI_USERNAME", "admin")
        .with_env("KNORA_WEBAPI_TRIPLESTORE_FUSEKI_PASSWORD", "test")
        .with_env("ALLOW_ERASE_PROJECTS", "true")
        .with_bind_ports(host=ports.api, container=API_INTERNAL_PORT)
    )
    api.start()
    wait_for_logs(api, "AppState set to Running")
    wait_for_logs(api, "Starting api on")
    print("API is ready")
    return api


def _print_containers_are_ready(containers: Containers) -> None:
    print("Containers are ready")
    print(f"  {containers.fuseki._name}: {containers.fuseki.ports}")
    print(f"  {containers.sipi._name}: {containers.sipi.ports}")
    print(f"  {containers.ingest._name}: {containers.ingest.ports}")
    print(f"  {containers.api._name}: {containers.api.ports}")
