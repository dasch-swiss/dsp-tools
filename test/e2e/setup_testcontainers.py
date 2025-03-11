import socket
import subprocess
from contextlib import contextmanager
from dataclasses import dataclass
from itertools import count
from pathlib import Path
from typing import Iterator
from uuid import uuid4

import regex
import requests
from testcontainers.core.container import DockerContainer
from testcontainers.core.network import Network
from testcontainers.core.waiting_utils import wait_for_logs

E2E_TESTDATA = Path("testdata/e2e").absolute()
SIPI_IMAGES = E2E_TESTDATA / "images"
TMP_SIPI = E2E_TESTDATA / "tmp-dsp-sipi"
TMP_INGEST = E2E_TESTDATA / "tmp-dsp-ingest"
INGEST_DB = E2E_TESTDATA / "ingest-db"

TESTCONTAINER_PORTS_LOCKFILES = Path("test/e2e/testcontainer_port_lockfiles")
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

    fuseki_port: int
    sipi_port: int
    ingest_port: int
    api_port: int


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


@contextmanager
def get_containers() -> Iterator[ContainerPorts]:
    if subprocess.run("docker stats --no-stream".split(), check=False).returncode != 0:
        raise RuntimeError("Docker is not running properly")
    with Network() as network:
        ports = _get_ports()
        prefix = f"testcontainer-{str(uuid4())[:6]}"
        names = ContainerNames(f"{prefix}-db", f"{prefix}-sipi", f"{prefix}-ingest", f"{prefix}-api")
        containers = _get_all_containers(network, ports, names)
        try:
            yield ports
        finally:
            _stop_all_containers(containers)
            _release_ports(ports)


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
    (TESTCONTAINER_PORTS_LOCKFILES / str(ports.fuseki_port)).unlink()
    (TESTCONTAINER_PORTS_LOCKFILES / str(ports.sipi_port)).unlink()
    (TESTCONTAINER_PORTS_LOCKFILES / str(ports.ingest_port)).unlink()
    (TESTCONTAINER_PORTS_LOCKFILES / str(ports.api_port)).unlink()


def _get_all_containers(network: Network, ports: ContainerPorts, names: ContainerNames) -> Containers:
    versions = _get_image_versions()
    fuseki = _get_fuseki_container(network, versions.fuseki, ports, names)
    sipi = _get_sipi_container(network, versions.sipi, ports, names)
    ingest = _get_ingest_container(network, versions.ingest, ports, names)
    api = _get_api_container(network, versions.api, ports, names)
    containers = Containers(fuseki=fuseki, sipi=sipi, ingest=ingest, api=api)
    _print_containers_are_ready(containers)
    return containers


def _get_fuseki_container(
    network: Network, version: str, ports: ContainerPorts, names: ContainerNames
) -> DockerContainer:
    fuseki = (
        DockerContainer(f"daschswiss/apache-jena-fuseki:{version}")
        .with_name(names.fuseki)
        .with_network(network)
        .with_bind_ports(host=ports.fuseki_port, container=FUSEKI_INTERNAL_PORT)
        .with_env("ADMIN_PASSWORD", "test")
    )
    fuseki.start()
    wait_for_logs(fuseki, f"Server .+ Started .+ on port {FUSEKI_INTERNAL_PORT}")
    print("Fuseki is ready")
    _create_data_set_and_admin_user(ports.fuseki_port)
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


def _get_sipi_container(
    network: Network, version: str, ports: ContainerPorts, names: ContainerNames
) -> DockerContainer:
    sipi = (
        DockerContainer(f"daschswiss/knora-sipi:{version}")
        .with_name(names.sipi)
        .with_network(network)
        .with_bind_ports(host=ports.sipi_port, container=SIPI_INTERNAL_PORT)
        .with_env("KNORA_WEBAPI_KNORA_API_EXTERNAL_HOST", "0.0.0.0")  # noqa: S104
        .with_env("KNORA_WEBAPI_KNORA_API_EXTERNAL_PORT", ports.api_port)
        .with_command("--config=/sipi/config/sipi.docker-config.lua")
        .with_volume_mapping(TMP_SIPI, "/tmp", "rw")  # noqa: S108
        .with_volume_mapping(E2E_TESTDATA, "/sipi/config", "rw")
        .with_volume_mapping(SIPI_IMAGES, "/sipi/images", "rw")
    )
    sipi.start()
    wait_for_logs(sipi, f"Sipi: Server listening on HTTP port {SIPI_INTERNAL_PORT}")
    print("Sipi is ready")
    return sipi


def _get_ingest_container(
    network: Network, version: str, ports: ContainerPorts, names: ContainerNames
) -> DockerContainer:
    ingest = (
        DockerContainer(f"daschswiss/dsp-ingest:{version}")
        .with_name(names.ingest)
        .with_network(network)
        .with_bind_ports(host=ports.ingest_port, container=INGEST_INTERNAL_PORT)
        .with_env("STORAGE_ASSET_DIR", "/opt/images")
        .with_env("STORAGE_TEMP_DIR", "/opt/temp")
        .with_env("JWT_ISSUER", f"http://{names.api}:{ports.api_port}")
        .with_env("JWT_SECRET", "UP 4888, nice 4-8-4 steam engine")
        .with_env("SIPI_USE_LOCAL_DEV", "false")
        .with_env("ALLOW_ERASE_PROJECTS", "true")
        .with_env("DB_JDBC_URL", "jdbc:sqlite:/opt/db/ingest.sqlite")
        .with_volume_mapping(SIPI_IMAGES, "/opt/images", "rw")
        .with_volume_mapping(TMP_INGEST, "/opt/temp", "rw")
        .with_volume_mapping(INGEST_DB, "/opt/db", "rw")
    )
    ingest.start()
    wait_for_logs(ingest, "Started dsp-ingest")
    print("Ingest is ready")
    return ingest


def _get_api_container(network: Network, version: str, ports: ContainerPorts, names: ContainerNames) -> DockerContainer:
    api = (
        DockerContainer(f"daschswiss/knora-api:{version}")
        .with_name(names.api)
        .with_network(network)
        # other containers are addressed by their service name and their **internal** port
        .with_env("KNORA_WEBAPI_DSP_INGEST_BASE_URL", f"http://{names.ingest}:{INGEST_INTERNAL_PORT}")
        .with_env("KNORA_WEBAPI_JWT_ISSUER", f"http://{names.api}:{ports.api_port}")
        .with_env("KNORA_WEBAPI_KNORA_API_EXTERNAL_PORT", ports.api_port)
        .with_env("KNORA_WEBAPI_TRIPLESTORE_HOST", names.fuseki)
        .with_env("KNORA_WEBAPI_TRIPLESTORE_FUSEKI_REPOSITORY_NAME", "knora-test")
        .with_env("KNORA_WEBAPI_TRIPLESTORE_FUSEKI_USERNAME", "admin")
        .with_env("KNORA_WEBAPI_TRIPLESTORE_FUSEKI_PASSWORD", "test")
        .with_env("ALLOW_ERASE_PROJECTS", "true")
        .with_bind_ports(host=ports.api_port, container=API_INTERNAL_PORT)
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


def _stop_all_containers(containers: Containers) -> None:
    containers.fuseki.stop()
    containers.sipi.stop()
    containers.ingest.stop()
    containers.api.stop()
    print("All containers have been stopped")
