from pathlib import Path

import pytest
import requests
from rdflib import Graph

from dsp_tools.cli.args import ServerCredentials
from dsp_tools.commands.create.create import create
from dsp_tools.commands.mapping.config_file import parse_mapping_config
from dsp_tools.commands.mapping.mapping_add import mapping_add
from dsp_tools.utils.data_formats.iri_util import make_dsp_ontology_prefix
from dsp_tools.utils.exceptions import DspToolsRequestException

SHORTCODE = "4124"
ONTO_NAME = "minimal-tp"
CLASS_LOCAL_NAME = "minimalResource"
PROP_LOCAL_NAME = "hasText"

TESTDATA = Path("testdata/mapping")


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
    url = f"{ontology_namespace.rstrip('#')}{ONTO_NAME}"
    response = requests.get(url, headers={"Accept": "text/turtle"}, timeout=5)
    if not response.ok:
        raise DspToolsRequestException("Non-ok response when requesting the ontology from the server.")
    onto_g = Graph()
    onto_g.parse(data=response.text, format="ttl")


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
