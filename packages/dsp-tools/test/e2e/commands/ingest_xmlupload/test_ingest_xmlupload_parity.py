import json
import shutil
from collections.abc import Iterator
from pathlib import Path

import pytest
import requests
from rdflib import RDF
from rdflib import RDFS
from rdflib import BNode
from rdflib import Graph
from rdflib import Literal
from rdflib import URIRef
from rdflib.compare import graph_diff
from rdflib.compare import isomorphic
from rdflib.term import Node

from dsp_tools.cli.args import ServerCredentials
from dsp_tools.commands.create.create import create
from dsp_tools.commands.ingest_xmlupload.create_resources.upload_xml import ingest_xmlupload
from dsp_tools.commands.ingest_xmlupload.ingest_files.ingest_files import ingest_files
from dsp_tools.commands.ingest_xmlupload.upload_files.upload_files import upload_files
from dsp_tools.commands.xmlupload.xmlupload import xmlupload
from test.e2e.commands.ingest_xmlupload.utils import util_get_attached_to_user
from test.e2e.commands.ingest_xmlupload.utils import util_get_auth_header
from test.e2e.commands.ingest_xmlupload.utils import util_get_list_node_name
from test.e2e.commands.ingest_xmlupload.utils import util_get_user_iri
from test.e2e.commands.xmlupload.utils import util_request_resources_by_class
from test.e2e.setup_testcontainers.containers import ContainerMetadata
from test.e2e.setup_testcontainers.setup import get_containers

TEMPLATE_DIR = Path("testdata/dsp-ingest-data/parity")
IMAGE_DIR = Path("testdata/dsp-ingest-data/e2e-sample-project").absolute()
TEMPLATE_PROJECT = TEMPLATE_DIR / "parity-project-0013.json"
TEMPLATE_DATA = TEMPLATE_DIR / "parity-data-0013.xml"
ONTO_NAME = "parity-onto"
RESOURCE_CLASSES = ["ParityThing", "ParityImage"]
EXIT_IF_EXISTS = True

TEMPLATE_VALUES = {
    "shortcode": "0013",
    "shortname": "parity-a",
    "username": "parityMember",
    "email": "parity.member@test.org",
}
PROJECT_A = TEMPLATE_VALUES
PROJECT_B = {
    "shortcode": "0014",
    "shortname": "parity-b",
    "username": "parityMemberB",
    "email": "parity.member.b@test.org",
}

NORMALISED_ONTO_NS = "http://parity.test/onto#"
NORMALISED_RESOURCE_NS = "http://parity.test/resource/"
NORMALISED_LIST_NODE_NS = "http://parity.test/list-node/"

KB = "http://api.knora.org/ontology/knora-api/v2#"
# Each predicate legitimately differs between xmlupload and ingest-xmlupload, or between the two projects.
IGNORED_PREDICATES: dict[URIRef, str] = {
    URIRef(f"{KB}attachedToUser"): "the xmlupload user differs from the on-behalf-of user",
    URIRef(f"{KB}attachedToProject"): "the two projects have different IRIs",
    URIRef(f"{KB}userHasPermission"): "depends on the requesting user's relation to the owner",
    URIRef(f"{KB}creationDate"): "minted at import time",
    URIRef(f"{KB}lastModificationDate"): "set at import time",
    URIRef(f"{KB}valueCreationDate"): "minted at import time",
    URIRef(f"{KB}valueHasUUID"): "random UUID of the value",
    URIRef(f"{KB}arkUrl"): "contains the project shortcode and a resource UUID",
    URIRef(f"{KB}versionArkUrl"): "contains the project shortcode, a resource UUID and a timestamp",
    URIRef(f"{KB}valueAsString"): "is a copy of other value content, which is compared separately",
    URIRef(f"{KB}fileValueHasFilename"): "internal filename assigned by the ingest",
    URIRef(f"{KB}fileValueAsUrl"): "contains the internal filename",
    URIRef(f"{KB}stillImageFileValueHasIIIFBaseUrl"): "contains the project shortcode",
    URIRef(f"{KB}mayHaveMoreResults"): "paging marker of the response",
}


@pytest.fixture(scope="module")
def container_metadata() -> Iterator[ContainerMetadata]:
    with get_containers() as metadata:
        yield metadata


@pytest.fixture(scope="module")
def creds(container_metadata: ContainerMetadata) -> ServerCredentials:
    return ServerCredentials(
        "root@example.com",
        "test",
        f"http://0.0.0.0:{container_metadata.ports.api}",
        f"http://0.0.0.0:{container_metadata.ports.api}/ingest",
    )


