from pathlib import Path

import pytest
import requests
from rdflib import RDFS
from rdflib import Graph
from rdflib import URIRef

from dsp_tools.cli.args import ServerCredentials
from dsp_tools.clients.exceptions import ProjectNotFoundError
from dsp_tools.commands.create.create import create
from dsp_tools.commands.mapping.config_file import parse_mapping_config
from dsp_tools.commands.mapping.exceptions import OntologyReferencedNotFoundError
from dsp_tools.commands.mapping.mapping_add import mapping_add
from dsp_tools.commands.mapping.models import MappingInfo
from dsp_tools.utils.data_formats.iri_util import make_dsp_ontology_prefix
from dsp_tools.utils.exceptions import DspToolsRequestException

SHORTCODE = "4124"
ONTO_NAME = "testonto"

KNORA_RESOURCE = "http://api.knora.org/ontology/knora-api/v2#Resource"
KNORA_HAS_VALUE = "http://api.knora.org/ontology/knora-api/v2#hasValue"


@pytest.fixture(scope="module")
def ontology_namespace(creds: ServerCredentials) -> str:
    return make_dsp_ontology_prefix(creds.server, SHORTCODE, ONTO_NAME)


@pytest.fixture(scope="module")
def create_minimal_project(creds: ServerCredentials) -> None:
    assert create(Path("testdata/json-project/minimal-project-4124.json"), creds, True)


def _adjust_api_url_to_test_container(config_info: MappingInfo, creds: ServerCredentials) -> MappingInfo:
    """
    The config info yaml has the default localhost API URL.
    However, the test containers create different API URLs on the fly to avoid conflict.
    The actual URL is stored in the creds and corrected here.
    """
    corrected_server = ServerCredentials(
        user=config_info.server.user,
        password=config_info.server.password,
        server=creds.server,
    )
    config_info.server = corrected_server
    return config_info


def _get_ontology_graph(ontology_namespace: str) -> Graph:
    url = ontology_namespace.rstrip("#")
    response = requests.get(url, headers={"Accept": "text/turtle"}, timeout=5)
    if not response.ok:
        raise DspToolsRequestException(
            f"Non-ok response when requesting the ontology from the server.\n"
            f"Code: {response.status_code} Text: {response.text}"
        )
    onto_g = Graph()
    onto_g.parse(data=response.text, format="ttl")
    return onto_g


def _get_super_entities(onto_g: Graph, entity_iri: str, predicate: URIRef) -> set[URIRef]:
    # Cardinality restrictions are also in the results, they are of type blank node and can be filtered out.
    return {x for x in onto_g.objects(URIRef(entity_iri), predicate) if isinstance(x, URIRef)}


@pytest.mark.usefixtures("create_minimal_project")
@pytest.mark.run("first")
def test_add_mapping_good(creds: ServerCredentials):
    config_file = Path("testdata/mapping/4124-testonto-mapping-good.yaml")
    config_info = parse_mapping_config(config_file)
    config_info = _adjust_api_url_to_test_container(config_info, creds)
    success = mapping_add(config_info)
    assert success


@pytest.mark.usefixtures("create_minimal_project")
def test_check_successful_mapping_result(ontology_namespace):
    onto_g = _get_ontology_graph(ontology_namespace)

    expected_sub_props = {
        URIRef("https://www.dublincore.org/specifications/dublin-core/dcmi-terms/title"),
        URIRef(KNORA_HAS_VALUE),
    }
    assert _get_super_entities(onto_g, f"{ontology_namespace}hasText", RDFS.subPropertyOf) == expected_sub_props

    expected_sub_cls = {
        URIRef("http://www.cidoc-crm.org/cidoc-crm/E22_Human-Made_Object"),
        URIRef("https://www.w3.org/TR/rdf-schema/Book"),
        URIRef("http://purl.org/ontology/bibo/Book"),
        URIRef(KNORA_RESOURCE),
    }
    assert _get_super_entities(onto_g, f"{ontology_namespace}minimalResource", RDFS.subClassOf) == expected_sub_cls


