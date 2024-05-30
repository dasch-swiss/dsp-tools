import subprocess
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator

import requests
from testcontainers.core.container import DockerContainer
from testcontainers.core.network import Network
from testcontainers.core.waiting_utils import wait_for_logs

SIPI_PATH = Path("testdata/e2e").absolute()
SIPI_PATH_IMAGES = SIPI_PATH / "images"
SIPI_PATH_TMP_SIPI = SIPI_PATH / "tmp-dsp-sipi"
SIPI_PATH_TMP_INGEST = SIPI_PATH / "tmp-dsp-ingest"


@dataclass(frozen=True)
class Containers:
    fuseki: DockerContainer
    sipi: DockerContainer
    ingest: DockerContainer
    api: DockerContainer


@contextmanager
def get_containers() -> Iterator[Containers]:
    if subprocess.run("docker stats --no-stream".split(), check=False).returncode != 0:
        raise RuntimeError("Docker is not running properly")
    with Network() as network:
        containers = _get_all_containers(network)
        try:
            yield containers
        finally:
            _stop_all_containers(containers)


def _get_all_containers(network: Network) -> Containers:
    fuseki = _get_fuseki_container(network)
    sipi = _get_sipi_container(network)
    ingest = _get_ingest_container(network)
    api = _get_api_container(network)
    containers = Containers(fuseki=fuseki, sipi=sipi, ingest=ingest, api=api)
    _print_containers_are_ready(containers)
    return containers


def _get_fuseki_container(network: Network) -> DockerContainer:
    fuseki = (
        DockerContainer("daschswiss/apache-jena-fuseki:5.0.0-3")
        .with_name("db")
        .with_network(network)
        .with_bind_ports(3030, 3030)
        .with_env("ADMIN_PASSWORD", "test")
    )
    fuseki.start()
    wait_for_logs(fuseki, r"Server .+ Started .+ on port \d+$")
    print("Fuseki is ready")
    _create_data_set_and_admin_user()
    return fuseki


def _create_data_set_and_admin_user() -> None:
    repo_config = Path("testdata/e2e/repo_config.ttl").read_text(encoding="utf-8")
    if not requests.post(
        "http://0.0.0.0:3030/$/datasets",
        files={"file": ("file.ttl", repo_config, "text/turtle; charset=utf8")},
        auth=("admin", "test"),
        timeout=30,
    ).ok:
        raise RuntimeError("Fuseki did not create the dataset")
    print("Dataset created")

    admin_user_data = Path("testdata/e2e/admin_user_data.ttl").read_text(encoding="utf-8")
    graph_prefix = "http://0.0.0.0:3030/knora-test/data?graph="
    admin_graph = "http://www.knora.org/data/admin"
    if not requests.post(
        graph_prefix + admin_graph,
        files={"file": ("file.ttl", admin_user_data, "text/turtle; charset: utf-8")},
        auth=("admin", "test"),
        timeout=30,
    ).ok:
        raise RuntimeError("Fuseki did not create the admin user")
    print("Admin user created")


def _get_sipi_container(network: Network) -> DockerContainer:
    sipi = (
        DockerContainer("daschswiss/knora-sipi:v30.14.0")
        .with_name("sipi")
        .with_network(network)
        .with_bind_ports(1024, 1024)
        .with_command("--config=/sipi/config/sipi.docker-config.lua")
        .with_env("SIPI_EXTERNAL_PROTOCOL", "http")
        .with_env("SIPI_EXTERNAL_HOSTNAME", "0.0.0.0")  # noqa: S104
        .with_env("SIPI_EXTERNAL_PORT", "1024")
        .with_env("SIPI_WEBAPI_HOSTNAME", "api")
        .with_env("SIPI_WEBAPI_PORT", "3333")
        .with_env("KNORA_WEBAPI_KNORA_API_EXTERNAL_HOST", "0.0.0.0")  # noqa: S104
        .with_env("KNORA_WEBAPI_KNORA_API_EXTERNAL_PORT", "3333")
        .with_volume_mapping(SIPI_PATH_TMP_SIPI, "/tmp", "rw")  # noqa: S108
        .with_volume_mapping(SIPI_PATH, "/sipi/config", "rw")
        .with_volume_mapping(SIPI_PATH_IMAGES, "/sipi/images", "rw")
    )
    sipi.start()
    wait_for_logs(sipi, "Sipi: Server listening on HTTP port 1024")
    print("Sipi is ready")
    return sipi


def _get_ingest_container(network: Network) -> DockerContainer:
    ingest = (
        DockerContainer("daschswiss/dsp-ingest:v0.9.1")
        .with_name("ingest")
        .with_network(network)
        .with_bind_ports(3340, 3340)
        .with_env("SERVICE_HOST", "0.0.0.0")  # noqa: S104
        .with_env("SERVICE_PORT", "3340")
        .with_env("SERVICE_LOG_FORMAT", "text")
        .with_env("STORAGE_ASSET_DIR", "/opt/images")
        .with_env("STORAGE_TEMP_DIR", "/opt/temp")
        .with_env("JWT_AUDIENCE", "http://localhost:3340")
        .with_env("JWT_ISSUER", "0.0.0.0:3333")
        .with_env("JWT_SECRET", "UP 4888, nice 4-8-4 steam engine")
        .with_env("SIPI_USE_LOCAL_DEV", "false")
        .with_volume_mapping(SIPI_PATH_IMAGES, "/opt/images", "rw")
        .with_volume_mapping(SIPI_PATH_TMP_INGEST, "/opt/temp", "rw")
    )
    ingest.start()
    wait_for_logs(ingest, "Started dsp-ingest")
    print("Ingest is ready")
    return ingest


def _get_api_container(network: Network) -> DockerContainer:
    api = (
        DockerContainer("daschswiss/knora-api:v30.14.0")
        .with_name("api")
        .with_network(network)
        .with_env("KNORA_WEBAPI_DSP_INGEST_BASE_URL", "http://ingest:3340")
        .with_env("KNORA_WEBAPI_TRIPLESTORE_HOST", "db")
        .with_env("KNORA_WEBAPI_TRIPLESTORE_DBTYPE", "fuseki")
        .with_env("KNORA_WEBAPI_SIPI_INTERNAL_HOST", "sipi")
        .with_env("KNORA_WEBAPI_TRIPLESTORE_FUSEKI_REPOSITORY_NAME", "knora-test")
        .with_env("KNORA_WEBAPI_TRIPLESTORE_FUSEKI_USERNAME", "admin")
        .with_env("KNORA_WEBAPI_TRIPLESTORE_FUSEKI_PASSWORD", "test")
        .with_env("KNORA_WEBAPI_CACHE_SERVICE_ENABLED", "true")
        .with_env("KNORA_WEBAPI_ALLOW_RELOAD_OVER_HTTP", "true")
        .with_env("KNORA_WEBAPI_KNORA_API_EXTERNAL_HOST", "0.0.0.0")  # noqa: S104
        .with_env("KNORA_WEBAPI_KNORA_API_EXTERNAL_PORT", "3333")
        .with_env("DSP_API_LOG_LEVEL", "INFO")
        .with_bind_ports(3333, 3333)
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


def main() -> None:
    with get_containers():
        pass


if __name__ == "__main__":
    main()
