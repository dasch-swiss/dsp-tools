from pathlib import Path

import pytest
import requests
from rdflib import RDFS
from rdflib import Graph
from rdflib import URIRef

from dsp_tools.cli.args import ServerCredentials
from dsp_tools.commands.create.create import create
from dsp_tools.commands.mapping.config_file import parse_mapping_config
from dsp_tools.commands.mapping.mapping_add import mapping_add
from dsp_tools.utils.data_formats.iri_util import make_dsp_ontology_prefix
from dsp_tools.utils.exceptions import DspToolsRequestException

SHORTCODE = "4124"
ONTO_NAME = "testonto"


@pytest.fixture(scope="module")
def ontology_namespace(creds: ServerCredentials) -> str:
    return make_dsp_ontology_prefix(creds.server, SHORTCODE, ONTO_NAME)


@pytest.fixture(scope="module")
def create_minimal_project(creds: ServerCredentials) -> None:
    assert create(Path("testdata/json-project/minimal-project-4124.json"), creds, True)


@pytest.mark.usefixtures("create_minimal_project")
def test_add_mapping_good():
    config_file = Path("testdata/mapping/4124-testonto-mapping-good.yaml")
    config_info = parse_mapping_config(config_file)
    success = mapping_add(config_info)
    assert success


@pytest.mark.usefixtures("test_add_mapping_good")
def test_check_successful_mapping_result(ontology_namespace):
    url = ontology_namespace.rstrip("#")
    response = requests.get(url, headers={"Accept": "text/turtle"}, timeout=5)
    if not response.ok:
        raise DspToolsRequestException(
            f"Non-ok response when requesting the ontology from the server.\n"
            f"Code: {response.status_code} Text: {response.text}"
        )
    onto_g = Graph()
    onto_g.parse(data=response.text, format="ttl")

    prop_iri = URIRef(f"{ontology_namespace}hasText")
    expected_sub_props = {
        URIRef("https://www.dublincore.org/specifications/dublin-core/dcmi-terms/title"),
        URIRef("http://api.knora.org/ontology/knora-api/v2#hasValue"),
    }
    result_sub_props = set(onto_g.objects(prop_iri, RDFS.subPropertyOf))
    assert result_sub_props == expected_sub_props

    cls_iri = URIRef(f"{ontology_namespace}minimalResource")
    expected_sub_cls = {
        URIRef("http://www.cidoc-crm.org/cidoc-crm/E22_Human-Made_Object"),
        URIRef("https://www.w3.org/TR/rdf-schema/Book"),
        URIRef("http://purl.org/ontology/bibo/Book"),
        URIRef("http://api.knora.org/ontology/knora-api/v2#Resource"),
    }
    result_sub_cls = set(onto_g.objects(cls_iri, RDFS.subClassOf))
    # cardinality restrictions are also in the results, they are of type blank node and can be filtered out
    result_sub_cls_without_bnodes = {x for x in result_sub_cls if isinstance(x, URIRef)}
    assert result_sub_cls_without_bnodes == expected_sub_cls


@pytest.mark.usefixtures("create_minimal_project")
def test_add_mapping_inexistent_onto():
    config_file = Path("testdata/mapping/4124-testonto-mapping-inexistent-onto.yaml")
    config_info = parse_mapping_config(config_file)
    success = mapping_add(config_info)
    assert not success


@pytest.mark.usefixtures("create_minimal_project")
def test_add_mapping_inexistent_references():
    config_file = Path("testdata/mapping/4124-testonto-mapping-inexistent-references.yaml")
    config_info = parse_mapping_config(config_file)
    success = mapping_add(config_info)
    assert not success


@pytest.mark.usefixtures("create_minimal_project")
def test_add_mapping_missing_prefix():
    config_file = Path("testdata/mapping/4124-testonto-mapping-missing-prefix.yaml")
    config_info = parse_mapping_config(config_file)
    success = mapping_add(config_info)
    assert not success
