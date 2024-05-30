from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator

import requests
from docker.errors import DockerException
from testcontainers.core.container import DockerContainer
from testcontainers.core.network import Network
from testcontainers.core.waiting_utils import wait_for_logs

# copied and adapted from dsp-api/webapi/scripts/fuseki-repository-config.ttl.template
_repo_config: str = """
@prefix :           <http://base/#> .
@prefix fuseki:     <http://jena.apache.org/fuseki#> .
@prefix ja:         <http://jena.hpl.hp.com/2005/11/Assembler#> .
@prefix tdb2:       <http://jena.apache.org/2016/tdb#> .
@prefix rdf:        <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs:       <http://www.w3.org/2000/01/rdf-schema#> .
@prefix text:       <http://jena.apache.org/text#> .
@prefix knora-base: <http://www.knora.org/ontology/knora-base#> .

[] rdf:type        fuseki:Server ;
   fuseki:services :service_tdb_all ;
   ja:loadClass    "org.apache.jena.query.text.TextQuery" .

:service_tdb_all a fuseki:Service ;
                 rdfs:label                        "TDB2 knora-test" ;
                 fuseki:dataset                    :text_dataset ;
                 fuseki:name                       "knora-test" ;
                 fuseki:serviceQuery               "query" , "sparql" ;
                 fuseki:serviceReadGraphStore      "get" ;
                 fuseki:serviceReadWriteGraphStore "data" ;
                 fuseki:serviceUpdate              "update" ;
                 fuseki:serviceUpload              "upload" .

:text_dataset rdf:type     text:TextDataset ;
            text:dataset :tdb_dataset_readwrite ;
            text:index   :indexLucene .

:tdb_dataset_readwrite  a                                   tdb2:DatasetTDB2 ;
                        tdb2:unionDefaultGraph              true ;
                        tdb2:location                       "/fuseki/databases/knora-test" .

:indexLucene a text:TextIndexLucene ;
            text:directory "/fuseki/lucene/knora-test" ;
            text:entityMap :entMap ;
            text:analyzer  [ a text:ConfigurableAnalyzer ;
                              text:tokenizer text:WhitespaceTokenizer ;
                              text:filters ( text:ASCIIFoldingFilter text:LowerCaseFilter)
                           ] .

:entMap a                 text:EntityMap ;
        text:entityField  "uri" ;
        text:defaultField "text" ;
        text:uidField     "uid" ;
        text:map          (
                              [ text:field  "text" ;  text:predicate  rdfs:label ]
                              [ text:field  "text" ;  text:predicate  knora-base:valueHasString ]
                              [ text:field  "text" ;  text:predicate  knora-base:valueHasComment ]
                          ) .
"""

# copied and adapted from dsp-api/test_data/project_data/admin-data-minimal.ttl
_admin_user_data: str = """
@prefix xsd:         <http://www.w3.org/2001/XMLSchema#> .
@prefix rdf:         <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix knora-admin: <http://www.knora.org/ontology/knora-admin#> .

<http://rdfh.ch/users/root> a knora-admin:User ;
    knora-admin:username             "root"^^xsd:string ;
    knora-admin:email                "root@example.com"^^xsd:string ;
    knora-admin:givenName            "System"^^xsd:string ;
    knora-admin:familyName           "Administrator"^^xsd:string ;
    knora-admin:password             "$2a$12$7XEBehimXN1rbhmVgQsyve08.vtDmKK7VMin4AdgCEtE4DWgfQbTK"^^xsd:string ;
    knora-admin:phone                "123456"^^xsd:string ;
    knora-admin:preferredLanguage    "en"^^xsd:string ;
    knora-admin:status               "true"^^xsd:boolean ;
    knora-admin:isInSystemAdminGroup "true"^^xsd:boolean .
"""


SIPI_PATH = Path("testdata/e2e/sipi").absolute()
SIPI_PATH_IMAGES = SIPI_PATH / "images"


@dataclass
class Containers:
    sipi: DockerContainer
    fuseki: DockerContainer
    api: DockerContainer
    ingest: DockerContainer


@contextmanager
def get_containers() -> Iterator[Containers]:
    try:
        network = Network()
    except DockerException:
        raise RuntimeError("Cannot create network, probably because Docker is not running properly")
    network.__enter__()
    fuseki = _get_fuseki_container(network)
    fuseki.start()
    wait_for_logs(fuseki, r"Server .+ Started .+ on port \d+$")
    print("Fuseki is ready")
    if not requests.post(
        "http://0.0.0.0:3030/$/datasets",
        files={"file": ("file.ttl", _repo_config, "text/turtle; charset=utf8")},
        auth=("admin", "test"),
        timeout=30,
    ).ok:
        raise RuntimeError("Fuseki did not create the dataset")
    print("Dataset created")
    graph_prefix = "http://0.0.0.0:3030/knora-test/data?graph="
    admin_graph = "http://www.knora.org/data/admin"
    if not requests.post(
        graph_prefix + admin_graph,
        files={"file": ("file.ttl", _admin_user_data, "text/turtle; charset: utf-8")},
        auth=("admin", "test"),
        timeout=30,
    ).ok:
        raise RuntimeError("Fuseki did not create the admin user")
    print("Admin user created")
    sipi = _get_sipi_container(network)
    sipi.start()
    ingest = _get_ingestion_container(network)
    ingest.start()
    wait_for_logs(sipi, "Sipi: Server listening on HTTP port 1024")
    print("Sipi is ready")
    wait_for_logs(ingest, "Started dsp-ingest")
    print("Ingest is ready")
    api = _get_api_container(network)
    api.start()
    wait_for_logs(api, "AppState set to Running")
    wait_for_logs(api, "Starting api on")
    print("API is ready")
    print("Containers are ready")
    print(f"  {api._name}: {api.ports}")
    print(f"  {fuseki._name}: {fuseki.ports}")
    print(f"  {sipi._name}: {sipi.ports}")
    print(f"  {ingest._name}: {ingest.ports}")
    yield Containers(sipi, fuseki, api, ingest)
    print("Closing all containers")
    api.stop()
    ingest.stop()
    sipi.stop()
    fuseki.stop()
    network.remove()


def _get_sipi_container(network: Network) -> DockerContainer:
    return (
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
        .with_volume_mapping(SIPI_PATH / "tmp", "/tmp", "rw")  # noqa: S108
        .with_volume_mapping(SIPI_PATH / "config", "/sipi/config", "rw")
        .with_volume_mapping(SIPI_PATH_IMAGES, "/sipi/images", "rw")
    )


def _get_fuseki_container(network: Network) -> DockerContainer:
    return (
        DockerContainer("daschswiss/apache-jena-fuseki:5.0.0-3")
        .with_name("db")
        .with_network(network)
        .with_bind_ports(3030, 3030)
        .with_env("ADMIN_PASSWORD", "test")
    )


def _get_api_container(network: Network) -> DockerContainer:
    return (
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


def _get_ingestion_container(network: Network) -> DockerContainer:
    return (
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
        .with_volume_mapping(SIPI_PATH / "tmp-dsp-ingest", "/opt/temp", "rw")
    )


def main() -> None:
    with get_containers() as containers:
        print("Containers are ready")
        print(f"  {containers.api._name}: {containers.api.ports}")
        print(f"  {containers.fuseki._name}: {containers.fuseki.ports}")
        print(f"  {containers.sipi._name}: {containers.sipi.ports}")
        print(f"  {containers.ingest._name}: {containers.ingest.ports}")


if __name__ == "__main__":
    main()