@pytest.fixture
def home_folder(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("HOME", str(tmp_path))


def _write_project_copy(values: dict[str, str], folder: Path) -> tuple[Path, Path]:
    folder.mkdir()
    project_text = TEMPLATE_PROJECT.read_text(encoding="utf-8")
    data_text = TEMPLATE_DATA.read_text(encoding="utf-8")
    for key, template_value in TEMPLATE_VALUES.items():
        project_text = project_text.replace(template_value, values[key])
        data_text = data_text.replace(template_value, values[key])
    project_text = project_text.replace("../../../src", str(Path("src").absolute()))
    project_file = folder / f"parity-project-{values['shortcode']}.json"
    data_file = folder / f"parity-data-{values['shortcode']}.xml"
    project_file.write_text(project_text, encoding="utf-8")
    data_file.write_text(data_text, encoding="utf-8")
    return project_file, data_file


def _fetch_graph(shortcode: str, creds: ServerCredentials) -> Graph:
    auth_header = util_get_auth_header(creds)
    project_iri = requests.get(f"{creds.server}/admin/projects/shortcode/{shortcode}", timeout=10).json()["project"][
        "id"
    ]
    onto_ns = _onto_ns(shortcode, creds)
    graph = Graph()
    for cls in RESOURCE_CLASSES:
        graph += util_request_resources_by_class(f"{onto_ns}{cls}", auth_header, project_iri, creds)
    return graph


def _onto_ns(shortcode: str, creds: ServerCredentials) -> str:
    return f"{creds.server}/ontology/{shortcode}/{ONTO_NAME}/v2#"


def _list_node_names(graph: Graph, creds: ServerCredentials) -> dict[URIRef, URIRef]:
    nodes = {o for o in graph.objects(None, URIRef(f"{KB}listValueAsListNode")) if isinstance(o, URIRef)}
    return {node: URIRef(NORMALISED_LIST_NODE_NS + util_get_list_node_name(str(node), creds)) for node in nodes}


def _normalise(graph: Graph, shortcode: str, onto_ns: str, list_nodes: dict[URIRef, URIRef]) -> Graph:
    resource_iris = {
        s: URIRef(NORMALISED_RESOURCE_NS + str(label).replace(" ", "_"))
        for s, label in graph.subject_objects(RDFS.label)
        if isinstance(s, URIRef)
    }
    value_iri_prefix = f"http://rdfh.ch/{shortcode}/"
    bnodes: dict[URIRef, BNode] = {}

    def convert_iri(iri: URIRef) -> Node:
        if iri in resource_iris:
            return resource_iris[iri]
        if iri in list_nodes:
            return list_nodes[iri]
        if str(iri).startswith(value_iri_prefix):
            return bnodes.setdefault(iri, BNode())
        if str(iri).startswith(onto_ns):
            return URIRef(NORMALISED_ONTO_NS + str(iri).removeprefix(onto_ns))
        return iri

    def convert(term: Node) -> Node:
        if isinstance(term, URIRef):
            return convert_iri(term)
        if isinstance(term, Literal):
            text = str(term)
            for old, new in resource_iris.items():
                text = text.replace(str(old), str(new))
            return Literal(text, datatype=term.datatype, lang=term.language)
        return term

    normalised = Graph()
    for s, p, o in graph:
        if p in IGNORED_PREDICATES:
            continue
        normalised.add((convert(s), convert(p), convert(o)))
    return normalised


def _format_diff(graph_a: Graph, graph_b: Graph) -> str:
    _, in_a_only, in_b_only = graph_diff(graph_a, graph_b)
    only_a = "\n".join(sorted(str(t) for t in in_a_only))
    only_b = "\n".join(sorted(str(t) for t in in_b_only))
    return f"only in xmlupload:\n{only_a}\n\nonly in ingest-xmlupload:\n{only_b}"


def _run_ingest_chain(
    data_file: Path,
    shortcode: str,
    on_behalf_of_user: str,
    creds: ServerCredentials,
) -> dict[str, str]:
    assert upload_files(data_file, creds, data_file.parent)
    assert ingest_files(creds, shortcode)
    assert ingest_xmlupload(data_file, creds, on_behalf_of_user=on_behalf_of_user)
    id2iri_file = list(Path.cwd().glob(f"id2iri_{shortcode}_localhost*.json"))[-1]
    id2iri: dict[str, str] = json.loads(id2iri_file.read_text(encoding="utf-8"))
    return id2iri


@pytest.mark.usefixtures("home_folder")
def test_xmlupload_and_ingest_xmlupload_produce_the_same_data(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    creds: ServerCredentials,
) -> None:
    project_file_a, data_file_a = _write_project_copy(PROJECT_A, tmp_path / "a")
    project_file_b, data_file_b = _write_project_copy(PROJECT_B, tmp_path / "b")
    assert create(project_file_a, creds, EXIT_IF_EXISTS)
    assert create(project_file_b, creds, EXIT_IF_EXISTS)

    monkeypatch.chdir(tmp_path / "a")
    assert xmlupload(data_file_a, creds, str(IMAGE_DIR))

    shutil.copytree(IMAGE_DIR / "Bilder Projekt 2024", tmp_path / "b" / "Bilder Projekt 2024")
    monkeypatch.chdir(tmp_path / "b")
    id2iri_b = _run_ingest_chain(data_file_b, PROJECT_B["shortcode"], PROJECT_B["email"], creds)

    raw_a = _fetch_graph(PROJECT_A["shortcode"], creds)
    raw_b = _fetch_graph(PROJECT_B["shortcode"], creds)
    graph_a = _normalise(raw_a, PROJECT_A["shortcode"], _onto_ns("0013", creds), _list_node_names(raw_a, creds))
    graph_b = _normalise(raw_b, PROJECT_B["shortcode"], _onto_ns("0014", creds), _list_node_names(raw_b, creds))
    assert len(list(graph_a.subjects(RDF.type, URIRef(NORMALISED_ONTO_NS + "ParityThing")))) == 4
    assert list(graph_a.subjects(RDF.type, URIRef(NORMALISED_ONTO_NS + "ParityImage")))
    assert list(graph_a.triples((None, URIRef(NORMALISED_ONTO_NS + "hasText"), None)))
    assert list(graph_a.triples((None, URIRef(f"{KB}listValueAsListNode"), None)))
    assert list(graph_a.triples((None, URIRef(f"{KB}hasPermissions"), None)))
    assert isomorphic(graph_a, graph_b), _format_diff(graph_a, graph_b)

    member_iri = util_get_user_iri(PROJECT_B["email"], creds)
    assert all(util_get_attached_to_user(iri, creds) == member_iri for iri in id2iri_b.values())
