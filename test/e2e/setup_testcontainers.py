import subprocess
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import ClassVar
from typing import Iterator

import docker
import regex
import requests
from docker.errors import NotFound
from docker.models.networks import Network
from testcontainers.core.container import DockerContainer
from testcontainers.core.waiting_utils import wait_for_logs

E2E_TESTDATA = Path("testdata/e2e").absolute()
SIPI_IMAGES = E2E_TESTDATA / "images"
TMP_SIPI = E2E_TESTDATA / "tmp-dsp-sipi"
TMP_INGEST = E2E_TESTDATA / "tmp-dsp-ingest"
INGEST_DB = E2E_TESTDATA / "ingest-db"

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


def _get_image_versions() -> ImageVersions:
    docker_compose_content = Path("src/dsp_tools/resources/start-stack/docker-compose.yml").read_text(encoding="utf-8")
    fuseki = _get_image_version(docker_compose_content, "apache-jena-fuseki")
    sipi = _get_image_version(docker_compose_content, "knora-sipi")
    ingest = _get_image_version(docker_compose_content, "dsp-ingest")
    api = _get_image_version(docker_compose_content, "knora-api")
    return ImageVersions(fuseki=fuseki, sipi=sipi, ingest=ingest, api=api)


class TestContainerFactory:
    __counter: ClassVar[int] = 0
    versions: ClassVar[ImageVersions] = _get_image_versions()

    def __init__(self) -> None:
        raise TypeError

    @classmethod
    @contextmanager
    def get_containers(cls) -> Iterator[Containers]:
        if subprocess.run("docker stats --no-stream".split(), check=False).returncode != 0:
            raise RuntimeError("Docker is not running properly")
        cls.__counter += 1
        with get_test_network(cls.__counter) as network:
            containers = _get_all_containers(network, cls.versions, cls.__counter)
            try:
                yield containers
            finally:
                _stop_all_containers(containers)


@contextmanager
def get_test_network(counter: int) -> Iterator[Network]:
    name = f"dsp-tools-test-network-{counter}"
    client = docker.client.from_env()
    try:
        network = client.networks.get(name)
    except NotFound:
        client.networks.create(name, internal=True, check_duplicate=True)
        network = client.networks.get(name)
    try:
        yield network
    finally:
        network.remove()
        client.close()  # type: ignore[no-untyped-call]  # incomplete stubs - remove this when the stubs are complete


def _get_all_containers(network: Network, versions: ImageVersions, counter: int) -> Containers:
    fuseki = _get_fuseki_container(network, versions.fuseki, counter)
    sipi = _get_sipi_container(network, versions.sipi, counter)
    ingest = _get_ingest_container(network, versions.ingest, counter)
    api = _get_api_container(network, versions.api, counter)
    containers = Containers(fuseki=fuseki, sipi=sipi, ingest=ingest, api=api)
    _print_containers_are_ready(containers)
    return containers


def _get_image_version(docker_compose_content: str, component: str) -> str:
    match = regex.search(rf"image: daschswiss/{component}:([^\n]+)", docker_compose_content)
    return match.group(1) if match else "latest"


def _get_fuseki_container(network: Network, version: str, counter: int) -> DockerContainer:
    fuseki_external_port = FUSEKI_INTERNAL_PORT + counter
    fuseki = (
        DockerContainer(f"daschswiss/apache-jena-fuseki:{version}")
        .with_name("db")
        .with_network(network)
        .with_bind_ports(host=fuseki_external_port, container=FUSEKI_INTERNAL_PORT)
        .with_env("ADMIN_PASSWORD", "test")
    )
    fuseki.start()
    wait_for_logs(fuseki, r"Server .+ Started .+ on port \d+$")
    print("Fuseki is ready")
    _create_data_set_and_admin_user(fuseki_external_port)
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


def _get_sipi_container(network: Network, version: str, counter: int) -> DockerContainer:
    sipi_external_port = SIPI_INTERNAL_PORT + counter
    api_external_port = API_INTERNAL_PORT + counter
    sipi = (
        DockerContainer(f"daschswiss/knora-sipi:{version}")
        .with_name("sipi")
        .with_network(network)
        .with_bind_ports(host=sipi_external_port, container=SIPI_INTERNAL_PORT)
        .with_env("KNORA_WEBAPI_KNORA_API_EXTERNAL_HOST", "0.0.0.0")  # noqa: S104
        .with_env("KNORA_WEBAPI_KNORA_API_EXTERNAL_PORT", api_external_port)
        .with_command("--config=/sipi/config/sipi.docker-config.lua")
        .with_volume_mapping(TMP_SIPI, "/tmp", "rw")  # noqa: S108
        .with_volume_mapping(E2E_TESTDATA, "/sipi/config", "rw")
        .with_volume_mapping(SIPI_IMAGES, "/sipi/images", "rw")
    )
    sipi.start()
    wait_for_logs(sipi, f"Sipi: Server listening on HTTP port {sipi_external_port}")
    print("Sipi is ready")
    return sipi


def _get_ingest_container(network: Network, version: str, counter: int) -> DockerContainer:
    ingest_external_port = INGEST_INTERNAL_PORT + counter
    api_external_port = API_INTERNAL_PORT + counter
    ingest = (
        DockerContainer(f"daschswiss/dsp-ingest:{version}")
        .with_name("ingest")
        .with_network(network)
        .with_bind_ports(host=ingest_external_port, container=INGEST_INTERNAL_PORT)
        .with_env("STORAGE_ASSET_DIR", "/opt/images")
        .with_env("STORAGE_TEMP_DIR", "/opt/temp")
        .with_env("JWT_AUDIENCE", f"http://ingest:{ingest_external_port}")
        .with_env("JWT_ISSUER", f"http://api:{api_external_port}")
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


def _get_api_container(network: Network, version: str, counter: int) -> DockerContainer:
    api_external_port = API_INTERNAL_PORT + counter
    ingest_external_port = INGEST_INTERNAL_PORT + counter
    api = (
        DockerContainer(f"daschswiss/knora-api:{version}")
        .with_name("api")
        .with_network(network)
        # other containers are addressed by their service name and their **internal** port
        .with_env("KNORA_WEBAPI_DSP_INGEST_BASE_URL", f"http://ingest:{INGEST_INTERNAL_PORT}")
        .with_env("KNORA_WEBAPI_DSP_INGEST_AUDIENCE", f"http://ingest:{ingest_external_port}")
        .with_env("KNORA_WEBAPI_JWT_ISSUER", f"http://api:{api_external_port}")
        .with_env("KNORA_WEBAPI_KNORA_API_EXTERNAL_PORT", api_external_port)
        .with_env("KNORA_WEBAPI_TRIPLESTORE_HOST", "db")
        .with_env("KNORA_WEBAPI_TRIPLESTORE_FUSEKI_REPOSITORY_NAME", "knora-test")
        .with_env("KNORA_WEBAPI_TRIPLESTORE_FUSEKI_USERNAME", "admin")
        .with_env("KNORA_WEBAPI_TRIPLESTORE_FUSEKI_PASSWORD", "test")
        .with_env("ALLOW_ERASE_PROJECTS", "true")
        .with_bind_ports(host=api_external_port, container=API_INTERNAL_PORT)
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