@pytest.mark.usefixtures("create_minimal_project")
def test_add_mapping_inexistent_onto(creds: ServerCredentials):
    config_file = Path("testdata/mapping/4124-testonto-mapping-inexistent-onto.yaml")
    config_info = parse_mapping_config(config_file)
    config_info = _adjust_api_url_to_test_container(config_info, creds)
    with pytest.raises(OntologyReferencedNotFoundError):
        mapping_add(config_info)


@pytest.mark.usefixtures("create_minimal_project")
def test_add_mapping_inexistent_project(creds: ServerCredentials):
    config_file = Path("testdata/mapping/F000-testonto-mapping-project-not-exist.yaml")
    config_info = parse_mapping_config(config_file)
    config_info = _adjust_api_url_to_test_container(config_info, creds)
    with pytest.raises(ProjectNotFoundError):
        mapping_add(config_info)


@pytest.mark.usefixtures("create_minimal_project")
def test_add_mapping_inexistent_references(creds: ServerCredentials):
    config_file = Path("testdata/mapping/4124-testonto-mapping-inexistent-references.yaml")
    config_info = parse_mapping_config(config_file)
    config_info = _adjust_api_url_to_test_container(config_info, creds)
    success = mapping_add(config_info)
    assert not success


@pytest.mark.usefixtures("create_minimal_project")
def test_add_mapping_missing_prefix(creds: ServerCredentials):
    config_file = Path("testdata/mapping/4124-testonto-mapping-missing-prefix.yaml")
    config_info = parse_mapping_config(config_file)
    config_info = _adjust_api_url_to_test_container(config_info, creds)
    success = mapping_add(config_info)
    assert not success


@pytest.mark.usefixtures("create_minimal_project")
def test_replace_mapping_with_different_excel(creds: ServerCredentials):
    # This test establishes its own pre-state instead of inheriting it from the tests above. The Excel files of
    # the earlier tests do not list `otherResource` and `hasOtherText`, so under replace semantics those two are
    # already stripped by the time this test runs, and the assertions of the next test would prove nothing.
    good_config = parse_mapping_config(Path("testdata/mapping/4124-testonto-mapping-good.yaml"))
    assert mapping_add(_adjust_api_url_to_test_container(good_config, creds))

    replace_config = parse_mapping_config(Path("testdata/mapping/4124-testonto-mapping-replace.yaml"))
    assert mapping_add(_adjust_api_url_to_test_container(replace_config, creds))


@pytest.mark.usefixtures("create_minimal_project")
def test_check_replaced_mapping_result(ontology_namespace):
    onto_g = _get_ontology_graph(ontology_namespace)

    # `bibo:Book` is listed in both Excel files and must survive, `cidoc:E22` and `schema:Book` must be gone,
    # and the knora-api super-class must never be touched.
    expected_sub_cls = {
        URIRef("http://iflastandards.info/ns/fr/frbr/frbroo/F1_Work"),
        URIRef("http://purl.org/ontology/bibo/Book"),
        URIRef(KNORA_RESOURCE),
    }
    assert _get_super_entities(onto_g, f"{ontology_namespace}minimalResource", RDFS.subClassOf) == expected_sub_cls

    expected_sub_props = {
        URIRef("https://www.dublincore.org/specifications/dublin-core/dcmi-terms/description"),
        URIRef(KNORA_HAS_VALUE),
    }
    assert _get_super_entities(onto_g, f"{ontology_namespace}hasText", RDFS.subPropertyOf) == expected_sub_props

    # `otherResource` and `hasOtherText` are absent from the replace Excel, so their external mappings are gone
    # although the Excel never mentions them. This is what proves the wipe covers the whole ontology.
    assert _get_super_entities(onto_g, f"{ontology_namespace}otherResource", RDFS.subClassOf) == {
        URIRef(KNORA_RESOURCE)
    }
    assert _get_super_entities(onto_g, f"{ontology_namespace}hasOtherText", RDFS.subPropertyOf) == {
        URIRef(KNORA_HAS_VALUE)
    }
